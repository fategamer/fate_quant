"""
Create a local .env from the example file if it does not exist.
Does not write tokens. You fill them yourself.
"""

import os
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXAMPLE = os.path.join(ROOT, "config", "secrets.example.env")
TARGET = os.path.join(ROOT, ".env")


def main():
    if os.path.exists(TARGET):
        print(f".env already exists at:\n{TARGET}")
        print("Open that file and fill TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID.")
        return
    if not os.path.exists(EXAMPLE):
        print("Missing config/secrets.example.env")
        return
    shutil.copyfile(EXAMPLE, TARGET)
    print(f"Created:\n{TARGET}")
    print("Now open .env and paste your token and chat id there.")
    print("Do not commit .env and do not send keys in chat.")


if __name__ == "__main__":
    main()
