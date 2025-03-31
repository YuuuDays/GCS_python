import os
import requests
from mailSender import mail_sender_main
from datetime import datetime, timezone, timedelta

# グローバル変数
global_today = ""


def get_contribute_main(documents):
    global global_today
    global_today = datetime.today().strftime('%Y-%m-%d')  # 今日の日付を取得
    print(f"-----------★　本日の日付は: {global_today} ------------------")
    call_contributes(documents)


def call_contributes(documents):
    for doc in documents:
        user_info = {
            'user_name': doc.get("git_name"),
            'user_time': doc.get("time"),
            'user_mail': doc.get("mail")
        }
        scrape(**user_info)  # 辞書をアンパックして関数に渡す


def scrape(user_time, user_name, user_mail):
    # GitHub APIからリポジトリ情報を取得
    repos = fetch_github_repos(user_name)
    if repos:
        scraping(repos, user_time, user_name, user_mail)


def fetch_github_repos(user_name):
    """ GitHub APIからユーザーのリポジトリ情報を取得 """
    token = os.environ.get("GITHUB_TOKEN")  # GitHubのPersonal Access Token
    url = f"https://api.github.com/users/{user_name}/repos"

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 404:
            print(f"404エラー: {url} が見つかりません。")
            return None
        elif response.status_code != 200:
            print(f"HTTPエラー {response.status_code}: {url} の処理中にエラーが発生しました。")
            return None
        else:
            return response.json()  # JSON形式でデータを返す
    except requests.RequestException as e:
        print(f"HTTPエラー: {e}")
        return None


def scraping(repos, user_time, user_name, user_mail):
    # 取得したuserのスクレイピング時間か判定
    now_time_judge = False
    # 現在のUTC時間を取得して15分単位に丸め、日本時間に変換
    current_time_utc = datetime.now(timezone.utc)
    current_time_japan = current_time_utc + timedelta(hours=9)  # 日本時間に変換

    print(f"[DEBUG] UTC時間: {current_time_utc.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"[DEBUG] 日本時間: {current_time_japan.strftime('%Y-%m-%d %H:%M:%S')}")

    current_time = round_to_nearest_15_minutes(current_time_japan)
    print(f"[DEBUG] 丸め後の時間: {current_time}")

    if user_time == current_time:
        print("userが設定した時刻と現在の時間が一致")
        print(f"処理を開始します->対象githubユーザー名:{user_name}")
        now_time_judge = True

    if now_time_judge:
        found_today = False
        # リポジトリ情報を順に処理
        for repo in repos:
            pushed_at = repo.get('pushed_at')
            if pushed_at:
                pushed_date = pushed_at[:10]  # yyyy-mm-dd のみ抽出
                if pushed_date == global_today:
                    found_today = True
                    break  # 今日のプッシュがあったので、処理を終了

        if found_today:
            print(f"今日はリポジトリがプッシュされた日です 日付: {global_today}")
        else:
            print(f"★　メール送信を行います :対象githubユーザー名:\"{user_name}\",ユーザ設定時刻\"{user_time}\"")
            # メール送信処理
            mail_sender_main(user_mail,user_name)
    else:
        print("userが設定した時刻と現在の時間が不一致")
        print(f"現在の時間はメールは送信されませんでした :対象githubユーザー名:\"{user_name}\",ユーザ設定時刻\"{user_time}\"")
    print("------------------------------------------------")


def round_to_nearest_15_minutes(dt):
    """ 現在の時間を15分単位に丸める関数（切り捨て） """
    if dt.second > 0 or dt.microsecond > 0:
        # 秒単位のずれがあるなら、1分後の時間にしてから丸める
        dt = dt + timedelta(minutes=1)


    rounded_minutes = (dt.minute // 15) * 15  # 15分単位で切り捨て
    tmp_rounded_time = dt.replace(minute=rounded_minutes, second=0, microsecond=0)
    rounded_time = tmp_rounded_time.strftime('%H:%M')
    print(f"GetContributes.py実行時間: {rounded_time} (日本時間)")
    return rounded_time
