"""Công cụ của bài toán Track A2 — Cổng hỗ trợ Lab L3A.

Mỗi công cụ gắn @tool để tracing.py tự ghi tên, input, output rút gọn, độ trễ và lỗi.
Mọi công cụ ở đây KHÔNG tự thực hiện tác động ra ngoài; thao tác chuyển coach chỉ tạo
bản nháp trạng thái pending_approval chờ điều phối viên duyệt.
"""
import datetime
import uuid

from knowledge_store import get_store
from tracing import tool, TOOLS  # noqa: F401


@tool
def search_lab_announcements(query: str, include_expired: bool = False) -> dict:
    """Tên: search_lab_announcements.
    Input: câu hỏi hoặc từ khoá cần tra (str), include_expired (bool).
    Output: dict gồm active_matches, expired_matches và total_checked từ kho thông báo L3A.
    Tác động ra ngoài: Không."""
    return get_store().search_announcements(query=query, include_expired=include_expired)


@tool
def lookup_coach_roster(topic: str, shift: str = "") -> dict:
    """Tên: lookup_coach_roster.
    Input: chủ đề cần hỗ trợ (str), ca trực tuỳ chọn (str).
    Output: dict gồm danh sách matched_coaches (mã, vai trò, kênh, SLA) và fallback_channel.
    Tác động ra ngoài: Không."""
    return get_store().match_coach(topic=topic, shift=shift)


@tool
def build_handoff_draft(question: str, coach_id: str, missing_context: str = "") -> dict:
    """Tên: build_handoff_draft.
    Input: câu hỏi học viên (str), mã coach/điều phối (str), ghi chú ngữ cảnh còn thiếu (str).
    Output: dict bản nháp chuyển coach ở trạng thái pending_approval.
    Tác động ra ngoài: Không — chỉ tạo bản nháp chờ điều phối viên duyệt, không tự gửi tin."""
    store = get_store()
    data = store.load_knowledge()
    roster = data.get("coach_roster", [])
    coach = next((c for c in roster if c.get("coach_id") == coach_id), None)
    if coach is None:
        coach = roster[-1] if roster else {
            "coach_id": "COORD-L3A",
            "role_title": "Điều phối viên lớp AI20K L3A",
            "channel": "#l3a-lab-support",
            "sla": "Chờ điều phối xác nhận",
        }

    short_id = "DRF-" + uuid.uuid4().hex[:6].upper()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    missing_note = (" | Lưu ý bổ sung: " + missing_context.strip()) if missing_context.strip() else ""
    draft_message = (
        "[L3A · Chờ điều phối duyệt] Học viên hỏi: \"%s\"%s. "
        "Đề xuất chuyển %s tại kênh %s để hỗ trợ kịp thời."
        % (question.strip()[:240], missing_note, coach.get("role_title"), coach.get("channel"))
    )

    return {
        "draft_id": short_id,
        "created_at": now_str,
        "question": question.strip(),
        "coach_id": coach.get("coach_id"),
        "coach_role": coach.get("role_title"),
        "channel": coach.get("channel"),
        "sla": coach.get("sla", ""),
        "reason": "Cần coach/điều phối hỗ trợ trực tiếp hoặc xác nhận thông tin ngoài bộ quy tắc hiện hành.",
        "draft_message": draft_message,
        "status": "pending_approval",
        "coordinator_note": "",
        "synthetic": False,
    }
