import time
import traceback
from dotenv import load_dotenv
import os
from crawler import is_flight_schedule_available, get_flight_schedules
from slack import send_slack_webhook

load_dotenv()

def main():
    flight_schedule_date = os.getenv('FLIGHT_SCHEDULE_DATE')
    url = f'https://sky.interpark.com/schedules/domestic/CJU-GMP-{flight_schedule_date}?adt=2&chd=0&inf=0&seat=DOMESTIC_BASE&pickAirLine=&pickMainFltNo=&pickSDate='

    webhook_url = os.getenv('SLACK_WEBHOOK_URL')

    try:
        print('Start to check flight schedule')
        schedules = get_flight_schedules(url)
        print(schedules)
        message = "\n".join([
            f"*Airline:* {schedule['airline_name']}\n*Departure:* {schedule['departure_time']} - *Arrival:* {schedule['arrival_time']}\n*Fee:* {schedule['fee']}\n"
            for schedule in schedules
        ])

        send_slack_webhook(webhook_url, message)

    except Exception as e:
        error_message = f"Error sending message: {e}\n{traceback.format_exc()}"
        print(error_message)

        send_slack_webhook(webhook_url, error_message)

if __name__ == "__main__":
    main()
