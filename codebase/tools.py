"""Đọc tin nhắn và lịch phân công cục bộ cho bản mock CP2."""

import csv
import os
from pathlib import Path

from tracing import tool

DEFAULT_DATA_DIR = Path(__file__).resolve().parents[1] / "data"
SOURCE_KEYWORDS = {
    "han_nop_lab": ("nộp", "deadline"),
    "ten_repo_lab": ("tên repo", "tên repository"),
    "huong_dan_lab": ("hướng dẫn", "tài liệu", "lms"),
    "su_co_truy_cap_lab": ("lỗi truy cập", "không truy cập", "không mở được", "không vào được"),
}
OFFICIAL_TOPICS = {"han_nop_lab", "ten_repo_lab"}


def _read_rows(filename: str) -> list:
    directory = Path(os.environ.get("LAB_SUPPORT_DATA_DIR") or DEFAULT_DATA_DIR)
    with (directory / filename).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


@tool
def search_lab_thread(thread_id: str, lab_id: str, session_date: str, shift: str, topic: str) -> dict:
    """Input: thread, bài, ngày, ca và chủ đề. Output: nguồn cùng thread và cờ nguồn lệch ngày/ca.
    Chỉ đọc dữ liệu cục bộ, không tác động ra ngoài.
    """
    lab_label = lab_id.replace("-", " ")
    scoped = [
        row for row in _read_rows("lab_thread_messages.csv")
        if row["thread_id"] == thread_id
        and row["lab"] == lab_label
        and (topic not in OFFICIAL_TOPICS or row["source_status"] == "official")
        and any(keyword in row["text"].casefold() for keyword in SOURCE_KEYWORDS[topic])
    ]
    active = [
        {"code": row["message_id"], "text": row["text"], "source_url": row["url"]}
        for row in scoped
        if row["date"] == session_date and row["session"] == shift
        and row["url"] and row["source_status"] in {"official", "answered"}
    ]
    has_stale = any(
        row["date"] != session_date or row["session"] != shift or row["source_status"] == "expired"
        for row in scoped
    )
    return {"active": active, "has_stale": has_stale}


@tool
def lookup_lab_coach(class_id: str, room: str, session_date: str, shift: str) -> list:
    """Input: lớp, phòng, ngày và ca. Output: những coach có phân công xác nhận đúng phòng.
    Chỉ đọc lịch cục bộ, không tác động ra ngoài.
    """
    return sorted({
        row["coach"] for row in _read_rows("lab_coach_assignments.csv")
        if row["class"] == class_id and row["room"] == room
        and row["date"] == session_date and row["session"] == shift
        and row["room_status"] == "da_xac_nhan"
        and row["assignment_status"] == "xac_nhan_theo_phong" and row["coach"]
    })
