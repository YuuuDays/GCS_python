# 1時間単位化・JST日付修正の確認用テスト(GitHub API / DB / メールには接続しない)
from datetime import datetime, timezone
import GetContributes as gc


def fix_now(monkeypatch, utc_dt):
    """GetContributes内の「現在時刻」をutc_dtに固定する"""
    class FixedDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return utc_dt if tz else utc_dt.replace(tzinfo=None)
    monkeypatch.setattr(gc, "datetime", FixedDatetime)


def run(monkeypatch, utc_dt, user_time, pushed_at):
    fix_now(monkeypatch, utc_dt)
    sent = []
    monkeypatch.setattr(gc, "fetch_github_repos", lambda name: [{"pushed_at": pushed_at}])
    monkeypatch.setattr(gc, "mail_sender_main", lambda mail, name: sent.append(mail))
    gc.get_contribute_main([{"git_name": "test", "time": user_time, "mail": "a@example.com"}])
    return len(sent)


# 23:00 JST(=14:00 UTC)起動、23時設定、今日pushなし → 1通送る
def test_23h_no_push_sends(monkeypatch):
    assert run(monkeypatch, datetime(2026, 11, 10, 14, 0, 5, tzinfo=timezone.utc), "23:00", "2026-11-09T10:00:00Z") == 1


# 0:00 JST起動では23時設定の人は対象外(24時のチェックは入らない)
def test_23h_not_checked_at_midnight(monkeypatch):
    assert run(monkeypatch, datetime(2026, 11, 10, 15, 0, 5, tzinfo=timezone.utc), "23:00", "2026-11-09T10:00:00Z") == 0


# 旧仕様の"21:30"登録ユーザーも21:00 JSTに通知される
def test_legacy_minutes_matched_by_hour(monkeypatch):
    assert run(monkeypatch, datetime(2026, 11, 10, 12, 0, 5, tzinfo=timezone.utc), "21:30", "2026-11-09T10:00:00Z") == 1


# 【修正C】11/10 7:00 JST起動、前日(11/09 JST)にpushだけ → 今日はpushなしなので送る
def test_early_morning_uses_jst_date(monkeypatch):
    assert run(monkeypatch, datetime(2026, 11, 9, 22, 0, 5, tzinfo=timezone.utc), "07:00", "2026-11-09T12:00:00Z") == 1


# 今日(JST)pushしていれば送らない
def test_pushed_today_no_mail(monkeypatch):
    assert run(monkeypatch, datetime(2026, 11, 10, 12, 0, 5, tzinfo=timezone.utc), "21:00", "2026-11-10T03:00:00Z") == 0
