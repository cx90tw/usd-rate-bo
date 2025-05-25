import requests
from bs4 import BeautifulSoup
import os

def get_usdt_price():
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'application/json'
        }
        res = requests.get('https://max-api.maicoin.com/api/v2/tickers/usdt_twd', headers=headers, timeout=5)
        data = res.json()
        price = float(data['ticker']['last'])
        return round(price, 3)
    except Exception as e:
        print(f"抓取 MAX USDT 價格失敗：{e}")
        return '無法取得'

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
            suggested_price_1 = round(cash_sell + 0.35, 3)

            usdt_price = get_usdt_price()
            if isinstance(usdt_price, float):
                suggested_price_2 = round(usdt_price + 0.45, 3)
            else:
                suggested_price_2 = '無法計算'

            return (
                f"【台灣銀行美金匯率】\n"
                f"買入：{cash_buy}\n"
                f"賣出：{cash_sell}\n\n"
                f"【MAX交易所USDT】\n"
                f"USDT 價格：NT$ {usdt_price}\n\n"
                f"=============\n"
                f"0.35\n"
                f"TWD-USD：(台灣銀行賣出金額+0.35)：{suggested_price_1}\n"
                f"0.45\n"
                f"TWD-USD：(USDT價格+0.45)：{suggested_price_2}\n"
                f"=============\n"
                f"資料時間：{rate_time}\n"
                f"「本匯率報價機器人僅供參考」"
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
