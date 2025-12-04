### Status Moving Text Self-b0t with Fixed Health Check
import os
import time
import requests
import urllib3
import threading
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Global flag to track bot health
bot_healthy = True
last_success = datetime.now()

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.handle_request()
    
    def do_HEAD(self):
        self.handle_request(head_only=True)
    
    def handle_request(self, head_only=False):
        global bot_healthy, last_success
        
        # Check if bot is still running
        time_since_last = (datetime.now() - last_success).seconds
        
        if time_since_last > 300:  # 5 minutes without updates
            bot_healthy = False
            self.send_response(503)  # Service Unavailable
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            if not head_only:
                self.wfile.write(b'Bot appears to be stuck')
            return
        
        if self.path == '/health' or self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            if not head_only:
                self.wfile.write(b'Discord Status Bot is running!')
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        # Optional: log health checks if needed
        # print(f"[Health Check] {self.address_string()} - {self.path}")
        pass

def start_health_server():
    """Start HTTP server for health checks"""
    port = int(os.getenv("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    print(f"🩺 Health check server running on port {port}")
    print(f"✅ Endpoints: GET/HEAD http://0.0.0.0:{port}/health")
    server.serve_forever()

# Get token from environment variable
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    print("❌ ERROR: DISCORD_TOKEN environment variable is not set!")
    exit(1)

def update_health():
    """Update last successful operation timestamp"""
    global last_success
    last_success = datetime.now()

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
        response = requests.patch(url, headers=headers, json=data, verify=False, timeout=10)
        response.raise_for_status()
        update_health()
        print(f"✅ Status updated: {message}")
        return True
    except requests.exceptions.RequestException as e:
        update_health()  # Still update timestamp for attempted communication
        if response is not None and response.status_code == 429:
            retry_after = response.json().get('retry_after', 5)
            print(f"⏳ Rate limited. Waiting {retry_after} seconds...")
            time.sleep(retry_after)
            return change_user_status(message)
        else:
            print(f"❌ Status Error: {e}")
            if response:
                print(f"Response: {response.status_code}")
            return False

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
        response = requests.patch(url, headers=headers, json=data, verify=False, timeout=10)
        response.raise_for_status()
        update_health()
        print(f"✅ Bio updated: {bio_text}")
        return True
    except requests.exceptions.RequestException as e:
        update_health()
        if response is not None and response.status_code == 429:
            retry_after = response.json().get('retry_after', 5)
            print(f"⏳ Rate limited. Waiting {retry_after} seconds...")
            time.sleep(retry_after)
            return change_user_bio(bio_text)
        else:
            print(f"❌ Bio Error: {e}")
            if response:
                print(f"Response: {response.status_code}")
            return False

def generate_moving_text(base_text, length=20):
    dot_padding = '-' * length
    moving_texts = []
    for text in base_text:
        full_text = dot_padding + text + dot_padding
        moving_texts.extend([full_text[i:i+length] for i in range(len(full_text) - length + 1)])
    return moving_texts

def discord_bot():
    """Main bot function"""
    base_text = ["𝘿-𝙀-𝙁-𝙄-𝙉-𝙄-𝙓"]
    status_length = 13
    moving_texts = generate_moving_text(base_text, status_length)

    bio_texts = ["𝔡𝔢𝔣𝔦𝔫𝔦𝔵", "𝖉𝖊𝖋𝖎𝖓𝖎𝖝", "𝓭𝓮𝓯𝓲𝓷𝓲𝔁", "𝒹𝑒𝒻𝒾𝓃𝒾𝓍", "𝕕𝕖𝕗𝕚𝕟𝕚𝕩", "ｄｅｆｉｎｉｘ", "ᴅᴇꜰɪɴɪx"]

    print("🚀 Discord Status Bot Started!")
    print(f"📝 Status variations: {len(moving_texts)}")
    print(f"📖 Bio variations: {len(bio_texts)}")
    
    consecutive_errors = 0
    max_errors = 10
    
    while True:
        try:
            for i, message in enumerate(moving_texts):
                # Update status
                status_ok = change_user_status(message)
                
                # Update bio every 2nd iteration
                if i % 2 == 0:
                    bio_index = (i // 2) % len(bio_texts)
                    bio_ok = change_user_bio(bio_texts[bio_index])
                
                # Reset error counter on success
                if status_ok:
                    consecutive_errors = 0
                else:
                    consecutive_errors += 1
                
                # If too many errors, wait longer
                if consecutive_errors >= max_errors:
                    print(f"⚠️ Too many errors ({consecutive_errors}). Waiting 60 seconds...")
                    time.sleep(60)
                    consecutive_errors = max_errors // 2  # Reduce counter but not reset
                
                time.sleep(1.3)
                
        except Exception as e:
            print(f"🔥 Critical bot error: {e}")
            update_health()
            time.sleep(30)  # Wait before retrying
            continue

def main():
    """Start health server and bot"""
    print("=" * 50)
    print("Discord Status Bot with Health Check Server")
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Start health server in background
    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()
    
    # Give health server time to start
    time.sleep(2)
    
    # Start bot
    discord_bot()

if __name__ == "__main__":
    main()
