### Status Moving Text Self-b0t with Health Check Server
import os
import time
import requests
import urllib3
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# Disable SSL warnings for cleaner output
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Health Check Server Class
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health' or self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Discord Status Bot is running!')
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        # Disable default logging to keep logs clean
        pass

def start_health_server():
    """Start a simple HTTP server for health checks"""
    port = int(os.getenv("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    print(f"🩺 Health check server running on port {port}")
    server.serve_forever()

# Get token from environment variable
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    print("❌ ERROR: DISCORD_TOKEN environment variable is not set!")
    print("Please set it in Render dashboard → Environment section")
    exit(1)

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
        response = requests.patch(url, headers=headers, json=data, verify=False)
        response.raise_for_status()  
        print(f"✅ Status updated: {message}")
    except requests.exceptions.RequestException as e:
        if response is not None and response.status_code == 429:  
            retry_after = response.json().get('retry_after', 1)
            print(f"⏳ Rate limited. Waiting {retry_after} seconds...")
            time.sleep(retry_after)
            change_user_status(message) 
        else:
            print(f"❌ Error: {e}")
            if response:
                print(f"Response: {response.status_code} - {response.text}")

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
        response = requests.patch(url, headers=headers, json=data, verify=False)
        response.raise_for_status()  
        print(f"✅ Bio updated: {bio_text}")
    except requests.exceptions.RequestException as e:
        if response is not None and response.status_code == 429:  
            retry_after = response.json().get('retry_after', 1)
            print(f"⏳ Rate limited. Waiting {retry_after} seconds...")
            time.sleep(retry_after)
            change_user_bio(bio_text) 
        else:
            print(f"❌ Error: {e}")
            if response:
                print(f"Response: {response.status_code} - {response.text}")

def generate_moving_text(base_text, length=20):
    dot_padding = '-' * length
    moving_texts = []
    for text in base_text:
        full_text = dot_padding + text + dot_padding
        moving_texts.extend([full_text[i:i+length] for i in range(len(full_text) - length + 1)])
    return moving_texts

def discord_bot():
    """Main bot function that runs in a loop"""
    base_text = ["𝘿-𝙀-𝙁-𝙄-𝙉-𝙄-𝙓"]  # Your text here
    status_length = 13
    moving_texts = generate_moving_text(base_text, status_length)

    bio_texts = ["𝔡𝔢𝔣𝔦𝔫𝔦𝔵", "𝖉𝖊𝖋𝖎𝖓𝖎𝖝", "𝓭𝓮𝓯𝓲𝓷𝓲𝔁", "𝒹𝑒𝒻𝒾𝓃𝒾𝓍", "𝕕𝕖𝕗𝕚𝕟𝕚𝕩", "ｄｅｆｉｎｉｘ", "ᴅᴇꜰɪɴɪx", "​🇩​​🇪​​🇫​​🇮​​🇳​​🇮​​🇽​", "🄳🄴🄵🄸🄽🄸🅇", "🅳🅴🅵🅸🅽🅸🆇", "dₑfᵢₙᵢₓ", "ᵈᵉᶠⁱⁿⁱˣ", "ⓓⓔⓕⓘⓝⓘⓧ", "𝚍𝚎𝚏𝚒𝚗𝚒𝚡", "𝙙𝙚𝙛𝙞𝙣𝙞𝙭", "DΣFIПIX", "ĐɆ₣ł₦łӾ", "ᗪ乇千丨几丨乂", "【d】【e】【f】【i】【n】【i】【x】", "『d』『e』『f』『i』『n』『i』『x』"]

    print("🚀 Discord Status Bot Started!")
    print(f"📝 Using {len(moving_texts)} status variations")
    print(f"📖 Using {len(bio_texts)} bio variations")
    
    while True:
        for i, message in enumerate(moving_texts):
            change_user_status(message)
            
            if i % 2 == 0:
                bio_index = (i // 2) % len(bio_texts)
                change_user_bio(bio_texts[bio_index])
            
            time.sleep(1.3)

def main():
    """Start both the health server and discord bot"""
    print("=" * 50)
    print("Starting Discord Status Bot with Health Check Server")
    print("=" * 50)
    
    # Start health check server in a separate thread
    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()
    
    # Start the discord bot (this will run in the main thread)
    discord_bot()

if __name__ == "__main__":
    main()
