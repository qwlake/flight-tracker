import time
from dotenv import load_dotenv
import os
from crawler import is_flight_schedule_available
from slack import send_slack_webhook

load_dotenv()

def main():
    webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    message = 'flight schedule available !'

    while True:
        print('Start to check flight schedule')

        is_available = is_flight_schedule_available()

        if is_available:
            # TODO: 비행기 스케줄 시간도 긁어서 보내기
            send_slack_webhook(webhook_url, message)
        time.sleep(30)


if __name__ == "__main__":
    main()
