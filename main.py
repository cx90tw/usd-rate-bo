import requests
from bs4 import BeautifulSoup
import os

def get_usd_rate():
    url = 'https://rate.bot.com.tw/xrt?Lang=zh-TW'
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')

    # 擷取報價時間
    time_tag = soup.select_one('span.time')
    rate_time = time_tag.text.strip() if time_tag else '無法取得報價時間'

    # 擷取美金匯率
    rows = soup.select('table.table tbody tr')
    for row in rows:
        if 'USD' in row.text:
            cols = row.find_all('td')
            cash_buy = float(cols[1].text.strip())
            cash_sell = float(cols[2].text.strip())
            twd_usdt = round(cash_sell + 0.35, 3)

            return (
                f"【台灣銀行美金匯率】\n"
                f"資料時間：{rate_time}\n"
                f"買入：{cash_buy}\n"
                f"賣出：{cash_sell}\n\n"
                f"===============\n"
                f"TWD-USDT：{twd_usdt}\n"
                f"===============\n\n"
                f"「本匯率僅供參考」"
            )

def send_to_telegram(text):
    token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {'chat_id': chat_id, 'text': text}
    requests.post(url, data=payload)

if __name__ == "__main__":
    msg = get_usd_rate()
    print(msg)
    send_to_telegram(msg)
