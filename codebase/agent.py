"""Workflow mô phỏng hỗ trợ học viên AI20K L3A."""
import re
import unicodedata
from datetime import date, timedelta

from tools import lookup_lab_sessions, search_lab_announcements
from tracing import note

BRANCHES = {
    "answer_with_sources": "Nhánh 1 — Trả lời kèm nguồn",
    "ask_clarification": "Nhánh 2 — Hỏi thêm",
    "draft_handoff": "Nhánh 3 — Chuẩn bị chuyển câu hỏi",
}

DEMO_DATE = date(2026, 11, 27)
LAB_ALIASES = {"10": "LAB-DEMO-01"}  # Bí danh duy nhất để chạy lại các câu demo ban đầu.
LAB_REFERENCE = re.compile(r"\blab demo (\d+)\b|\blab (?:so )?(\d+)\b")
ROOM_REFERENCE = re.compile(r"\bh (\d{3})\b")
SHIFTS = {"sang": "sáng", "chieu": "chiều", "toi": "tối"}
HACKATHON_TOPICS = {"hackathon_repo", "checkpoint"}


def _normalize(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text.casefold().replace("đ", "d"))
    unaccented = "".join(char for char in decomposed if not unicodedata.combining(char))
    return " ".join(re.findall(r"[a-z]+|[0-9]+", unaccented))


def _numeric_lab_id(number: str) -> str:
    number = number.lstrip("0") or "0"
    return LAB_ALIASES.get(number, f"Lab {number}")


def _topic(query: str) -> str | None:
    if re.search(r"\b(?:lab|tai lieu|huong dan|lms)\b", query) and re.search(
        r"\b(?:(?:khong|chua) (?:the )?(?:truy cap|vao duoc|mo duoc|xem duoc|tai duoc)|"
        r"(?:truy cap|vao|mo|tai) khong duoc|bi chan|loi (?:khi )?truy cap|"
        r"(?:thieu|khong co|bi tu choi) quyen)\b",
        query,
    ):
        return "access"
    if re.search(r"\b(?:han nop|deadline|thoi han|(?:khi nao|bao gio|may gio) nop)\b", query) or re.search(
        r"\bnop\b.*\b(?:khi nao|luc nao|may gio|bao gio)\b", query
    ):
        if re.search(r"\b(?:cp|checkpoint) 2\b", query) and not re.search(r"\blab\b", query):
            return "checkpoint"
        return "deadline"
    if re.search(r"\b(?:dat ten|ten (?:repo|repository)|(?:repo|repository) (?:dat )?ten)\b", query):
        if re.search(r"\b(?:hackathon|day 15)\b", query) and not re.search(r"\blab\b", query):
            return "hackathon_repo"
        return "repo_naming"
    if re.search(r"\b(?:lms|xem huong dan|xem tren|tai lieu|de bai|github chuong trinh)\b", query):
        return "portal"
    return None


def _session_date(text: str, query: str) -> str | None:
    explicit = re.search(r"(?<!\d)(\d{1,2})/(\d{1,2})(?:/(\d{4}))?(?![\d/])", text)
    if explicit:
        day, month, year = explicit.groups()
        return date(int(year) if year else DEMO_DATE.year, int(month), int(day)).isoformat()
    relative = re.search(r"\b(?:hom|sang|chieu|toi|ngay) (qua|nay|mai)\b", query)
    if relative:
        offset = {"qua": -1, "nay": 0, "mai": 1}[relative[1]]
        return (DEMO_DATE + timedelta(days=offset)).isoformat()
    return None


def _result(decision: str, reason: str, message: str, **details) -> dict:
    label = BRANCHES[decision]
    note(f"{label}. Lý do: {reason}")
    return {
        "output": f"[Bản mock L3A]\n{label}\nLý do: {reason}\n\n{message}",
        "decision": decision,
        "decision_reason": reason,
        **details,
    }


def _clarify(reason: str, message: str, **context) -> dict:
    return _result("ask_clarification", reason, message, clarification=context)


def _answer_from_faq(source: dict) -> dict:
    code = source["code"]
    scope = source["applies_to"]
    source_label = "Nguồn demo" if source["synthetic"] else "Nguồn"
    return _result(
        "answer_with_sources",
        f"FAQ {code} khớp nội dung và phạm vi câu hỏi.",
        f'{source["text"]}\nPhạm vi: {scope}\n{source_label}: {code} · {source["url"]}',
        citations=[source],
    )


def _prepare_handoff(question: str, reason: str, sessions: list) -> dict:
    if len(sessions) != 1:
        missing = (
            "Lịch demo chưa có ca khớp với thông tin bạn cung cấp."
            if not sessions else "Lịch demo có nhiều ca phù hợp, chưa xác định được ca cần hỗ trợ."
        )
        return _result("draft_handoff", f"{reason} {missing}", "Chưa xác minh được người phụ trách ca lab.")

    session = sessions[0]
    session_day = date.fromisoformat(session["date"]).strftime("%d/%m/%Y")
    shift = f'Ca {session["shift"]} ngày {session_day}'
    session_label = f'{session["session"]} · {shift} · Phòng {session["room"]}'
    if session["status"] != "assigned" or not session.get("coach"):
        return _result(
            "draft_handoff",
            f'{reason} Lịch {session["code"]} có ca nhưng chưa xác nhận coach.',
            f"{session_label}\nChưa xác minh được người phụ trách.",
        )

    draft = {
        "question": question,
        "lab_id": session["session"],
        "session": shift,
        "room": session["room"],
        "assignee": session["coach"],
        "roster_code": session["code"],
        "status": "pending_approval",
    }
    return _result(
        "draft_handoff",
        f'{reason} Lịch {draft["roster_code"]} xác nhận coach cho ca và phòng lab.',
        f'Bản nháp chờ điều phối viên duyệt\nCâu hỏi: {draft["question"]}\n'
        f'Ca lab: {session_label}\nNgười phụ trách: {draft["assignee"]} (demo)',
        draft_handoff=draft,
    )


def answer(text: str, *, clarification: dict | None = None) -> dict:
    """Trả kết quả cho một câu hỏi hoặc dữ kiện bổ sung sau lượt hỏi thêm."""
    question = text.strip()
    query = _normalize(question)
    topic = _topic(query)
    lab_ids = {
        f"LAB-DEMO-{demo_number}" if demo_number else _numeric_lab_id(lab_number)
        for demo_number, lab_number in LAB_REFERENCE.findall(query)
    }
    rooms = {f"H{number}" for number in ROOM_REFERENCE.findall(query)}
    room = next(iter(rooms)) if len(rooms) == 1 else None
    try:
        session_date = _session_date(question, query)
    except ValueError:
        return _result("ask_clarification", "Ngày trong câu hỏi không hợp lệ.", "Bạn nhập lại ngày diễn ra ca lab nhé.")
    # Giữ dấu khi nhận diện buổi đứng riêng để phân biệt "tôi" với "tối".
    shifts = set(re.findall(r"\b(?:sáng|chiều|tối)\b", question.casefold()))
    unaccented_shifts = re.findall(r"\b(?:ca|buoi) (sang|chieu|toi)\b", query)
    unaccented_shifts.extend(re.findall(r"\b(sang|chieu|toi) (?:qua|nay|mai)\b", query))
    shifts.update(SHIFTS[word] for word in unaccented_shifts)
    shift = next(iter(shifts)) if len(shifts) == 1 else None

    if topic is None and clarification:
        bare_number = re.fullmatch(r"(\d+)(?: a)?", query)
        if bare_number and clarification["lab_id"] is None:
            lab_ids = {_numeric_lab_id(bare_number[1])}
        if lab_ids or session_date or shift or room:
            topic = clarification["topic"]
            if not lab_ids and clarification["lab_id"] is not None:
                lab_ids = {clarification["lab_id"]}
            session_date = session_date or clarification["session_date"]
            shift = shift or clarification["shift"]
            room = room or clarification["room"]
            question = f'{clarification["question"]}\nThông tin bổ sung: {question}'

    if topic is None:
        return _result(
            "ask_clarification",
            "Chưa xác định được thông tin lab bạn cần tra.",
            "Bạn muốn hỏi hạn nộp, cách đặt tên repo, nơi xem hướng dẫn hay sự cố truy cập?",
        )

    day = session_date or DEMO_DATE.isoformat()
    if topic in HACKATHON_TOPICS:
        sources = search_lab_announcements(None, topic, day, None)
        if len(sources) == 1:
            return _answer_from_faq(sources[0])
        return _result(
            "draft_handoff",
            "FAQ chưa có một nguồn chính thức phù hợp cho câu hỏi về hackathon Day 15.",
            "Chưa xác minh được thông tin để trả lời câu hỏi này.",
        )

    lab_id = next(iter(lab_ids)) if len(lab_ids) == 1 else None
    sessions = None
    if not lab_ids and shift and (topic == "portal" or room):
        sessions = lookup_lab_sessions(None, day, shift, room)
        scheduled_lab_ids = {session["session"] for session in sessions}
        if len(scheduled_lab_ids) == 1:
            lab_id = next(iter(scheduled_lab_ids))

    context = {
        "question": question,
        "topic": topic,
        "lab_id": lab_id,
        "session_date": session_date,
        "shift": shift,
        "room": room,
    }
    if lab_id is None:
        return _clarify(
            "Chưa xác định được lab để tra đúng FAQ và lịch.",
            "Bạn đang hỏi Lab số mấy? Bạn cũng có thể nhập mã lab, ví dụ LAB-DEMO-01.",
            **context,
        )
    if topic == "access" and (not session_date or not shift):
        if session_date:
            missing = "ca (sáng, chiều hay tối)"
        elif shift:
            missing = "ngày diễn ra ca"
        else:
            missing = "ngày và ca (sáng, chiều hay tối)"
        return _clarify(
            f"Cần biết {missing} để tra đúng lịch phụ trách.",
            f"Bạn cho mình biết {missing} bạn gặp sự cố được không?",
            **context,
        )

    sources = search_lab_announcements(lab_id, topic, day, shift)
    if len(sources) == 1:
        return _answer_from_faq(sources[0])

    if len(sources) > 1:
        reason = f"Có nhiều mục FAQ phù hợp cho nội dung này của {lab_id}."
    elif topic == "access":
        reason = f"FAQ chưa có hướng dẫn xử lý sự cố truy cập tài liệu {lab_id} cho ca bạn hỏi."
    else:
        reason = f"FAQ chưa có mục phù hợp với nội dung và phạm vi bạn hỏi về {lab_id}."

    if sessions is None:
        sessions = lookup_lab_sessions(lab_id, day, shift, room)
    if len(sessions) > 1 and not shift:
        return _clarify(f"{reason} Lịch có nhiều ca.", "Bạn đang hỏi ca sáng, chiều hay tối?", **context)
    if len(sessions) > 1 and not room:
        return _clarify(f"{reason} Lịch có nhiều phòng trong ca này.", "Bạn đang ở phòng nào?", **context)
    return _prepare_handoff(question, reason, sessions)
