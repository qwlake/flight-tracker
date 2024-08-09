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
        flight_schedule_date = os.getenv('FLIGHT_SCHEDULE_DATE')
        url = f'https://sky.interpark.com/schedules/domestic/CJU-GMP-{flight_schedule_date}?adt=2&chd=0&inf=0&seat=DOMESTIC_BASE&pickAirLine=&pickMainFltNo=&pickSDate='

        webhook_url = os.getenv('SLACK_WEBHOOK_URL')

        try:
            print('Start to check flight schedule')
            schedules = get_flight_schedules(url)
            if schedules:
                message = "\n".join([
                    f"*Airline:* {schedule['airline_name']}\n*Departure:* {schedule['departure_time']} - *Arrival:* {schedule['arrival_time']}\n*Fee:* {schedule['fee']}\n"
                    for schedule in schedules
                ])

                send_slack_webhook(webhook_url, message)

        except Exception as e:
            error_message = f"Error sending message: {e}\n{traceback.format_exc()}"

            send_slack_webhook(webhook_url, error_message)
        
        random_number = random.randint(30, 60)
        time.sleep(random_number)

if __name__ == "__main__":
    main()
