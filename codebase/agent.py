"""Luồng thử hỗ trợ học viên trong thread của một phòng lab."""

import json
import re
import unicodedata
from datetime import date, timedelta

from ai import call_model, current_provider
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
URL_PATTERN = re.compile(r"https?://[^\s)\]>\"']+")
TIME_REFERENCE = re.compile(
    r"(?i)(?<![a-z0-9])(\d{1,2})\s*(?::([0-5]\d)|[hg]([0-5]\d)?|giờ(?:\s*([0-5]\d))?)(?:\s*(sáng|chiều|tối))?\b"
)
REPO_REFERENCE = re.compile(r"\bK\d+(?:-[A-Za-z0-9_]+)+\b")
EXACT_DATE_REFERENCE = re.compile(r"(?<!\d)\d{2}/\d{2}/\d{4}(?![\d/])")
SHIFTS = {"sang": "sáng", "chieu": "chiều", "toi": "tối"}
VALID_EVAL_ACTIONS = {
    "answer_with_sources",
    "conflicting_sources",
    "insufficient_sources",
    "ask_clarification",
    "refuse",
}

BRANCH_LABELS = {
    "answer_with_sources": "Nhánh 1 — Trả lời kèm nguồn",
    "ask_clarification": "Nhánh 2 — Hỏi thêm",
    "draft_handoff": "Nhánh 3 — Hỗ trợ tiếp trong thread",
    "refuse": "Từ chối yêu cầu vượt phạm vi",
}

SOURCE_EVAL_SYSTEM = """Bạn là bước đánh giá nguồn và chọn bước xử lý cho trợ lý hỗ trợ học viên AI20K trong thread phòng lab.
Chỉ dựa vào dữ liệu JSON đầu vào (ngữ cảnh thread hiện tại, câu hỏi và retrieved_sources.active / has_stale).
Tuyệt đối KHÔNG bịa ngày, giờ, link, tên repo, tên coach hoặc dữ kiện từ thread khác.

Chọn đúng một giá trị cho "action":
1. "answer_with_sources": Chỉ chọn khi retrieved_sources.active có nguồn rõ ràng, không mâu thuẫn và trả lời trực tiếp cho đúng bài lab, ngày và ca đang hỏi. Viết "reply" ngắn gọn bằng tiếng Việt, giữ nguyên chính xác giờ, ngày (dd/mm/YYYY), mẫu tên và link từ nguồn; liệt kê mã nguồn đã dùng vào "cited_codes".
2. "conflicting_sources": Chọn khi retrieved_sources.active có từ 2 nguồn trở lên nhưng thông tin mâu thuẫn nhau cho cùng ca đang hỏi. KHÔNG tự chọn một đáp án; nêu ngắn gọn điểm mâu thuẫn ở "reason" và liệt kê các mã vào "cited_codes".
3. "insufficient_sources": Chọn khi retrieved_sources.active rỗng hoặc không trả lời đúng câu hỏi/bài/ngày/ca đang hỏi (kể cả khi has_stale=true, nghĩa là nguồn chỉ áp dụng cho ngày hoặc ca khác). Viết "reason" ngắn gọn bằng tiếng Việt nêu cụ thể đang thiếu thông tin/nội dung gì (theo đúng câu hỏi, bài lab, ngày, ca) trong thread hiện tại (ghi rõ mã thread_id, vd: trong thread 3A-LAB-C302). Nếu has_stale=true, nêu rõ nguồn hiện có chỉ áp dụng cho ngày/ca khác và KHÔNG khẳng định thông tin của ca đang hỏi. Chỉ nhận xét về nguồn tin nhắn trong thread — KHÔNG tự kết luận là có hay không có coach vì hệ thống sẽ tra lịch ở bước kế tiếp.
4. "ask_clarification": Chỉ chọn khi câu hỏi còn chi tiết mơ hồ cần học viên làm rõ thêm mới đối chiếu được nguồn.
5. "refuse": Chỉ chọn khi câu hỏi thực chất nằm ngoài phạm vi hỗ trợ buổi lab hoặc yêu cầu thông tin nội bộ / ngoài thread hiện tại.

Chỉ trả về DUY NHẤT một JSON object hợp lệ gồm 4 khoá:
{"action": "...", "reason": "...", "cited_codes": ["..."], "reply": "..."}"""


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
    prefix = "[Mock CP2 · dữ liệu mẫu]" if current_provider() == "fake" else "[Trợ lý lab · dữ liệu mẫu]"
    return {"output": f"{prefix}\n{label}\n{message}", "decision": decision, **details}


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


def _extract_json_object(raw: str) -> dict | None:
    """Trích JSON object hợp lệ đầu tiên từ phản hồi của model."""
    text = (raw or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.IGNORECASE | re.DOTALL).strip()
    start = text.find("{")
    if start == -1:
        return None
    depth = 0
    in_string = False
    escaped = False
    for idx in range(start, len(text)):
        ch = text[idx]
        if escaped:
            escaped = False
            continue
        if ch == "\\" and in_string:
            escaped = True
            continue
        if ch == '"':
            in_string = not in_string
        elif not in_string:
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    try:
                        parsed = json.loads(text[start:idx + 1])
                        return parsed if isinstance(parsed, dict) else None
                    except ValueError:
                        return None
    return None


def _extract_urls(text: str) -> set[str]:
    return {match.group(0).rstrip(".,;:!?") for match in URL_PATTERN.finditer(text or "")}


def _extract_times(text: str) -> set[str]:
    times = set()
    for hour_s, m_colon, m_hg, m_gio, period in TIME_REFERENCE.findall(text or ""):
        hour = int(hour_s)
        minute = int(m_colon or m_hg or m_gio or 0)
        if period and period.casefold() in {"chiều", "tối"} and 1 <= hour <= 11:
            hour += 12
        if 0 <= hour <= 23 and 0 <= minute <= 59:
            times.add(f"{hour:02d}:{minute:02d}")
    return times


def _extract_dates(text: str) -> set[tuple[int, int, int | None]]:
    return {
        (int(day), int(month), int(year) if year else None)
        for day, month, year in DATE_REFERENCE.findall(text or "")
    }


def _extract_repos(text: str) -> set[str]:
    return set(REPO_REFERENCE.findall(text or ""))


def _collect_source_facts(sources_list: list[dict]) -> dict:
    combined = "\n".join(s.get("text", "") for s in sources_list)
    return {
        "urls": {s["source_url"] for s in sources_list if s.get("source_url")},
        "times": _extract_times(combined),
        "dates": _extract_dates(combined),
        "exact_dates": set(EXACT_DATE_REFERENCE.findall(combined)),
        "repos": _extract_repos(combined),
    }


def _dates_compatible(reply_dates: set[tuple[int, int, int | None]], allowed_dates: set[tuple[int, int, int | None]]) -> bool:
    for day, month, year in reply_dates:
        if not any(
            ad == day and am == month and (year is None or ay is None or year == ay)
            for ad, am, ay in allowed_dates
        ):
            return False
    return True


def _text_matches_sources(
    text: str,
    sources_list: list[dict],
    *,
    session_date: str | None = None,
    require_all_times: bool = False,
    require_exact_official: bool = False,
    topic: str | None = None,
) -> bool:
    """Kiểm tra câu model viết có khớp hoàn toàn mốc giờ, ngày, tên repo và link của nguồn đã tra hay không."""
    if not text or not sources_list:
        return False
    facts = _collect_source_facts(sources_list)
    reply_urls = _extract_urls(text)
    if reply_urls - facts["urls"]:
        return False
    reply_times = _extract_times(text)
    if reply_times - facts["times"]:
        return False
    if require_all_times and facts["times"] and not (facts["times"] <= reply_times):
        return False
    reply_dates = _extract_dates(text)
    allowed_dates = facts["dates"]
    if not allowed_dates and session_date:
        parsed_session = date.fromisoformat(session_date)
        allowed_dates = {(parsed_session.day, parsed_session.month, parsed_session.year)}
    if allowed_dates and not _dates_compatible(reply_dates, allowed_dates):
        return False
    if not allowed_dates and reply_dates:
        return False
    reply_repos = _extract_repos(text)
    if reply_repos - facts["repos"]:
        return False
    if topic == "ten_repo_lab" and facts["repos"] and not (facts["repos"] <= reply_repos):
        return False
    if require_exact_official:
        if topic == "han_nop_lab" and any(t not in text for t in facts["times"]):
            return False
        if facts["exact_dates"] and not any(ed in text for ed in facts["exact_dates"]):
            return False
    return True


def _reason_matches_insufficient(reason: str, session_date: str, active: list[dict]) -> bool:
    """Chặn model đưa URL, mốc giờ hoặc tên repo chưa kiểm chứng vào lý do thiếu nguồn."""
    if not reason:
        return False
    allowed_urls = {s["source_url"] for s in active if s.get("source_url")}
    if _extract_urls(reason) - allowed_urls:
        return False
    if not active:
        if _extract_times(reason) or _extract_repos(reason):
            return False
        parsed_session = date.fromisoformat(session_date)
        allowed_dates = {(parsed_session.day, parsed_session.month, parsed_session.year)}
        if not _dates_compatible(_extract_dates(reason), allowed_dates):
            return False
    return True


def _is_valid_eval_payload(parsed: object) -> bool:
    """Kiểm tra chặt chẽ kiểu dữ liệu JSON trả về từ model trước khi xử lý."""
    if not isinstance(parsed, dict):
        return False
    action = parsed.get("action")
    if not isinstance(action, str) or action not in VALID_EVAL_ACTIONS:
        return False
    reply = parsed.get("reply", "")
    reason = parsed.get("reason", "")
    cited_codes = parsed.get("cited_codes", [])
    if not isinstance(reply, str) or not isinstance(reason, str):
        return False
    if not isinstance(cited_codes, list) or not all(isinstance(code, str) for code in cited_codes):
        return False
    return True


def _fallback_eval_decision(sources: dict, thread_id: str) -> dict:
    """Đánh giá nguồn theo quy tắc cố định khi ở chế độ fake hoặc cần dự phòng."""
    active = sources["active"]
    if len(active) == 1:
        source = active[0]
        return {
            "action": "answer_with_sources",
            "reason": f"Đã tìm thấy nguồn khớp ca hỏi trong thread {thread_id}.",
            "cited_codes": [source["code"]],
            "reply": source["text"],
        }
    if len(active) > 1:
        return {
            "action": "conflicting_sources",
            "reason": "Các nguồn còn mâu thuẫn, chưa xác định được thông báo thay thế.",
            "cited_codes": [s["code"] for s in active],
            "reply": "",
        }
    reason = (
        "Nguồn tìm được đã cũ hoặc thuộc ngày/ca khác. Chưa xác minh được thông tin của ca đang hỏi."
        if sources["has_stale"]
        else f"Chưa đủ căn cứ trong thread {thread_id}."
    )
    return {"action": "insufficient_sources", "reason": reason, "cited_codes": [], "reply": ""}


def _evaluate_sources(context: dict, room: str, sources: dict) -> dict:
    """Gọi model đánh giá các nguồn đã tra trong thread và chọn bước xử lý."""
    thread_id = context["thread_id"]
    payload = json.dumps(
        {
            "thread_id": thread_id,
            "room": room,
            "class": f"L{thread_id[:2]}",
            "lab_id": context["lab_id"],
            "session_date": context["session_date"],
            "shift": context["shift"],
            "topic": context["topic"],
            "student_question": _mask_contact(context["question"]),
            "retrieved_sources": {
                "active": sources["active"],
                "has_stale": sources["has_stale"],
            },
        },
        ensure_ascii=False,
        indent=2,
    )
    model_resp = call_model(SOURCE_EVAL_SYSTEM, payload)
    raw_text = model_resp.get("text", "")
    if not isinstance(raw_text, str):
        note("Phản hồi đánh giá nguồn sai kiểu — dùng quy tắc dự phòng")
        return _fallback_eval_decision(sources, thread_id)
    if model_resp.get("model") == "fake" or raw_text.startswith("[câu trả lời giả"):
        return _fallback_eval_decision(sources, thread_id)

    parsed = _extract_json_object(raw_text)
    if not _is_valid_eval_payload(parsed):
        note("Phản hồi đánh giá nguồn không hợp lệ hoặc sai kiểu — dùng quy tắc dự phòng")
        return _fallback_eval_decision(sources, thread_id)
    return parsed


def _apply_source_decision(context: dict, room: str, sources: dict, evaluated: dict) -> dict:
    """Thực thi bước xử lý đã chọn với kiểm tra kiểu dữ liệu, dữ kiện nguồn và lịch phân công."""
    thread_id = context["thread_id"]
    if not _is_valid_eval_payload(evaluated):
        note("Kiểu dữ liệu đánh giá nguồn không hợp lệ — dùng quy tắc dự phòng")
        evaluated = _fallback_eval_decision(sources, thread_id)

    lab_id = context["lab_id"]
    session_date = context["session_date"]
    shift = context["shift"]
    active = sources["active"]
    by_code = {s["code"]: s for s in active}

    action = evaluated.get("action")
    raw_reply = (evaluated.get("reply") or "").strip()
    raw_reason = (evaluated.get("reason") or "").strip()
    cited_codes = [c for c in (evaluated.get("cited_codes") or []) if c in by_code]

    if action == "refuse":
        safe_refuse = raw_reply if _reason_matches_insufficient(raw_reply, session_date, active) else ""
        return _result("refuse", safe_refuse or "Mình chỉ hỗ trợ câu hỏi về buổi lab trong thread này.")

    if action == "ask_clarification":
        safe_clarify = raw_reply if _reason_matches_insufficient(raw_reply, session_date, active) else ""
        return _clarify(context, safe_clarify or "Bạn nói rõ thêm chi tiết để mình kiểm tra lại trong thread nhé.")

    if action == "answer_with_sources" and not active:
        action = "insufficient_sources"
    elif action == "answer_with_sources" and len(active) > 1 and context["topic"] in {"han_nop_lab", "ten_repo_lab"}:
        action = "conflicting_sources"

    if action == "answer_with_sources":
        citations = [by_code[c] for c in cited_codes] or active[:1]
        is_official = context["topic"] in {"han_nop_lab", "ten_repo_lab"}
        if _text_matches_sources(
            raw_reply,
            citations,
            session_date=session_date,
            require_all_times=(context["topic"] == "han_nop_lab"),
            require_exact_official=is_official,
            topic=context["topic"],
        ):
            body = raw_reply
        else:
            note("Câu trả lời model lệch dữ kiện nguồn — dùng lại nội dung nguồn đã kiểm tra")
            body = "\n".join(s["text"] for s in citations)
        footer = "\n".join(
            f'Nguồn mẫu: {s["code"]} · {s["source_url"]}'
            if s["text"] in body
            else f'Nguồn mẫu: {s["code"]} ({s["text"]}) · {s["source_url"]}'
            for s in citations
            if s["source_url"] not in body or s["text"] not in body
        )
        message = body if not footer else f"{body}\n{footer}"
        return _result("answer_with_sources", message, citations=citations)

    if action == "conflicting_sources" and len(active) >= 2:
        summary_candidate = raw_reason or raw_reply
        if _text_matches_sources(summary_candidate, active, session_date=session_date, require_all_times=True, topic=context["topic"]):
            summary = summary_candidate
        else:
            note("Tóm tắt nguồn mâu thuẫn lệch dữ kiện — dùng tóm tắt chuẩn theo nguồn")
            summary = "Các nguồn còn mâu thuẫn, chưa xác định được thông báo thay thế."
        choices = "\n".join(f'- [{s["code"]}] {s["text"]} · {s["source_url"]}' for s in active)
        return _result(
            "draft_handoff",
            f"{summary}\n{choices}\nBạn có thể hỏi lại ngay trong thread này để xác nhận.",
            citations=active,
        )

    stale_note = "Nguồn tìm được đã cũ hoặc thuộc ngày/ca khác. Chưa xác minh được thông tin của ca đang hỏi."
    reason = raw_reason if _reason_matches_insufficient(raw_reason, session_date, active) else ""
    if not reason and raw_reason:
        note("Lý do thiếu nguồn chứa dữ kiện chưa kiểm chứng — thay bằng thông báo an toàn")
    if sources["has_stale"]:
        if not reason:
            reason = stale_note
        elif not any(tok in reason.casefold() for tok in ("ca khác", "ngày/ca khác", "không khớp", "chỉ áp dụng")):
            reason = f"{reason}\n{stale_note}"
    elif not reason:
        reason = f"Chưa đủ căn cứ trong thread {thread_id}."

    class_id = f"L{thread_id[:2]}"
    coaches = lookup_lab_coach(class_id, room, session_date, shift)
    if not coaches:
        return _result("draft_handoff", f"{reason}\nChưa xác minh được Lab Coach phụ trách phòng {room}. Bạn có thể tiếp tục hỏi trong thread {thread_id}.")

    handoff_reason = reason
    if "coach" in handoff_reason.casefold() and any(w in handoff_reason.casefold() for w in ("không có", "chưa có")):
        handoff_reason = f"Chưa có thông báo hoặc giải đáp sẵn cho vướng mắc này trong thread {thread_id}."

    draft = {
        "question": _mask_contact(context["question"]),
        "thread_id": thread_id,
        "lab_id": lab_id,
        "class": class_id,
        "room": room,
        "date": session_date,
        "shift": shift,
        "coaches": coaches,
        "reason": handoff_reason,
        "status": "pending_approval",
    }
    return _result(
        "draft_handoff",
        f"{handoff_reason}\nLab Coach mẫu: {', '.join(coaches)} · {class_id} · {room} · ca {shift} ngày "
        f"{date.fromisoformat(session_date):%d/%m/%Y}."
        f"\nCâu hỏi: {draft['question']}"
        "\nHọc viên chọn người và xác nhận tag mô phỏng. Chưa gửi tag.",
        draft_handoff=draft,
    )


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

    if re.search(
        r"\b(?:(?:danh sach|bang) phan cong noi bo|danh ba rieng|(?:so dien thoai|sdt|email|thong tin lien he) (?:rieng|ca nhan))\b",
        query,
    ):
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

    sources = search_lab_thread(thread_id, context["lab_id"], context["session_date"], context["shift"], context["topic"])
    evaluated = _evaluate_sources(context, room, sources)
    return _apply_source_decision(context, room, sources, evaluated)
