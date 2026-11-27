"""Luồng thử hỗ trợ học viên trong thread của một phòng lab."""

import re
import unicodedata
from datetime import date, timedelta

from tools import lookup_lab_coach, search_lab_thread
from tracing import note

DEMO_DATE = date(2026, 11, 27)
MOCK_LAB_YEAR = 2027
THREAD_HEADER = re.compile(r"^\[Thread:\s*(3[AB]-LAB-[A-Z]\d{3})\]\s*", re.IGNORECASE)
ROOM_CODE = re.compile(r"\b([a-z]) (\d{3})\b")
LAB_CODE = re.compile(r"\blab (?:so )?(?:(demo) )?(\d+)\b")
LAB_SCOPE = re.compile(r"\b(?:lab|bai thuc hanh|bai nay|de bai)\b")
DATE_REFERENCE = re.compile(r"(?<!\d)(\d{1,2})/(\d{1,2})(?:/(\d{4}))?(?![\d/])")
RELATIVE_DATE = re.compile(r"\b(?:hom|sang|chieu|toi|ngay) (qua|nay|mai)\b")
DETAIL_WORDS = re.compile(r"\b(?:ngay|ca|buoi|sang|chieu|toi|da|em|minh|hoi|la|a|nhe)\b")
SHIFTS = {"sang": "sáng", "chieu": "chiều", "toi": "tối"}

BRANCH_LABELS = {
    "answer_with_sources": "Nhánh 1 — Trả lời kèm nguồn",
    "ask_clarification": "Nhánh 2 — Hỏi thêm",
    "draft_handoff": "Nhánh 3 — Hỗ trợ tiếp trong thread",
    "refuse": "Từ chối yêu cầu vượt phạm vi",
}


def _normalize(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text.casefold().replace("đ", "d"))
    unaccented = "".join(char for char in decomposed if not unicodedata.combining(char))
    return " ".join(re.findall(r"[a-z]+|[0-9]+", unaccented))


def _topic(query: str) -> str | None:
    lab_context = LAB_SCOPE.search(query)
    if re.search(r"\b(?:tai lieu|lms|de bai|file lab|link bai|repo lab|lab coach)\b", query) and re.search(
        r"\b(?:khong|chua) (?:the )?(?:truy cap|mo duoc|xem duoc|vao duoc)\b|"
        r"\b(?:truy cap|mo|vao) khong duoc\b|\b(?:loi truy cap|nho lab coach)\b",
        query,
    ):
        return "su_co_truy_cap_lab"
    if re.search(r"\bhan nop(?: bai)?(?: voi| la| luc| khi| may| bao| a| nhe| vay| cua lab|$)\b", query) or (
        lab_context and re.search(r"\b(?:han nop|deadline|chot gio nao|chot may gio)\b|\bnop\b.*\b(?:khi nao|luc nao|may gio|bao gio)\b", query)
    ):
        return "han_nop_lab"
    if re.search(r"\b(?:repo|repository)\b", query) and re.search(r"\b(?:dat ten|ten repo|ten repository)\b", query):
        return "ten_repo_lab"
    if lab_context and re.search(r"\b(?:lms|huong dan|tai lieu|de bai|github)\b", query):
        return "huong_dan_lab"
    return None


def _session_date(text: str, query: str) -> str | None:
    explicit = DATE_REFERENCE.search(text)
    if explicit:
        day, month, year = explicit.groups()
        return date(int(year) if year else MOCK_LAB_YEAR, int(month), int(day)).isoformat()
    relative = RELATIVE_DATE.search(query)
    if relative:
        offset = {"qua": -1, "nay": 0, "mai": 1}[relative[1]]
        return (DEMO_DATE + timedelta(days=offset)).isoformat()
    return None


def _session_shift(text: str, query: str) -> str | None:
    lab_shifts = set(re.findall(r"\blab (?:so )?\d+ (?:ca |buoi )?(sang|chieu|toi)\b", query))
    if len(lab_shifts) == 1:
        return SHIFTS[lab_shifts.pop()]
    shifts = set(re.findall(r"\b(?:sáng|chiều|tối)\b", text.casefold()))
    explicit = re.findall(r"\b(?:ca|buoi) (sang|chieu|toi)\b", query)
    relative = re.findall(r"\b(sang|chieu|toi) (?:qua|nay|mai)\b", query)
    shifts.update(SHIFTS[word] for word in explicit + relative)
    bare = SHIFTS.get(query) if query in {"sang", "chieu"} or text.strip().casefold() == "tối" else None
    return next(iter(shifts)) if len(shifts) == 1 else bare if not shifts else None


def _result(decision: str, message: str, **details) -> dict:
    label = BRANCH_LABELS[decision]
    note(label)
    return {"output": f"[Mock CP2 · dữ liệu mẫu]\n{label}\n{message}", "decision": decision, **details}


def _clarify(context: dict, message: str) -> dict:
    return _result("ask_clarification", message, clarification=context)


def _lab_id(query: str, *, allow_number: bool) -> str | None:
    matches = {f"LAB-{'DEMO-' if demo else ''}{int(number):02d}" for demo, number in LAB_CODE.findall(query)}
    if len(matches) == 1:
        return matches.pop()
    if not matches and allow_number:
        number = re.fullmatch(r"(\d+)(?: a)?", query)
        if number:
            return f"LAB-{int(number[1]):02d}"
    return None


def _mask_contact(text: str) -> str:
    text = re.sub(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", "[đã ẩn email]", text)
    text = re.sub(r"\b0\d{9,10}\b", "[đã ẩn số liên hệ]", text)
    return re.sub(r"(?i)\b(?:token|mật khẩu|api[ _-]?key)\s*[:=]\s*\S+", "[đã ẩn thông tin nhạy cảm]", text)


def _is_detail_reply(question: str, query: str) -> bool:
    """Chỉ tiếp tục lượt cũ khi phần bổ sung gồm dữ kiện về bài hoặc ca."""
    if re.fullmatch(r"\d+(?: a)?", query):
        return True
    has_detail = DATE_REFERENCE.search(question) or RELATIVE_DATE.search(query) or LAB_CODE.search(query)
    if not has_detail and not _session_shift(question, query):
        return False
    remaining = _normalize(DATE_REFERENCE.sub(" ", question))
    remaining = LAB_CODE.sub(" ", RELATIVE_DATE.sub(" ", remaining))
    return not DETAIL_WORDS.sub(" ", remaining).strip()


def answer(text: str, *, clarification: dict | None = None) -> dict:
    """Nhận ngữ cảnh thread mô phỏng ở đầu input CLI/eval, tách riêng khỏi lời hỏi."""
    incoming = text.strip()
    header = THREAD_HEADER.match(incoming)
    current_thread = header[1].upper() if header else None
    previous = clarification or {}
    if current_thread and previous.get("thread_id") and current_thread != previous["thread_id"]:
        previous = {}
    thread_id = current_thread or previous.get("thread_id")
    question = incoming[header.end():] if header else incoming
    query = _normalize(question)

    if re.search(r"\b(?:(?:danh sach|bang) phan cong noi bo|danh ba rieng|so dien thoai rieng|email rieng)\b", query):
        return _result("refuse", "Thông tin nội bộ chỉ dành cho người có quyền. Bạn có thể hỏi qua thread lab dành cho học viên.")

    mentioned_rooms = {f"{letter.upper()}{number}" for letter, number in ROOM_CODE.findall(query)}
    room = thread_id.rsplit("-", 1)[-1] if thread_id else None
    if room and mentioned_rooms - {room}:
        return _result("refuse", f"Trợ lý chỉ tra trong thread {thread_id} (phòng {room}). Bạn có thể mở thread phòng cần hỏi.")

    topic = _topic(query)
    supplies_thread = current_thread and not previous.get("thread_id") and not question
    detail_only = _is_detail_reply(question, query)
    is_followup = bool(previous) and (supplies_thread or detail_only)
    if not topic and not is_followup:
        if LAB_SCOPE.search(query) and (detail_only or re.search(r"\b(?:hoi ve|thac mac|ho tro)\b", query)):
            return _result("ask_clarification", "Bạn cần hỏi gì về lab: hạn nộp, tên repo, hướng dẫn hay lỗi truy cập?")
        return _result("refuse", "Mình chỉ hỗ trợ câu hỏi về buổi lab trong thread này.")

    if not is_followup:
        previous = {}
    context = {
        "thread_id": thread_id,
        "question": previous.get("question") or question,
        "lab_id": _lab_id(query, allow_number=bool(previous)) or previous.get("lab_id"),
        "topic": topic or previous.get("topic"),
        "session_date": previous.get("session_date"),
        "shift": _session_shift(question, query) or previous.get("shift"),
    }
    try:
        context["session_date"] = _session_date(question, query) or previous.get("session_date")
    except ValueError:
        return _clarify(context, "Ngày bạn nhập không hợp lệ. Bạn cho mình ngày diễn ra ca lab nhé.")

    for key, prompt in (
        ("thread_id", "Bạn đang hỏi trong thread phòng lab nào? Trong bản mock, nhập ngữ cảnh [Thread: 3A-LAB-C302]."),
        ("lab_id", "Bạn đang hỏi bài Lab số mấy hoặc tên bài lab nào?"),
        ("session_date", "Bạn đang hỏi ca lab ngày nào?"),
        ("shift", "Bạn đang hỏi ca sáng, chiều hay tối?"),
        ("topic", "Bạn muốn hỏi hạn nộp, cách đặt tên repo, nơi xem hướng dẫn hay sự cố truy cập?"),
    ):
        if not context[key]:
            return _clarify(context, prompt)

    lab_id = context["lab_id"]
    session_date = context["session_date"]
    shift = context["shift"]
    sources = search_lab_thread(thread_id, lab_id, session_date, shift, context["topic"])
    active = sources["active"]
    if len(active) == 1:
        source = active[0]
        return _result("answer_with_sources", f'{source["text"]}\nNguồn mẫu: {source["code"]} · {source["source_url"]}',
                       citations=active)
    if len(active) > 1:
        choices = "\n".join(f'- {source["text"]} · {source["source_url"]}' for source in active)
        return _result("draft_handoff",
                       f"Các nguồn còn mâu thuẫn, chưa xác định được thông báo thay thế.\n{choices}"
                       "\nBạn có thể hỏi lại ngay trong thread này để xác nhận.",
                       citations=active)

    reason = ("Nguồn tìm được đã cũ hoặc thuộc ngày/ca khác. Chưa xác minh được thông tin của ca đang hỏi."
              if sources["has_stale"] else f"Chưa đủ căn cứ trong thread {thread_id}.")
    class_id = f"L{thread_id[:2]}"
    coaches = lookup_lab_coach(class_id, room, session_date, shift)
    if not coaches:
        return _result("draft_handoff", f"{reason}\nChưa xác minh được Lab Coach phụ trách phòng {room}. Bạn có thể tiếp tục hỏi trong thread này.")

    draft = {
        "question": _mask_contact(context["question"]),
        "thread_id": thread_id,
        "lab_id": lab_id,
        "class": class_id,
        "room": room,
        "date": session_date,
        "shift": shift,
        "coaches": coaches,
        "reason": reason,
        "status": "pending_approval",
    }
    return _result(
        "draft_handoff",
        f"{reason}\nLab Coach mẫu: {', '.join(coaches)} · {class_id} · {room} · ca {shift} ngày "
        f"{date.fromisoformat(session_date):%d/%m/%Y}."
        f"\nCâu hỏi: {draft['question']}"
        "\nHọc viên chọn người và xác nhận tag mô phỏng. Chưa gửi tag.",
        draft_handoff=draft,
    )
