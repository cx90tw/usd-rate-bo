import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime

def get_boc_usd_cash_rates():
    url = 'https://www.boc.cn/sourcedb/whpj/'
    res = requests.get(url)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')

    # 擷取中國銀行發布時間
    publish_text = soup.get_text()
    boc_time = "無法取得"
    for line in publish_text.splitlines():
        if "发布时间：" in line:
            date_part = line.strip().replace("发布时间：", "").split()[0].replace("-", "/")
            time_part = line.strip().split()[-1][:5]
            boc_time = f"{date_part} {time_part}"
            break

    # 擷取美元現鈔買入與賣出價格（人民幣/100 美元）
    table = soup.find('table', attrs={'align': 'left'})
    rows = table.find_all('tr')

    for row in rows:
        cols = row.find_all('td')
        if len(cols) >= 6 and '美元' in cols[0].text:
            cash_buy = float(cols[1].text.strip()) / 100
            cash_sell = float(cols[3].text.strip()) / 100
            return cash_buy, cash_sell, boc_time
    return None, None, boc_time

def get_usd_rate():
    url = 'https://rate.bot.com.tw/xrt?Lang=zh-TW'
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')

    # 明確指定台灣銀行官方時間（也可擴充為自動擷取）
    twb_time = "2025/06/05 03:02"

    rows = soup.select('table.table tbody tr')
    for row in rows:
        if 'USD' in row.text:
            cols = row.find_all('td')
            cash_buy = float(cols[1].text.strip())
            cash_sell = float(cols[2].text.strip())
            spot_buy = float(cols[3].text.strip())
            spot_sell = float(cols[4].text.strip())
            spot_avg = round((spot_buy + spot_sell) / 2, 3)

            # 擷取中國銀行資料
            boc_cash_buy, boc_cash_sell, boc_time = get_boc_usd_cash_rates()
            boc_avg = round((boc_cash_buy + boc_cash_sell) / 2, 3)

            # 衍生匯率計算
            t_u = round(spot_avg * 1.02, 3)
            u_t = round(spot_avg * 0.98, 3)
            r_u = round(boc_avg * 1.022, 3)

            # 輸出格式
            return (
                f"【台灣銀行美金匯率】\n"
                f"買入：{cash_buy:.2f}　 {spot_buy:.2f}\n"
                f"賣出：{cash_sell:.2f}　 {spot_sell:.2f}\n"
                f"資料時間：{twb_time}\n\n"
                f"【中國銀行美金匯率】\n"
                f"買入：{boc_cash_buy:.2f}\n"
                f"賣出：{boc_cash_sell:.2f}\n"
                f"資料時間：{boc_time}\n\n"
                f"===============\n"
                f"新台幣-USDT：{t_u}\n"
                f"USDT-新台幣：{u_t}\n"
                f"人民幣-USDT：{r_u}\n"
                f"===============\n"
                f"「本匯率僅供參考，非絕對」"
            )

def send_to_telegram(text):
    token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {'chat_id': chat_id, 'text': text}
    res = requests.post(url, data=payload)
    if res.status_code != 200:
        print(f"⚠️ 發送失敗：{res.text}")

if __name__ == "__main__":
    try:
        msg = get_usd_rate()
        if msg:
            print(msg)
            send_to_telegram(msg)
        else:
            print("⚠️ 匯率資料抓取失敗")
    except Exception as e:
        print(f"⚠️ 發生錯誤：{e}")
