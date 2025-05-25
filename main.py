import requests
from bs4 import BeautifulSoup
import os

def get_usd_rate():
    url = 'https://rate.bot.com.tw/xrt?Lang=zh-TW'
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    rows = soup.select('table.table tbody tr')
    for row in rows:
        if 'USD' in row.text:
            cols = row.find_all('td')
            cash_buy = cols[1].text.strip()
            cash_sell = cols[2].text.strip()
            spot_buy = cols[3].text.strip()
            spot_sell = cols[4].text.strip()
            return f"【台灣銀行美金匯率】\n現金買入：{cash_buy}\n現金賣出：{cash_sell}\n即期買入：{spot_buy}\n即期賣出：{spot_sell}"

def send_to_telegram(text):
    token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {'chat_id': chat_id, 'text': text}
    requests.post(url, data=payload)

if __name__ == "__main__":
    msg = get_usd_rate()
    send_to_telegram(msg)
