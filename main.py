import os
import requests
import random
import string
import time

BASE_URL = "https://discord.com/api/v9/users/@me/pomelo-attempt"
WEBHOOK_URL = "Enter WEBHOOK_URL HERE" 


def validate_token(token):
    """Validate Discord token format and check if it's authorized"""
    if not token:
        return False

    headers = {
        "Authorization":
        token,
        "Content-Type":
        "application/json",
        "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"
    }
    try:
        response = requests.get("https://discord.com/api/v9/users/@me",
                                headers=headers)
        if response.status_code == 200:
            return True
        print(f"[⚠️] Token validation error: {response.status_code}")
        return False
    except Exception as e:
        print(f"[!] Validation error: {str(e)}")
        return False


def generate_username():
    """Generate a random username between 3-5 characters"""
    length = random.randint(3, 5)
    return ''.join(
        random.choices(string.ascii_lowercase + string.digits, k=length))


def check_username(token, username):
    """Check if a username is available"""
    headers = {
        "Authorization":
        token,
        "Content-Type":
        "application/json",
        "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    payload = {"username": username, "global_name": None}

    try:
        response = requests.post(BASE_URL, headers=headers, json=payload)

        if response.status_code == 429:  # Rate limit
            retry_after = response.json().get("retry_after", 5)
            print(f"[⚠️] Rate-limited. Waiting {retry_after} seconds...")
            time.sleep(retry_after)
            return None
        elif response.status_code == 401:  # Unauthorized
            print(
                "[❌] Token is invalid or expired. Please provide a valid token."
            )
            return False
        elif response.status_code == 200:
            return not response.json().get("taken", True)
        else:
            print(f"[!] Error {response.status_code}: {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"[!] Network error: {e}")
        return None


def send_to_webhook(username):
    """Send available username to Discord webhook"""
    data = {"content": f"✅ Available Username: `{username}`"}
    try:
        response = requests.post(WEBHOOK_URL, json=data)
        if response.status_code == 204:
            print(f"[✅] Sent '{username}' to webhook.")
            return True
        else:
            print(f"[⚠️] Webhook failed. Status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"[!] Webhook error: {e}")
        return False


def main():
    print("Discord Username Checker")
    print("-" * 30)

    # Validate token from environment variable
    token = os.environ.get('DISCORD_TOKEN')
    if not token:
        print("[❌] Please set the DISCORD_TOKEN environment variable.")
        return

    if not validate_token(token):
        print("[❌] Invalid token. Please check your DISCORD_TOKEN.")
        return

    print("\n[✅] Token validated successfully!")
    print("[🔄] Starting username check...")

    try:
        check_count = 0
        while True:
            uname = generate_username()
            print(f"\nChecking username: {uname}")

            result = check_username(token, uname)

            if result is True:
                print(f"[✅] '{uname}' is AVAILABLE!")
                send_to_webhook(uname)
            elif result is False:
                print(f"[❌] '{uname}' is taken or token invalid.")
            else:
                print("[⚠️] Retrying after delay...")

            check_count += 1
            if check_count % 10 == 0:
                print(f"\n[📊] Checked {check_count} usernames so far...")

            time.sleep(2)  # Delay between checks

    except KeyboardInterrupt:
        print("\n\n[👋] Stopped by user. Thanks for using the checker!")


if __name__ == "__main__":
    main()
