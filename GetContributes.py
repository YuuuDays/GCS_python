import os
import requests
from mailSender import mail_sender_main
from datetime import datetime, timezone, timedelta

# グローバル変数
global_today = ""


# 概要:GitHubのデータを取得して、メールを送るか判定する
# @param documents ...DBから取得したUser情報
# @return
def get_contribute_main(documents):
    # 今日の日付
    global global_today
    # 今日の日付を日本時間で取得(サーバはUTCで動くため、+9hしないとJST0〜8時台に前日の日付になる)
    global_today = (datetime.now(timezone.utc) + timedelta(hours=9)).strftime('%Y-%m-%d')

    print(f"-----------★　本日の日付は: {global_today} ------------------")
    # 情報の取得
    users = get_user_repository(documents)

    # ユーザ数文,名前,通知時間,メールを取得
    for user_name, user_time, user_mail in users:
        # メールを送るか判定するフラグ(ユーザーごとにリセットする)
        need_to_send_mail = False

        # GitHub APIからリポジトリ情報(JSON形式)を取得
        repos = fetch_github_repos(user_name)

        # 　メール送信判定
        if repos:
            need_to_send_mail = should_send_mail(repos, user_time, user_name)
            print("------------------------------------------------")

        # メール送信
        if need_to_send_mail:
            mail_sender_main(user_mail, user_name)


# documentをタプル in listに入れる
def get_user_repository(documents):
    result = []
    for doc in documents:
        user_info = (
            doc.get("git_name"),
            doc.get("time"),
            doc.get("mail")
        )
        result.append(user_info)
    return result  # list[tuple]


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


# user情報からメールを送るか判断する
def should_send_mail(repos, user_time, user_name):
    # 取得したuserのスクレイピング時間か判定するフラグ
    now_time_judge = False
    # 今日のコミットがあるか
    has_today_commit = False

    # 現在のUTC時間を取得して日本時間に変換し、1時間単位に丸める
    current_time_utc = datetime.now(timezone.utc)
    current_time_japan = current_time_utc + timedelta(hours=9)  # 日本時間に変換

    print(f"[DEBUG] UTC時間: {current_time_utc.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"[DEBUG] 日本時間: {current_time_japan.strftime('%Y-%m-%d %H:%M:%S')}")

    current_hour = round_down_to_hour(current_time_japan)
    print(f"[DEBUG] 丸め後の時間: {current_hour}:00")

    # 通知は1時間単位。旧仕様(15分単位)で登録された"21:30"等も"時"だけで比較し、21時台に通知する
    if user_time and user_time.split(":")[0] == current_hour:
        print("userが設定した時刻と現在の時間が一致")
        print(f"処理を開始します->対象githubユーザー名:{user_name}")
        now_time_judge = True

    if now_time_judge:
        # 　ユーザの全てのリポジトリの更新履歴を取得
        for repo in repos:
            comparative_world_jp_dates = ""    # gitリポジトリは国際時間(日付)の為+9hする変数を保持
            pushed_date = None              # yyyy-mm-dd に成形された値を保持する変数

            # ユーザのレポジトリから最終更新日付を取得
            pushed_at = repo.get('pushed_at')

            if pushed_at:
                # UTCの文字列をdatetimeに変換
                utc_time = datetime.strptime(pushed_at, "%Y-%m-%dT%H:%M:%SZ")

                # 日本時間（UTC+9）
                japan_time  = utc_time + timedelta(hours=9)

                # "YYYY-MM-DD"形式に整形して返す
                comparative_world_jp_dates = japan_time .strftime("%Y-%m-%d")
                print(comparative_world_jp_dates)

            # ユーザのyyyy-mm-ddとuserの最新コミット日付と比較
            if comparative_world_jp_dates == global_today:
                has_today_commit = True
                print(f"本日のコミットはもうあります。")
                break
    else:
        print("userが設定した時刻と現在の時間が不一致")
        print(
            f"現在の時間はメールは送信されませんでした :対象githubユーザー名:\"{user_name}\",ユーザ設定時刻\"{user_time}\"")

    # メール送信判定(ユーザの通知時間が現在時刻と一致、かつ今日のコミットがない場合はTrue)
    if now_time_judge:
        if not has_today_commit:
            print(f"[DEBUG] ★メール送信を行います :対象githubユーザー名:\"{user_name}\",ユーザ設定時刻\"{user_time}\"")
            return True

    return False


def round_down_to_hour(dt):
    """ 現在の時間を1時間単位に丸める関数（切り捨て）。戻り値は"HH" """
    if dt.second > 0 or dt.microsecond > 0:
        # Schedulerの起動遅延で"10:59:59"等になった場合に備え、1分後の時間にしてから丸める
        dt = dt + timedelta(minutes=1)

    rounded_hour = dt.strftime('%H')
    print(f"GetContributes.py実行時間: {rounded_hour}:00 (日本時間)")
    return rounded_hour
