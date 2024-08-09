from dotenv import load_dotenv
import os
from crawler import is_flight_schedule_available
from slack import send_slack_webhook

load_dotenv()

def main():
    print('start to check flight schedule')
    is_available = is_flight_schedule_available()
    if is_available:
        webhook_url = os.getenv('SLACK_WEBHOOK_URL')
        message = 'flight schedule available !'

        # TODO: 비행기 스케줄 시간도 긁어서 보내기
        send_slack_webhook(webhook_url, message)


if __name__ == "__main__":
    main()
