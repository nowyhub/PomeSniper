import requests
import random
import string
import time

BASE_URL = "https://discord.com/api/v9/users/@me/pomelo-attempt" # API which checks for available usernames
WEBHOOK_URL = "ENTER WEBHOOK HERE"  # Replace with your actual webhook URL

# Generates username 
def generate_username():
    length = random.randint(3, 5)
    return ''.join(
        random.choices(string.ascii_lowercase + string.digits, k=length))

# sends a request to API endpoint to check if vaild username
def check_username(token, username):
    headers = {"Content-Type": "application/json", "Authorization": token}
    payload = {"username": username, "global_name": None}
    try:
        response = requests.post(BASE_URL, headers=headers, json=payload)
        if response.status_code == 429:
            retry_after = response.json().get("retry_after", 5)
            print(f"[⚠️] Rate-limited. Sleeping for {retry_after} seconds...")
            time.sleep(retry_after)
            return None
        elif response.status_code == 200:
            return not response.json().get("taken", True)
        else:
            print(
                f"[!] Error {response.status_code} while checking '{username}'"
            )
            return None
    except requests.exceptions.RequestException as e:
        print(f"[!] Request exception: {e}")
        return None

# Webhook sends available usernames in channel
def send_to_webhook(username):
    data = {"content": f"Available Username: `{username}`"}
    try:
        response = requests.post(WEBHOOK_URL, json=data)
        if response.status_code == 200:
            print(f"[✅] Sent '{username}' to webhook.")
        else:
            print(
                f"[⚠️] Webhook failed. Code: {response.status_code}, Response: {response.text}"
            )
    except requests.exceptions.RequestException as e:
        print(f"[!] Webhook error: {e}")

# Must give discord Token to check if vaild user when code is ran
def main():
    token = input("Enter your Discord token: ").strip()
    try:
        while True:
            uname = generate_username()
            print(f"Generated username: {uname}")
            result = check_username(token, uname)
            if result is True:
                print(f"[✅] '{uname}' is AVAILABLE!")
                send_to_webhook(uname)
            elif result is False:
                print(f"[❌] '{uname}' is taken.")
            else:
                print("[⚠️] Error or rate-limited. Sleeping...")
                time.sleep(5)
            time.sleep(5)  # Delay to prevent hitting rate limits
    except KeyboardInterrupt:
        print("Stopped by user.")


if __name__ == "__main__":
    main()
