import os
import requests
import random
import time

BASE_URL = "https://discord.com/api/v9/users/@me/pomelo-attempt"
WEBHOOK_URL = "PASTE_WEBHOOK_HERE"


def validate_token(token):
    if not token:
        return False
    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    try:
        response = requests.get("https://discord.com/api/v9/users/@me",
                                headers=headers)
        return response.status_code == 200
    except Exception:
        return False


def generate_base_username():
    common_start = [
        "cr", "tr", "ch", "sh", "br", "bl", "st", "gr", "gl", "pl", "pr", "cl",
        "c", "z", "m", "l"
    ]
    common_vowels = ["a", "e", "i", "o", "u"]
    common_end = [
        "sh", "ck", "nk", "nt", "ne", "nd", "st", "ch", "n", "t", "x", "sh",
        "y"
    ]

    part1 = random.choice(common_start)
    part2 = random.choice(common_vowels)
    part3 = random.choice(common_end)

    raw = part1 + part2 + part3

    leet_map = {
        'a': '4',
        'e': '3',
        'i': '1',
        'o': '0',
        's': '5',
        't': '7',
        'l': '1',
        'z': '2',
        'b': '8'
    }

    chars = list(raw)
    leet_applied = False
    for i in range(len(chars)):
        if not leet_applied and chars[i] in leet_map:
            chars[i] = leet_map[chars[i]]
            leet_applied = True

    final = ''.join(chars)

    # Trim the final username to 3 or 4 characters
    return final[:random.choice([3, 4])]


def check_username(token, username):
    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    payload = {"username": username, "global_name": None}
    try:
        response = requests.post(BASE_URL, headers=headers, json=payload)
        if response.status_code == 429:
            retry_after = response.json().get("retry_after", 5)
            print(f"[⚠️] Rate-limited. Waiting {retry_after} seconds...")
            time.sleep(retry_after)
            return None
        elif response.status_code == 401:
            print("[❌] Token is invalid or expired.")
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
    data = {"content": f"✅ Available Username: `{username}`"}
    try:
        response = requests.post(WEBHOOK_URL, json=data)
        return response.status_code == 204
    except requests.exceptions.RequestException as e:
        print(f"[!] Webhook error: {e}")
        return False


def main():
    print("Discord Username Checker")
    print("-" * 30)

    token = os.environ.get('DISCORD_TOKEN')
    if not token:
        print("[❌] Please set the DISCORD_TOKEN environment variable.")
        return

    if not validate_token(token):
        print("[❌] Invalid token. Please check your DISCORD_TOKEN.")
        return

    print("\n[✅] Token validated successfully!")
    print("[🔄] Starting username check...")

    check_count = 0
    try:
        while True:
            uname = generate_base_username()
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

            time.sleep(2)

    except KeyboardInterrupt:
        print("\n\n[👋] Stopped by user. Thanks for using the checker!")


if __name__ == "__main__":
    main()
