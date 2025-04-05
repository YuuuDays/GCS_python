import os
from urllib.parse import quote_plus
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


# Cloud Run では `.env` を読まない
if os.getenv("K_SERVICE") is None:
    load_dotenv()


def read_environmental_variables():
    """環境変数を読み取って MongoDB の URI を作成"""
    username = os.environ.get("NAME")
    password = os.environ.get("PASSWORD")
    url_first = os.environ.get("URL_FIRST")
    url_second = os.environ.get("URL_SECOND")

    if not all([username, password, url_first, url_second]):
        raise ValueError("環境変数が正しく設定されていません")

    # ユーザー名とパスワードをエンコード
    encoded_username = quote_plus(username)
    encoded_password = quote_plus(password)

    # 接続URIを構築
    uri = f"{url_first}{encoded_username}:{encoded_password}{url_second}"
    print("★接続URI:", uri)
    return uri


def db_call():
    load_dotenv()
    uri = read_environmental_variables()
    # ↓DBサーバーにアクセスしているだけ
    client = MongoClient(uri, server_api=ServerApi('1'))
    # 指定された名前のdbにアクセス
    # 存在しない場合、仮想dbを作成しdataが挿入された時点で物理的なdbが作成される
    db_name = os.environ.get("DB_NAME")
    db = client[db_name]
    # コレクション(テーブル)へのアクセス
    table_name = os.environ.get("TABLE_NAME")
    collection = db[table_name]

    try:
        # 以下はadminデータBSに対してping コマンドを使用
        client.admin.command('ping')
        print("-- MongoDB に接続成功 --")
        return client, collection
    except Exception as e:
        print(e)
        # DB close
        client.close()
        return None, None


def db_read(collection):
    # 全てのドキュメントを取得
    documents = collection.find()

    # ドキュメントリスト作成
    docs_list = list(documents)

    # ドキュメントを表示
    for doc in docs_list:
        print(doc)

    # レコード数取得
    documents_count = len(docs_list)
    print(f"取得したドキュメントの数は: {documents_count}")
    # 特定の条件でドキュメントを取得
    # query = {"git_name": "YuuHikida"}
    # document = collection.find_one(query)

    print("【DBの値正常読み取れました】")
    return docs_list