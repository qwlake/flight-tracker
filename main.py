import time
import traceback
from datetime import timezone, timedelta, datetime

from dotenv import load_dotenv
import os
from crawler import get_flight_schedules
from slack import send_slack_webhook
import random

load_dotenv()
timezone_KST = timezone(timedelta(hours=9))


class Message:

    def __init__(self, tz = None):
        self.text = ''
        self.is_new = False
        self.timezone = tz if tz is not None else timezone(timedelta(hours=9))

    def get_print_text(self):
        current_time = datetime.now(self.timezone).strftime('%m-%d %H:%M')
        print_text = self.text
        if self.is_new:
            print_text = '<!channel>\n' + print_text
        return f'{current_time} | {print_text}'


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

def main():

    previous_message = Message(tz=timezone_KST)
    server_time_ticker = datetime.now()

    while True:
        server_name = os.getenv('SERVER_NAME')
        url = os.getenv('FLIGHT_SCHEDULE_URL')
        dates = os.getenv('FLIGHT_SCHEDULE_DATE').split(',')
        departure_time = os.getenv('FLIGHT_SCHEDULE_DEPARTURE_TIME')
        departure_location = os.getenv('FLIGHT_SCHEDULE_DEPARTURE_LOCATION')
        arrival_time = os.getenv('FLIGHT_SCHEDULE_ARRIVAL_TIME')
        arrival_location = os.getenv('FLIGHT_SCHEDULE_ARRIVAL_LOCATION')
        webhook_url = os.getenv('SLACK_WEBHOOK_URL')
        status_webhook_url = os.getenv('SLACK_STATUS_WEBHOOK_URL')

        schedules_map = dict()
        message = Message(tz=timezone_KST)
        try:
            for date in dates:
                search_url = f'{url}/{departure_location}-{arrival_location}-{date}?adt=2'
                schedules = get_flight_schedules(search_url)
                schedules = filter_time(schedules, departure_time, arrival_time)
                if schedules:
                    schedules_map[date] = schedules

            for date, schedules in schedules_map.items():
                formated_date = datetime.strptime(date, '%Y%m%d').strftime('%m-%d')
                message.text += "\n".join([
                    f"*Airline:* {schedule['airline_name']}\n*Dep:* {departure_location} {formated_date} {schedule['departure_time']} - *Arr:* {arrival_location} {formated_date} {schedule['arrival_time']}\n*Fee:* {schedule['fee']}\n"
                    for schedule in schedules
                ])

        except Exception as e:
            message.text = f"Error sending message: {e}\n{traceback.format_exc()}"

        current_time = datetime.now(timezone_KST)
        if current_time.minute != server_time_ticker.minute:
            current_time_str = current_time.strftime('%Y-%m-%d %H:%M:%S')
            send_slack_webhook(status_webhook_url, f'{current_time_str} | {server_name} is running')
            server_time_ticker = current_time

        if previous_message.text != message.text:
            if message.text != '':
                message.is_new = True
                send_slack_webhook(webhook_url, message.get_print_text())
            else:
                send_slack_webhook(webhook_url, "좌석이 마감되었습니다.")
        previous_message = message

        random_number = random.randint(10, 15)
        time.sleep(random_number)


if __name__ == "__main__":
    main()
