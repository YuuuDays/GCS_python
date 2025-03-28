# 概要:メール内容のテンプレート作成
import os
import random

from dotenv import load_dotenv

if os.getenv("K_SERVICE") is None:
    load_dotenv()

# メール構成内容テンプレート
def define_body():
    # ランダム要素とか持たせたいなぁ
    # 環境変数の取得
    frontend_path = os.getenv("FRONTEND_PATH")
    # ランダムなメッセージ
    messages = [
        "今日のコミット頑張りましょう!!",
        "プッシュを忘れずに！",
        "小さな一歩が大きな成果に！",
        "コードを書いたらこまめに保存しよう！"
        "千里の道も一歩から！！！"
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
    subject = '本日のあなたのGitContributeについて'
    return subject