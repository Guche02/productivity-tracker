import os
import random
from dotenv import load_dotenv
from twilio.rest import Client
from apscheduler.schedulers.background import BackgroundScheduler

load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
USER_WHATSAPP_NUMBER = os.getenv("USER_WHATSAPP_NUMBER")  

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

quotes = [
    "Are you daydreaming again? Open that app and log your work, beta!",
    "If you don’t track your efforts, how will you show me you’re serious? Get to it!",
    "No more slacking! Even the cows are busy; you should be too.",
    "I’m watching you — better see some progress logged before dinner!",
    "Remember, the harder you work, the sweeter the momo tastes later!",
    "Why wait for tomorrow when you can shine today? Log your productivity now!",
    "Don’t make me come over there and check if you really did your work!",
    "Your phone isn’t just for scrolling — use it to log your success, okay?",
    "I didn’t raise a lazy child — show me those productivity scores, fast!",
    "Work hard now, so you don’t have to beg me for extra masu later!"
]


def send_whatsapp_message(to, body):
    try:
        message = client.messages.create(
            from_=f"whatsapp:{TWILIO_PHONE_NUMBER}",
            body=body,
            to=f"whatsapp:{to}"
        )
        print(f"Sent: {body}")
        return message.sid
    except Exception as e:
        print(f"Error sending message: {e}")

def morning_job():
    quote = random.choice(quotes)
    send_whatsapp_message(USER_WHATSAPP_NUMBER, f"🌞 Hey! It's your productivity mother here. \n\n{quote}")

def night_job():
    reminder = "🌙 Good Evening from the productivity mother! Don't forget to log your productivity details on the platform. Stay consistent!"
    send_whatsapp_message(USER_WHATSAPP_NUMBER, reminder)

scheduler = None  

def start_scheduler():
    global scheduler
    if scheduler is None:  
        scheduler = BackgroundScheduler(timezone="Asia/Kathmandu")
        scheduler.add_job(morning_job, 'cron', hour=9, minute=4)
        scheduler.add_job(night_job, 'cron', hour=21, minute=30)
        scheduler.start()
        print("Scheduler started.")