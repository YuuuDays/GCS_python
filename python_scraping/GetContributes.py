import requests

from mailSender import mail_sender_main
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta

# グローバル変数
global_today = ""


def fetch(url):
    try:
        response = requests.get(url)
        if response.status_code == 404:
            print(f"404エラー: {url} が見つかりません。")
            return None
        elif response.status_code != 200:
            print(f"HTTPエラー {response.status_code}: {url} の処理中にエラーが発生しました。")
            return None
        else:
            return response.text
    except requests.RequestException as e:
        print(f"HTTPエラー: {e}")
        return None


def scrape(user_name, user_time, user_mail):
    url = f"https://github.com/users/{user_name}/contributions"
    html = fetch(url)
    if html:
        soup = BeautifulSoup(html, "html.parser")
        scraping(soup, user_time, user_name, user_mail)
    # サーバーへの負荷を軽減するためのスリープ（必要に応じて）
    # time.sleep(1)


def round_to_nearest_30_minutes(dt):
    """ 現在の時間を30分単位に丸める関数 """
    minutes = dt.minute
    if minutes < 30:
        rounded_minutes = 0
    else:
        rounded_minutes = 30
    tmp_rounded_time = dt.replace(minute=rounded_minutes, second=0, microsecond=0)
    rounded_time = tmp_rounded_time.strftime('%H:%M')
    print(f"GetContributes.py実行時間: {rounded_time} (日本時間)")
    return rounded_time


def scraping(soup, user_time, user_name, user_mail):
    # 取得したuserのスクレイピング時間か判定
    now_time_judge = False
    # 現在のUTC時間を取得して30分単位に丸め、日本時間に変換
    current_time_utc = datetime.now(timezone.utc)
    current_time_japan = current_time_utc + timedelta(hours=9)  # 日本時間に変換
    current_time = round_to_nearest_30_minutes(current_time_japan)

    if user_time == current_time:
        print("userが設定した時刻と現在の時間が一致")
        print(f"処理を開始します->対象githubユーザー名:{user_name}")
        now_time_judge = True

    if now_time_judge:
        contributions = soup.find_all("td", class_="ContributionCalendar-day")
        found_today = False
        contribution_dates = []
        for day in contributions:
            count = int(day.get("data-level", 0))
            if count > 0:
                date = day.get("data-date")
                if date is not None:
                    date = date.strip()
                    contribution_dates.append(date)
        contribution_dates.sort()
        print("以下Contributeがある日付のみをソート表示:")
        for date in contribution_dates:
            print(f"{date}")
        for day in contributions:
            date = day.get("data-date")
            if date is not None:
                date = date.strip()
                if date == global_today:
                    count = int(day.get("data-level", 0))
                    if count > 0:
                        found_today = True
                    break
        if found_today:
            print(f"今日はコントリビューションがあります 日付: {global_today}")
        else:
            print(f"今日はコントリビューションがありません 日付: {global_today}")
            # メール送信処理
            mail_sender_main(user_mail)
    else:
        print("userが設定した時刻と現在の時間が不一致")
        print(f"現在の時間はメールは送信されませんでした ->対象githubユーザー名:{user_name}")
    print("------------------------------------------------")


def call_contributes(documents):
    for doc in documents:
        user_info = {
            'user_name': doc.get("git_name"),
            'user_time': doc.get("time"),
            'user_mail': doc.get("mail")
        }
        scrape(**user_info)  # 辞書をアンパックして関数に渡す


def get_contribute_main(documents):
    global global_today
    global_today = datetime.today().strftime('%Y-%m-%d')
    print(f"本日の日付は: {global_today}")
    call_contributes(documents)
