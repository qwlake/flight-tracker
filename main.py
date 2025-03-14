import time
import traceback
from dotenv import load_dotenv
import os
from crawler import get_flight_schedules
from slack import send_slack_webhook
import random

load_dotenv()

def main():

    previous_message = ''

    while True:
        url = os.getenv('FLIGHT_SCHEDULE_URL')
        dates = os.getenv('FLIGHT_SCHEDULE_DATE')
        webhook_url = os.getenv('SLACK_WEBHOOK_URL')

        schedules_map = dict()
        try:
            for date in dates.split(','):
                tmp = url + date + '?adt=2'
                schedules = get_flight_schedules(tmp)
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

        send_slack_webhook(webhook_url, message)

        random_number = random.randint(30, 60)
        time.sleep(random_number)

if __name__ == "__main__":
    main()
