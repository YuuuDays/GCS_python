# 草(contributions)判定の併用に関するテスト(外部には接続しない)
from datetime import datetime, timezone

import GetContributes as gc
from conftest import REAL_HAS_TODAY_CONTRIBUTIONS
from test_hourly import fix_now

NOW_21_JST = datetime(2026, 11, 16, 12, 0, 5, tzinfo=timezone.utc)  # 2026/11/16 21:00 JST
USER = {"git_name": "test", "time": "21:00", "mail": "a@example.com"}


def run(monkeypatch, repos, has_contributions):
    fix_now(monkeypatch, NOW_21_JST)
    sent, checked = [], []
    monkeypatch.setattr(gc, "fetch_github_repos", lambda name: repos)
    monkeypatch.setattr(gc, "mail_sender_main", lambda mail, name: sent.append(name))

    def fake_contributions(name):
        checked.append(name)
        return has_contributions

    monkeypatch.setattr(gc, "has_today_contributions", fake_contributions)
    gc.get_contribute_main([USER])
    return sent, checked


# 公開リポジトリへのpushは無いが、今日の草がある(privateリポジトリでの作業など) → 送らない
def test_no_push_but_contributions_no_mail(monkeypatch):
    sent, _ = run(monkeypatch, [{"pushed_at": "2026-11-15T11:00:00Z"}], True)
    assert sent == []


# pushも草も無い → 送る
def test_no_push_no_contributions_sends(monkeypatch):
    sent, _ = run(monkeypatch, [{"pushed_at": "2026-11-15T11:00:00Z"}], False)
    assert sent == ["test"]


# 今日pushしていれば、草のAPIは呼ばない(API呼び出しを増やさない)
def test_pushed_today_skips_contributions_api(monkeypatch):
    sent, checked = run(monkeypatch, [{"pushed_at": "2026-11-16T03:00:00Z"}], False)
    assert sent == []
    assert checked == []


# 公開リポジトリが0件でも、pushなしとして草を確認し、草も無ければ送る
def test_no_public_repos_checks_contributions(monkeypatch):
    sent, checked = run(monkeypatch, [], False)
    assert checked == ["test"]
    assert sent == ["test"]


# ---- has_today_contributions 本体のテスト ----
class FakeResponse:
    def __init__(self, status_code, body):
        self.status_code = status_code
        self._body = body

    def json(self):
        return self._body


def call_real(monkeypatch, response):
    gc.global_today = "2026-11-16"
    called = {}

    def fake_post(url, headers=None, json=None, timeout=None):
        called["url"] = url
        called["variables"] = json["variables"]
        return response

    monkeypatch.setattr(gc.requests, "post", fake_post)
    return REAL_HAS_TODAY_CONTRIBUTIONS("octocat"), called


def body(total):
    return {"data": {"user": {"contributionsCollection": {"contributionCalendar": {"totalContributions": total}}}}}


# 日本時間の「今日」の0:00〜23:59を指定して問い合わせ、1件以上ならTrue
def test_contributions_query_uses_jst_today(monkeypatch):
    result, called = call_real(monkeypatch, FakeResponse(200, body(1)))
    assert result is True
    assert called["url"] == "https://api.github.com/graphql"
    assert called["variables"] == {
        "login": "octocat",
        "from": "2026-11-16T00:00:00+09:00",
        "to": "2026-11-16T23:59:59+09:00",
    }


def test_zero_contributions_is_false(monkeypatch):
    result, _ = call_real(monkeypatch, FakeResponse(200, body(0)))
    assert result is False


# 取得に失敗したら False(=pushのみで判定していた従来どおりの動き)
def test_http_error_is_false(monkeypatch):
    result, _ = call_real(monkeypatch, FakeResponse(401, {"message": "Bad credentials"}))
    assert result is False


def test_graphql_error_is_false(monkeypatch):
    result, _ = call_real(monkeypatch, FakeResponse(200, {"errors": [{"message": "Could not resolve to a User"}], "data": {"user": None}}))
    assert result is False
