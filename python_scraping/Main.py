import functions_framework

from DataBaseModule import db_call, db_read
from GetContributes import get_contribute_main


@functions_framework.http
def run_batch(request):
    try:
        # DBに問い合わせ
        client, collection = db_call()

        if client is not None and collection is not None:
            # クエリでsortされたUser情報格納変数
            document_count, documents = db_read(collection)

            print(f"取得したドキュメントの数は: {document_count}")
            # 同期的スクレイピング実行
            get_contribute_main(documents)

            # DB閉じる
            client.close()

            # 成功を表示する
            return "Batch job completed successfully!", 200

        else:
            # エラーを表示する
            return "Error: Failed to connect to database", 500

    except Exception as e:
        # 例外を表示する
        return f"Exception occurred: {e}", 500
