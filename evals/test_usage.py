import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from usage import reserve_request, DemoLimit

def test_daily_limit_shared_by_distinct_sessions(tmp_path):
    path=tmp_path/'counter.sqlite3'
    for _ in range(2):
        reserve_request({}, path, now=1700000000, daily_limit=2)
    with pytest.raises(DemoLimit, match='daily'):
        reserve_request({}, path, now=1700000000, daily_limit=2)
    reserve_request({}, path, now=1700000000+86400, daily_limit=2)

def test_session_cooldown_and_count(tmp_path, monkeypatch):
    monkeypatch.setenv('SESSION_REQUEST_LIMIT', '2')
    state={}; path=tmp_path/'counter.sqlite3'
    reserve_request(state,path,now=100)
    with pytest.raises(DemoLimit, match='wait'):
        reserve_request(state,path,now=101)
    reserve_request(state,path,now=111)
    with pytest.raises(DemoLimit, match='session'):
        reserve_request(state,path,now=122)

def test_concurrent_visitors_cannot_exceed_cap(tmp_path):
    path=tmp_path/'counter.sqlite3'
    # Establish schema, then race requests from separate sessions.
    reserve_request({},path,now=100,daily_limit=5)
    def attempt(_):
        try:
            reserve_request({},path,now=100,daily_limit=5)
            return True
        except DemoLimit:
            return False
    with ThreadPoolExecutor(max_workers=8) as pool:
        assert sum(pool.map(attempt,range(15)))==4
