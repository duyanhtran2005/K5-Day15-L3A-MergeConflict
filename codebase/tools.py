"""Tra cứu FAQ và lịch phân công của trợ lý lab L3A."""
import json
import os
import re
from datetime import date
from pathlib import Path
from typing import Any

from tracing import tool

DEFAULT_DATA_DIR = Path(__file__).resolve().parents[1] / "data"
FAQ_TOPICS = {
    "deadline": "han_nop_lab",
    "repo_naming": "ten_repo_lab",
    "portal": "huong_dan_lab",
    "access": "su_co_truy_cap_lab",
    "hackathon_repo": "ten_repo_hackathon",
    "checkpoint": "han_nop_checkpoint",
}
LAB_CODE = re.compile(r"\bLAB-DEMO-\d+\b", re.IGNORECASE)
SCOPE_DATE = re.compile(r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b")
SCOPE_SHIFT = re.compile(r"\b(?:buổi|ca)\s+(sáng|chiều|tối)\b", re.IGNORECASE)


def _read_json(filename: str) -> tuple[Any, Path]:
    directory = Path(os.environ.get("LAB_SUPPORT_DATA_DIR") or DEFAULT_DATA_DIR)
    path = (directory / filename).resolve()
    try:
        return json.loads(path.read_text(encoding="utf-8-sig")), path
    except FileNotFoundError as error:
        raise FileNotFoundError(
            f"Thiếu {filename}. Đặt tệp trong data/ hoặc trỏ LAB_SUPPORT_DATA_DIR tới thư mục chứa hai tệp demo."
        ) from error


def _applies_to_lab(scope: str, lab_id: str, session_date: str, shift: str | None) -> bool:
    if lab_id not in {code.upper() for code in LAB_CODE.findall(scope)}:
        return False
    if not re.search(r"\bL3A\b", scope, re.IGNORECASE):
        return False

    scoped_date = SCOPE_DATE.search(scope)
    if not scoped_date:
        return False
    day, month, year = (int(part) for part in scoped_date.groups())
    if date(year, month, day).isoformat() != session_date:
        return False

    scoped_shift = SCOPE_SHIFT.search(scope)
    return not (shift and scoped_shift and scoped_shift[1].casefold() != shift)


@tool
def search_lab_announcements(lab_id: str | None, topic: str, session_date: str, shift: str | None) -> list:
    """Tra FAQ theo mã lab, chủ đề, ngày ISO và ca. Trả các mục phù hợp có liên kết nguồn.
    Chỉ đọc tệp, không tác động ra ngoài.
    """
    entries, faq_path = _read_json("demo_faq.json")
    matches = []
    for entry in entries:
        if entry["topic"] != FAQ_TOPICS[topic]:
            continue
        if lab_id is not None:
            if not _applies_to_lab(entry["applies_to"], lab_id, session_date, shift):
                continue
        elif entry["source_type"] != "official" or not entry["source_url"]:
            continue

        url = entry["source_url"] or (faq_path.as_uri() if entry["synthetic"] else None)
        if url:
            matches.append({**entry, "url": url})
    return matches


@tool
def lookup_lab_sessions(
    lab_id: str | None, session_date: str, shift: str | None, room: str | None = None
) -> list:
    """Tra lịch L3A theo mã lab, ngày ISO, ca và phòng. Trả các phân công đúng phạm vi.
    Chỉ đọc tệp, không tác động ra ngoài.
    """
    schedule, _ = _read_json("demo_lab_schedule.json")
    return [
        assignment
        for assignment in schedule["assignments"]
        if assignment["class"] == "L3A"
        and assignment["date"] == session_date
        and (lab_id is None or assignment["session"] == lab_id)
        and (shift is None or assignment["shift"] == shift)
        and (room is None or assignment["room"] == room)
    ]
