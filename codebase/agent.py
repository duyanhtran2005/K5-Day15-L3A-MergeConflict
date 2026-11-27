"""Workflow mô phỏng hỗ trợ học viên AI20K L3A. Không gọi model hoặc gửi tin."""
import re
import unicodedata
from datetime import date, timedelta

from tools import load_mock_data, lookup_lab_sessions, search_lab_announcements
from tracing import note

BRANCHES = {
    "answer_with_sources": "Nhánh 1 — Trả lời kèm nguồn",
    "ask_clarification": "Nhánh 2 — Hỏi thêm",
    "draft_handoff": "Nhánh 3 — Chuẩn bị chuyển câu hỏi",
}

LAB_NUMBER = re.compile(r"\blab\s+(?:so\s+)?(\d+)\b")
SHIFTS = {"sang": "sáng", "chieu": "chiều", "toi": "tối"}


def _normalize(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text.casefold().replace("đ", "d"))
    unaccented = "".join(char for char in decomposed if not unicodedata.combining(char))
    return " ".join(re.findall(r"[a-z]+|[0-9]+", unaccented))


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
        return "deadline"
    if re.search(r"\b(?:dat ten|ten (?:repo|repository)|(?:repo|repository) (?:dat )?ten)\b", query):
        return "repo_naming"
    if re.search(r"\b(?:lms|xem huong dan|xem tren|tai lieu|de bai|github chuong trinh)\b", query):
        return "portal"
    return None


def _session_date(text: str, query: str, today: date) -> str | None:
    explicit = re.search(r"(?<!\d)(\d{1,2})/(\d{1,2})(?:/(\d{4}))?(?![\d/])", text)
    if explicit:
        day, month, year = explicit.groups()
        try:
            return date(int(year) if year else today.year, int(month), int(day)).isoformat()
        except ValueError:
            return None
    relative = re.search(r"\b(?:hom|sang|chieu|toi|ngay) (qua|nay|mai)\b", query)
    if relative:
        offset = {"qua": -1, "nay": 0, "mai": 1}[relative[1]]
        return (today + timedelta(days=offset)).isoformat()
    return None


def _result(decision: str, reason: str, message: str, **details) -> dict:
    label = BRANCHES[decision]
    note(f"{label}. Lý do: {reason}")
    return {
        "output": f"[Bản mock · dữ liệu mẫu]\n{label}\nLý do: {reason}\n\n{message}",
        "decision": decision,
        "decision_reason": reason,
        **details,
    }


def _clarify(reason: str, message: str, **context) -> dict:
    return _result("ask_clarification", reason, message, clarification=context)


def _prepare_handoff(question: str, lab_number: int, topic: str, reason: str, sessions: list) -> dict:
    if len(sessions) != 1:
        missing = (
            "Lịch mẫu chưa có ca khớp với thông tin bạn cung cấp."
            if not sessions else "Lịch mẫu có nhiều ca phù hợp, chưa xác định được ca cần hỗ trợ."
        )
        return _result("draft_handoff", f"{reason} {missing}", "Chưa xác minh được người phụ trách ca lab.")

    session = sessions[0]
    session_day = date.fromisoformat(session["date"]).strftime("%d/%m/%Y")
    shift = f'Ca {session["shift"]} ngày {session_day} ({session["hours"]}, giờ Việt Nam)'
    assignment = session["assignments"].get(topic, {})
    if not assignment.get("confirmed") or not assignment.get("assignee"):
        return _result(
            "draft_handoff",
            f'{reason} Lịch {session["code"]} có ca nhưng chưa xác nhận phân công cho vấn đề này.',
            f"{shift} · Lab {lab_number}\nChưa xác minh được người phụ trách.",
        )

    draft = {
        "question": question,
        "lab_number": lab_number,
        "session": shift,
        "assignee": assignment["assignee"],
        "roster_code": session["code"],
        "status": "pending_approval",
    }
    return _result(
        "draft_handoff",
        f'{reason} Lịch {draft["roster_code"]} xác nhận người phụ trách đúng ca và vấn đề.',
        f'Bản nháp chờ điều phối viên duyệt\nCâu hỏi: {draft["question"]}\n'
        f'Ca lab: Lab {lab_number} · {shift}\nNgười phụ trách: {draft["assignee"]}',
        draft_handoff=draft,
    )


def answer(text: str, *, clarification: dict | None = None) -> dict:
    """Trả kết quả cho một câu hỏi hoặc dữ kiện bổ sung sau lượt hỏi thêm."""
    question = text.strip()
    query = _normalize(question)
    topic = _topic(query)
    lab_numbers = {int(number) for number in LAB_NUMBER.findall(query)}
    today = date.fromisoformat(load_mock_data()["demo_date"])
    session_date = _session_date(question, query, today)
    # Giữ dấu khi nhận diện buổi đứng riêng để phân biệt "tôi" với "tối".
    shifts = set(re.findall(r"\b(?:sáng|chiều|tối)\b", question.casefold()))
    unaccented_shifts = re.findall(r"\b(?:ca|buoi) (sang|chieu|toi)\b", query)
    unaccented_shifts.extend(re.findall(r"\b(sang|chieu|toi) (?:qua|nay|mai)\b", query))
    shifts.update(SHIFTS[word] for word in unaccented_shifts)
    shift = next(iter(shifts)) if len(shifts) == 1 else None

    if topic is None and clarification:
        bare_number = re.fullmatch(r"(\d+)(?: a)?", query)
        if bare_number and clarification["lab_number"] is None:
            lab_numbers = {int(bare_number[1])}
        if lab_numbers or session_date or shift:
            topic = clarification["topic"]
            if not lab_numbers and clarification["lab_number"] is not None:
                lab_numbers = {clarification["lab_number"]}
            session_date = session_date or clarification["session_date"]
            shift = shift or clarification["shift"]
            question = f'{clarification["question"]}\nThông tin bổ sung: {question}'

    if topic is None:
        return _result(
            "ask_clarification",
            "Chưa xác định được thông tin lab bạn cần tra.",
            "Bạn muốn hỏi hạn nộp, cách đặt tên repo, nơi xem hướng dẫn hay sự cố truy cập?",
        )

    lab_number = next(iter(lab_numbers)) if len(lab_numbers) == 1 else None
    sessions = None
    if topic == "portal" and session_date and not lab_numbers:
        sessions = lookup_lab_sessions(None, session_date, shift)
        if len(sessions) == 1:
            lab_number = sessions[0]["lab_number"]

    context = {
        "question": question,
        "topic": topic,
        "lab_number": lab_number,
        "session_date": session_date,
        "shift": shift,
    }
    if lab_number is None:
        return _clarify(
            "Chưa xác định được số lab để tra đúng thông báo và lịch.", "Bạn đang hỏi Lab số mấy?", **context
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

    sources = search_lab_announcements(lab_number, topic)
    if topic == "portal" and (session_date or shift) and sessions is None:
        sessions = lookup_lab_sessions(lab_number, session_date, shift)
    active = sources["active"]
    if len(active) == 1 and (sessions is None or sessions):
        source = active[0]
        effective = date.fromisoformat(source["effective_from"]).strftime("%d/%m/%Y")
        return _result(
            "answer_with_sources",
            f'Đã xác định Lab {lab_number} và thông báo mẫu {source["code"]} còn hiệu lực.',
            f'{source["answer"]}\nNguồn mẫu: {source["code"]} (hiệu lực từ {effective})\n'
            f'Link thông báo mẫu: {source["url"]}',
            citations=[source],
        )

    if sessions == []:
        reason = f"Cần xác định ca Lab {lab_number} để dùng đúng hướng dẫn về tài liệu."
    elif len(active) > 1:
        reason = f"Có nhiều thông báo còn hiệu lực cho cùng nội dung của Lab {lab_number}."
    elif sources["expired_codes"]:
        expired = ", ".join(sources["expired_codes"])
        reason = f"Thông báo {expired} đã hết hiệu lực."
    elif topic == "access":
        reason = f"Thông báo mẫu chưa có hướng dẫn xử lý sự cố truy cập tài liệu Lab {lab_number}."
    else:
        reason = f"Chưa có thông báo mẫu còn hiệu lực cho nội dung này của Lab {lab_number}."

    if sessions is None:
        sessions = lookup_lab_sessions(lab_number, session_date, shift)
    return _prepare_handoff(question, lab_number, topic, reason, sessions)
