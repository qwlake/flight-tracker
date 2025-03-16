import time
import traceback
from datetime import timezone, timedelta, datetime

from dotenv import load_dotenv
import os
from crawler import get_flight_schedules
from slack import send_slack_webhook
import random

load_dotenv()
KST = timezone(timedelta(hours=9))


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

    previous_message = ''

    while True:
        url = os.getenv('FLIGHT_SCHEDULE_URL')
        dates = os.getenv('FLIGHT_SCHEDULE_DATE').split(',')
        departure_time = os.getenv('FLIGHT_SCHEDULE_DEPARTURE_TIME')
        arrival_time = os.getenv('FLIGHT_SCHEDULE_ARRIVAL_TIME')
        webhook_url = os.getenv('SLACK_WEBHOOK_URL')

        schedules_map = dict()
        try:
            for date in dates:
                tmp = url + date + '?adt=2'
                schedules = get_flight_schedules(tmp)
                schedules = filter_time(schedules, departure_time, arrival_time)
                if schedules:
                    schedules_map[date] = schedules

            message = ''

            for date, schedules in schedules_map.items():
                message += "\n".join([
                    f"*Airline:* {schedule['airline_name']}\n*Departure:* {date} {schedule['departure_time']} - *Arrival:* {date} {schedule['arrival_time']}\n*Fee:* {schedule['fee']}\n"
                    for schedule in schedules
                ])

            if message == '':
                message = "예약 가능 스케줄이 없습니다."
            else:
                if previous_message != message:
                    new_message = True
                else:
                    new_message = False
                previous_message = message
                if new_message:
                    message = "<!channel>\n" + message

        except Exception as e:
            message = f"Error sending message: {e}\n{traceback.format_exc()}"

        current_time = datetime.now(KST).strftime('%m-%d %H:%M')
        send_slack_webhook(webhook_url, f'{current_time} | {message}')

        random_number = random.randint(30, 60)
        time.sleep(random_number)

if __name__ == "__main__":
    main()
