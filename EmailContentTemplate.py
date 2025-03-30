# 概要:メール内容のテンプレート作成
import os
import random
from datetime import datetime
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

if os.getenv("K_SERVICE") is None:
    load_dotenv()

# メール構成内容テンプレート
def define_body(user_name):
    # ランダム要素とか持たせたいなぁ
    # 環境変数の取得
    frontend_path = os.getenv("FRONTEND_PATH")
    # ランダムなメッセージ
    messages = [
        "今日のコミット頑張りましょう!!",
        "プッシュを忘れずに！",
        "小さな一歩が大きな成果に！",
        "コードを書いたらこまめに保存しよう！",
        "千里の道も一歩から！！！今日から始めよう！"
    ]
    random_message = random.choice(messages)


    # メールの本文を作成
    body = (
        f"Gitへのpushがまだのようです！\n\n"
        f"{random_message}\n\n"
        f"メール停止の際はサイトにアクセスしてユーザ削除を行ってください\n"
        f"{frontend_path}"
    )
    return body

def define_subject():
    now_japan = datetime.now(ZoneInfo("Asia/Tokyo"))  # 日本時間の取得
    convert_japan = now_japan.strftime('%m/%d')  # MM/DD 形式の文字列に変換
    subject = f"本日({convert_japan})のあなたのGitContributeについて"
    return subject
