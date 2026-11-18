# テスト共通の設定
import pytest

import GetContributes as gc

# 本物の関数を退避しておく(test_contributions.py で直接テストするため)
REAL_HAS_TODAY_CONTRIBUTIONS = gc.has_today_contributions


@pytest.fixture(autouse=True)
def no_contributions_by_default(monkeypatch):
    """ テスト中に本物のGitHub GraphQL APIへ接続しないよう、草は「無し」にしておく """
    monkeypatch.setattr(gc, "has_today_contributions", lambda user_name: False)
