import requests
from bs4 import BeautifulSoup
import os

def get_boc_usd_cash_rates():
    url = 'https://www.boc.cn/sourcedb/whpj/'
    res = requests.get(url)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')

    table = soup.find('table', attrs={'align': 'left'})
    rows = table.find_all('tr')

    for row in rows:
        cols = row.find_all('td')
        if len(cols) >= 6 and '美元' in cols[0].text:
            cash_buy = float(cols[1].text.strip())
            cash_sell = float(cols[3].text.strip())
            return cash_buy, cash_sell
    return None, None

def get_usd_rate():
    url = 'https://rate.bot.com.tw/xrt?Lang=zh-TW'
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')

    # 報價時間
    time_tag = soup.select_one('span.time')
    rate_time = time_tag.text.strip() if time_tag else '無法取得報價時間'

    # 擷取台銀美金匯率
    rows = soup.select('table.table tbody tr')
    for row in rows:
        if 'USD' in row.text:
            cols = row.find_all('td')
            cash_buy = float(cols[1].text.strip())
            cash_sell = float(cols[2].text.strip())
            spot_buy = float(cols[3].text.strip())
            spot_sell = float(cols[4].text.strip())
            spot_avg = round((spot_buy + spot_sell) / 2, 3)

            # 衍生價格
            twd_usdt = round(spot_avg * 1.02, 3)
            usdt_twd = round(spot_avg * 0.99, 3)
            cny_usdt = round(spot_avg * 1.022, 3)

            # 抓中國銀行數據
            boc_cash_buy, boc_cash_sell = get_boc_usd_cash_rates()

            return (
                f"【台灣銀行美金匯率】\n"
                f"買入：{cash_buy}\n"
                f"賣出：{cash_sell}\n"
                f"均價：{spot_avg}\n\n"
                f"【中國銀行美金匯率】\n"
                f"賣出：{boc_cash_sell}\n"
                f"買入：{boc_cash_buy}\n\n"
                f"===============\n"
                f"TWD-USDT：{twd_usdt}\n"
                f"USDT-TWD：{usdt_twd}\n"
                f"CNY-USDT：{cny_usdt}\n"
                f"===============\n\n"
                f"本匯率僅供參考使用\n"
                f"資料時間：{rate_time}\n"
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
