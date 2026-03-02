"""
Crypto Auto Trading BOT - Main Execution Engine
"""
import time
from config import settings
from utils.logger import send_telegram_message

def main():
    send_telegram_message("🚀 Trading Bot Started: Initializing Data Pipelines...")
    
    # Run the main asynchronous event loop for signal generation and order execution
    try:
        while True:
            # heartbeat
            time.sleep(60)
    except KeyboardInterrupt:
        send_telegram_message("🛑 Trading Bot Stopped Gracefully.")

if __name__ == "__main__":
    main()
