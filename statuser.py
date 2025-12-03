### Status Moving Text Self-b0t 
import time
import requests
import urllib3

# Disable SSL warnings for cleaner output
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TOKEN = "NzgxOTg2MTU1NDQ0NDM3MDQy.GNd3Mf._gZB1XxNDONLcoOAi5gtFYRhSWOMZYQAQVFlgw"  # put your user token here

def change_user_status(message):
    url = "https://discord.com/api/v9/users/@me/settings"
    headers = {
        "Authorization": TOKEN,
        "Content-Type": "application/json",
    }
    data = {
        "custom_status": {
            "text": message
        }
    }
    response = None
    try:
        response = requests.patch(url, headers=headers, json=data, verify=False)  # Added verify=False
        response.raise_for_status()  
        print(f"Status: {message}")
    except requests.exceptions.RequestException as e:
        if response is not None and response.status_code == 429:  
            retry_after = response.json().get('retry_after', 1)
            print(f"bro got ratelimited for {retry_after} seconds.")
            time.sleep(retry_after)
            change_user_status(message) 
        else:
            print("you fucked up:", e)

def change_user_bio(bio_text):
    url = "https://discord.com/api/v9/users/@me/profile"
    headers = {
        "Authorization": TOKEN,
        "Content-Type": "application/json",
    }
    data = {
        "bio": bio_text
    }
    response = None
    try:
        response = requests.patch(url, headers=headers, json=data, verify=False)  # Added verify=False
        response.raise_for_status()  
        print(f"Bio: {bio_text}")
    except requests.exceptions.RequestException as e:
        if response is not None and response.status_code == 429:  
            retry_after = response.json().get('retry_after', 1)
            print(f"bro got ratelimited for {retry_after} seconds.")
            time.sleep(retry_after)
            change_user_bio(bio_text) 
        else:
            print("you fucked up:", e)

def generate_moving_text(base_text, length=20):
    dot_padding = '-' * length # what you use for the spaces
    moving_texts = []
    for text in base_text:
        full_text = dot_padding + text + dot_padding
        moving_texts.extend([full_text[i:i+length] for i in range(len(full_text) - length + 1)])
    return moving_texts

def main():
    base_text = ["𝘿-𝙀-𝙁-𝙄-𝙉-𝙄-𝙓"] # where you put what you wanna send, heres mine for an example
    status_length = 13  # length of display cool tingy
    moving_texts = generate_moving_text(base_text, status_length)

    # You can use the same moving text for both status and bio, or different ones
    bio_texts = ["𝔡𝔢𝔣𝔦𝔫𝔦𝔵", "𝖉𝖊𝖋𝖎𝖓𝖎𝖝", "𝓭𝓮𝓯𝓲𝓷𝓲𝔁", "𝒹𝑒𝒻𝒾𝓃𝒾𝓍", "𝕕𝕖𝕗𝕚𝕟𝕚𝕩", "ｄｅｆｉｎｉｘ", "ᴅᴇꜰɪɴɪx", "​🇩​​🇪​​🇫​​🇮​​🇳​​🇮​​🇽​", "🄳🄴🄵🄸🄽🄸🅇", "🅳🅴🅵🅸🅽🅸🆇", "dₑfᵢₙᵢₓ", "ᵈᵉᶠⁱⁿⁱˣ", "ⓓⓔⓕⓘⓝⓘⓧ", "𝚍𝚎𝚏𝚒𝚗𝚒𝚡", "𝙙𝙚𝙛𝙞𝙣𝙞𝙭", "DΣFIПIX", "ĐɆ₣ł₦łӾ", "ᗪ乇千丨几丨乂", "【d】【e】【f】【i】【n】【i】【x】", "『d』『e』『f』『i』『n』『i』『x』"]  # Customize this

    while True:
        for i, message in enumerate(moving_texts):
            change_user_status(message)
            
            # Update bio - you can choose to update it every cycle or less frequently
            # Example: update bio every 10 status changes
            if i % 2 == 0:
                bio_index = (i // 2) % len(bio_texts)
                change_user_bio(bio_texts[bio_index])
            
            time.sleep(1.3)  # Add a small delay to avoid rate limits

if __name__ == "__main__":
    main()