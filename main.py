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
        url = os.getenv('FLIGHT_SCHEDULE_URL')
        dates = os.getenv('FLIGHT_SCHEDULE_DATE').split(',')
        departure_time = os.getenv('FLIGHT_SCHEDULE_DEPARTURE_TIME')
        arrival_time = os.getenv('FLIGHT_SCHEDULE_ARRIVAL_TIME')
        webhook_url = os.getenv('SLACK_WEBHOOK_URL')
        status_webhook_url = os.getenv('SLACK_STATUS_WEBHOOK_URL')

        schedules_map = dict()
        message = Message(tz=timezone_KST)
        try:
            for date in dates:
                tmp = url + date + '?adt=2'
                schedules = get_flight_schedules(tmp)
                schedules = filter_time(schedules, departure_time, arrival_time)
                if schedules:
                    schedules_map[date] = schedules

            for date, schedules in schedules_map.items():
                message.text += "\n".join([
                    f"*Airline:* {schedule['airline_name']}\n*Departure:* {date} {schedule['departure_time']} - *Arrival:* {date} {schedule['arrival_time']}\n*Fee:* {schedule['fee']}\n"
                    for schedule in schedules
                ])

            if message.text != '' and previous_message.text != message.text:
                message.is_new = True
            previous_message = message

        except Exception as e:
            message.text = f"Error sending message: {e}\n{traceback.format_exc()}"

        current_time = datetime.now(timezone_KST)
        if current_time.minute != server_time_ticker.minute:
            current_time_str = current_time.strftime('%y-%m-%d %H:%M:%S')
            send_slack_webhook(status_webhook_url, f'{current_time_str} | Server is running')
            server_time_ticker = current_time

        if message.text != '':
            send_slack_webhook(webhook_url, message.get_print_text())

        random_number = random.randint(5, 10)
        time.sleep(random_number)


if __name__ == "__main__":
    main()
