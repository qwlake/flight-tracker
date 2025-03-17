import time
import traceback
from datetime import timezone, timedelta, datetime

from dotenv import load_dotenv
import os

import request_util
from slack import send_slack_webhook
import random

load_dotenv()
timezone_KST = timezone(timedelta(hours=9))


class MessageContainer:

    def __init__(self, webhook_url, tz = None):
        self.webhook_url = webhook_url
        self.timezone = tz if tz is not None else timezone(timedelta(hours=9))
        self.previous_message: Message = Message(self.timezone)
        self.message: Message = Message(self.timezone)

    def rotate(self):
        self.previous_message = self.message
        self.message = Message(self.timezone)

    def append_text(self, text):
        self.message.text += text

    def send_message(self):
        if self.previous_message.text != self.message.text:
            if self.message.text != '':
                send_slack_webhook(self.webhook_url, '<!channel>\n' + self.message.get_print_text())
            else:
                send_slack_webhook(self.webhook_url, self.message.get_print_text())


class Message:

    def __init__(self, tz = None):
        self.text = ''
        self.timezone = tz if tz is not None else timezone(timedelta(hours=9))

    def get_print_text(self):
        current_time = datetime.now(self.timezone).strftime('%m-%d %H:%M')
        print_text = self.text if self.text != '' else '좌석이 마감되었습니다.'
        return f'{print_text}\n{current_time}'


def filter_time(schedules, departure_time, arrival_time):
    def is_valid_departure_time():
        if not departure_time or departure_time == '':
            return True
        return departure_time < schedule['departure_time']

    def is_valid_arrival_time():
        if not arrival_time or arrival_time == '':
            return True
        return schedule['arrival_time'] < arrival_time

    filtered_schedules = []
    for schedule in schedules:
        if is_valid_departure_time() and is_valid_arrival_time():
            filtered_schedules.append(schedule)
    return filtered_schedules


def get_current_time():
    return datetime.now(timezone_KST)


def get_current_time_str():
    return get_current_time().strftime('%Y-%m-%d %H:%M:%S')


def main():

    webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    message_container = MessageContainer(webhook_url)
    server_time_ticker = datetime.now()

    while True:
        server_name = os.getenv('SERVER_NAME')
        dates = os.getenv('FLIGHT_SCHEDULE_DATE').split(',')
        departure_time = os.getenv('FLIGHT_SCHEDULE_DEPARTURE_TIME')
        departure_location = os.getenv('FLIGHT_SCHEDULE_DEPARTURE_LOCATION')
        arrival_time = os.getenv('FLIGHT_SCHEDULE_ARRIVAL_TIME')
        arrival_location = os.getenv('FLIGHT_SCHEDULE_ARRIVAL_LOCATION')
        status_webhook_url = os.getenv('SLACK_STATUS_WEBHOOK_URL')

        current_time = get_current_time()
        if current_time.minute != server_time_ticker.minute:
            current_time_str = current_time.strftime('%Y-%m-%d %H:%M:%S')
            send_slack_webhook(status_webhook_url, f'{current_time_str} | {server_name} is running')
            server_time_ticker = current_time

        schedules_map = dict()
        try:
            for date in dates:
                schedules = request_util.get_flight_schedules(departure_location, arrival_location, date)
                schedules = filter_time(schedules, departure_time, arrival_time)
                if schedules:
                    schedules_map[date] = schedules

            for date, schedules in schedules_map.items():
                formated_date = datetime.strptime(date, '%Y%m%d').strftime('%m-%d')
                message_container.append_text("\n".join([
                    f"*Airline:* {schedule['airline_name']}\n*Dep:* {departure_location} {formated_date} {schedule['departure_time']} - *Arr:* {arrival_location} {formated_date} {schedule['arrival_time']}\n*Fee:* {schedule['fee']}\n"
                    for schedule in schedules
                ]))

            message_container.send_message()
            message_container.rotate()

        except Exception as e:
            send_slack_webhook(status_webhook_url, f'{get_current_time_str()} | {server_name} | Error fetching data: {e}\n{traceback.format_exc()}')

        random_number = random.randint(10, 15)
        time.sleep(random_number)


if __name__ == "__main__":
    main()
