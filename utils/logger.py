import os

def send_telegram_message(message: str):
    """
    Sends a monitoring message to the configured Telegram channel.
    (Mock implementation for portfolio)
    """
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if token and chat_id:
        # requests.post(f"https://api.telegram.org/bot{token}/sendMessage", ...)
        pass
    else:
        # Fallback to stdout
        pass
        
    print(f"[{get_current_time()}] 📢 TELEGRAM: {message}")

def get_current_time():
    import datetime
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
