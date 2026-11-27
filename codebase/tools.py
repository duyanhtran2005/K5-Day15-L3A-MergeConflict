"""Công cụ tra cứu chỉ đọc dữ liệu mô phỏng của trợ lý lab L3A."""
import json
from pathlib import Path

from tracing import tool

MOCK_DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "mock_lab_support.json"


def load_mock_data() -> dict:
    return json.loads(MOCK_DATA_PATH.read_text(encoding="utf-8"))


@tool
def search_lab_announcements(lab_number: int, topic: str) -> dict:
    """Tra thông báo theo số lab và chủ đề, trả nguồn còn hiệu lực và mã nguồn hết hiệu lực.
    Không tác động ra ngoài.
    """
    data = load_mock_data()
    today = data["demo_date"]
    active = []
    inactive = []
    for announcement in data["announcements"]:
        if announcement["lab_number"] != lab_number or announcement["topic"] != topic:
            continue
        if announcement["effective_from"] <= today <= announcement["effective_through"]:
            active.append({**announcement, "url": MOCK_DATA_PATH.as_uri()})
        elif announcement["effective_through"] < today:
            inactive.append(announcement["code"])
    return {"active": active, "expired_codes": inactive}


@tool
def lookup_lab_sessions(lab_number: int | None, session_date: str | None, shift: str | None) -> list:
    """Tra lịch theo số lab, ngày ISO và buổi, trả các ca phù hợp cùng phân công.
    Không tác động ra ngoài.
    """
    return [
        session
        for session in load_mock_data()["sessions"]
        if (lab_number is None or session["lab_number"] == lab_number)
        and (session_date is None or session["date"] == session_date)
        and (shift is None or session["shift"] == shift)
    ]
