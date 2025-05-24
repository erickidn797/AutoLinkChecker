import os
import time
import requests
from telegram import Bot
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

PROXIES = {
    "Telkomsel": os.getenv("PROXY_TELKOMSEL"),
    "Indosat": os.getenv("PROXY_INDOSAT"),
    "XL": os.getenv("PROXY_XL"),
    "Smartfren": os.getenv("PROXY_SMARTFREN"),
    "Tri": os.getenv("PROXY_TRI"),
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
        else:
            return f"[{provider_name}] ⚠️ {url} error {r.status_code}"
    except Exception as e:
        return f"[{provider_name}] ⚠️ {url} gagal diakses ({str(e)})"

def run_check():
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
                time.sleep(1)  # menghindari rate limit

    message = "\n".join(results)
    bot.send_message(chat_id=CHAT_ID, text=message[:4096])

if __name__ == "__main__":
    run_check()
