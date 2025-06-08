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
    "Believe in yourself! You're capable of amazing things.",
    "Every morning is a fresh start. Make it count!",
    "Discipline is the bridge between goals and accomplishment.",
    "Productivity is never an accident. It's always the result of commitment.",
    "Success starts with self-discipline."
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
    send_whatsapp_message(USER_WHATSAPP_NUMBER, f"🌞 Good Morning! Here's your productivity quote:\n\n{quote}")

def night_job():
    reminder = "🌙 Good Evening! Don't forget to log your productivity details on the platform. Stay consistent!"
    send_whatsapp_message(USER_WHATSAPP_NUMBER, reminder)

scheduler = None  

def start_scheduler():
    global scheduler
    if scheduler is None:  
        scheduler = BackgroundScheduler(timezone="Asia/Kathmandu")
        scheduler.add_job(morning_job, 'cron', hour=7, minute=0)
        scheduler.add_job(night_job, 'cron', hour=21, minute=36)
        scheduler.start()
        print("Scheduler started.")