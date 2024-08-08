import os
from crawler import is_flight_schedule_available
from slack import send_slack_webhook

def main():
    print('start to check flight schedule')
    is_available = is_flight_schedule_available()
    if is_available:
        webhook_url = os.getenv('SLACK_WEBHOOK_URL')
        message = 'flight schedule available !'
        send_slack_webhook(webhook_url, message)


if __name__ == "__main__":
    main()
