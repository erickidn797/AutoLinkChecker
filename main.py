import os
import time
import requests
from telegram import Bot
from dotenv import load_dotenv
from flask import Flask
import threading
import asyncio


load_dotenv()
app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

PROXIES = {
    "Telkomsel": os.getenv("PROXY_TELKOMSEL"),
    "XL": os.getenv("PROXY_XL"),
}

bot = Bot(token=BOT_TOKEN)

def check_url_with_proxy(url, provider_name, proxy_url):
    try:
        proxies = {
            "http": proxy_url,
            "https": proxy_url
        }
        r = requests.get(url, proxies=proxies, timeout=10, allow_redirects=True)
        if r.status_code == 200:
            return f"[{provider_name}] ✅ {url} dapat diakses"
        elif "internetpositif" in r.url or r.status_code in [403, 451]:
            return f"[{provider_name}] 🚫 {url} diblokir"
        elif r.is_redirect or r.status_code in [301, 302]:
            return f"[{provider_name}] 🔀 {url} redirect ke {r.headers.get('Location')}"
        else:
            return f"[{provider_name}] ⚠️ {url} error {r.status_code}"
    except Exception as e:
        return f"[{provider_name}] ⚠️ {url} gagal diakses ({str(e)})"

@app.route("/")
def index():
    return "URL checker is running."

@app.route("/run")
async def check_all_urls():
    results = []
    with open("listlink.txt") as file:
        urls = [line.strip() for line in file if line.strip()]
        for url in urls:
            for provider, proxy in PROXIES.items():
                if not proxy:
                    results.append(f"[{provider}] ⚠️ Proxy belum diatur")
                    continue
                result = check_url_with_proxy(url, provider, proxy)
                results.append(result)
                time.sleep(1)

    message = "\n".join(results)
    await bot.send_message(chat_id=CHAT_ID, text=message[:4096])


def scheduler():
    while True:
        asyncio.run(check_all_urls())
        time.sleep(7200)  # 2 jam = 7200 detik

# Mulai thread scheduler di background
threading.Thread(target=scheduler, daemon=True).start()

if __name__ == "__main__":
    threading.Thread(target=scheduler, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
