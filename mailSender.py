import os
import smtplib
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from EmailContentTemplate import define_subject, define_body


def mail_sender_main(user_email):
    # .envファイル読み込み(ローカル用)
    load_dotenv()

    # 環境変数の取得
    sender_email = os.getenv("SENDER_EMAIL")
    password = os.getenv("PASSWORD_EMAIL")

    if sender_email and password:
        return mail_sender(sender_email, password, user_email)
    else:
        # エラーを表示する
        error_msg = "Error: Failed to get E-Mail or App Password"
        print(error_msg)
        return error_msg, 500


def mail_sender(sender_email, password, user_email):
    # メールの設定
    receiver_email = user_email

    body = 'Gitへのpushがまだのようです！'

    # メールメッセージの作成
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = define_subject()
    msg.attach(MIMEText(define_body(), 'plain'))

    # Gmailサーバーへの接続とメール送信
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()  # 暗号化された接続の開始
            server.login(sender_email, password)
            server.send_message(msg)
        print('メールが送信されました')
    except smtplib.SMTPAuthenticationError:
        error_msg = 'SMTP Authentication Error: Check your email and password.'
        print(error_msg)
        return error_msg, 500
    except Exception as e:
        error_msg = f'エラーが発生しました: {e}'
        print(error_msg)
        return error_msg, 500
