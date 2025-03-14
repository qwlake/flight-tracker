import time
import traceback
from dotenv import load_dotenv
import os
from crawler import get_flight_schedules
from slack import send_slack_webhook
import random

load_dotenv()

def main():
    while True:
        urls = os.getenv('FLIGHT_SCHEDULE_URL')
        webhook_url = os.getenv('SLACK_WEBHOOK_URL')

        schedules = []
        try:
            for url in urls.split('\\'):
                schedules += get_flight_schedules(url)

            if schedules:
                message = "<!channel>\n" + "\n".join([
                    f"*Airline:* {schedule['airline_name']}\n*Departure:* {schedule['departure_time']} - *Arrival:* {schedule['arrival_time']}\n*Fee:* {schedule['fee']}\n"
                    for schedule in schedules
                ])
            else:
                message = "예약 가능 스케줄이 없습니다."

        except Exception as e:
            message = f"Error sending message: {e}\n{traceback.format_exc()}"

        send_slack_webhook(webhook_url, message)

        random_number = random.randint(30, 60)
        time.sleep(random_number)

if __name__ == "__main__":
    main()
