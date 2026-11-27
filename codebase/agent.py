"""Luồng chính của Trợ lý Hỗ trợ Buổi Lab L3A (Nhóm MergeConflict · Track A2).

Hợp đồng bắt buộc cho eval / simulate / app:
    answer(text: str, history: list | None = None) -> dict có khoá "output" (str)
    cùng các trường cấu trúc bổ sung (decision, citations, steps, clarifying_options,
    draft_handoff, model_mode) phục vụ giao diện web và kiểm chứng.

Luồng quyết định cố định có kiểm tra an toàn (workflow 3 quyết định):
    1. Chặn ngoài phạm vi / tấn công / đòi bịa số liệu hoặc tiết lộ bí mật (Lớp 3 & 4).
    2. Tra cứu kho thông báo (active & expired) và lịch phân công coach qua @tool.
    3. Nếu câu hỏi mơ hồ thiếu dữ kiện cốt lõi -> hỏi lại đúng điểm thiếu (Lớp 2).
    4. Nếu có nguồn active khớp rõ -> trả lời kèm mã nguồn [TB-...]/[HD-...], gọi @model_call.
    5. Nếu là lỗi kỹ thuật cần người trực hoặc nguồn đã hết hiệu lực -> tạo bản nháp chuyển
       coach trạng thái pending_approval chờ điều phối viên duyệt (không tự gửi).
"""
import re

from ai import call_model
from knowledge_store import normalize_vi
from tools import build_handoff_draft, lookup_coach_roster, search_lab_announcements
from tracing import note

SYSTEM = (
    "Bạn là Trợ lý Hỗ trợ Buổi Lab AI20K lớp L3A (Track A2). "
    "CHỈ trả lời dựa trên phần Căn cứ được cung cấp từ công cụ tra cứu. "
    "Luôn nêu rõ mã nguồn dạng [MÃ_NGUỒN] khi khẳng định hạn nộp, quy tắc repo hoặc kênh hỗ trợ. "
    "Không tự bịa thông tin, không tự gửi tin nhắn thay điều phối viên, không trả lời dựa trên thông báo đã hết hiệu lực."
)
MAX_STEPS = 4

_OUT_OF_SCOPE_PATTERNS = [
    r"\bapi[ _-]?key\b",
    r"\.env\b",
    r"system prompt",
    r"ignore (previous|all) instructions",
    r"bỏ qua (quy tắc|hướng dẫn)",
    r"bịa (phỏng vấn|trích dẫn|khảo sát|số liệu|data)",
    r"sửa (metric_spec|chuẩn đạt|run-\d+\.csv|expected)",
    r"tự gửi (tin|email|slack|zalo) luôn",
    r"chấm điểm hộ",
    r"\b(giá vàng|chứng khoán|thời tiết|kê đơn thuốc|bóng đá|xổ số)\b",
]

_ESCALATION_KEYWORDS = [
    "lỗi",
    "error",
    "conflict",
    "merge",
    "403",
    "401",
    "400",
    "429",
    "không push được",
    "push không được",
    "permission",
    "denied",
    "bị kẹt",
    "hỏi ai",
    "gặp coach",
    "nhờ coach",
    "liên hệ ai",
    "ai phụ trách",
    "đổi thành viên",
    "gia hạn",
    "điểm danh",
    "khẩn cấp",
    "không vào được",
    "mất quyền",
]

_RULE_ONLY_INDICATORS = [
    "hạn nộp",
    "mấy giờ",
    "đặt tên repo",
    "tên repo",
    "lms",
    "github chương trình",
    "xem hướng dẫn",
    "đề bài",
    "kênh hỗ trợ",
    "check",
    "teams.md",
    "nối model",
    "connect-model",
]

_VAGUE_STANDALONE = {
    "giúp với",
    "giup voi",
    "cứu",
    "cuu",
    "hỏi",
    "hoi",
    "hạn nộp",
    "han nop",
    "lỗi rồi",
    "loi roi",
    "không nộp được",
    "khong nop duoc",
    "hỏi ai",
    "hoi ai",
    "làm sao đây",
    "lam sao day",
    "sao vậy",
    "sao vay",
}


def _is_out_of_scope(text_norm: str, raw_text: str) -> str:
    raw_low = raw_text.lower()
    for pat in _OUT_OF_SCOPE_PATTERNS:
        if re.search(pat, raw_low) or re.search(pat, text_norm):
            return pat
    return ""


def _was_clarification_requested(history: list | None) -> bool:
    if not history:
        return False
    assistants = [m for m in history if isinstance(m, dict) and m.get("role") == "assistant"]
    return bool(assistants and assistants[-1].get("decision") == "ask_clarification")


def _build_effective_query(text: str, history: list | None) -> str:
    if not _was_clarification_requested(history):
        return text.strip()
    recent_user_turns = [
        str(m.get("content", "")).strip()
        for m in history[-4:]
        if isinstance(m, dict) and m.get("role") == "user" and str(m.get("content", "")).strip()
    ]
    if not recent_user_turns:
        return text.strip()
    prev = recent_user_turns[-1]
    if prev and prev != text.strip() and len(text.strip()) < 90:
        return prev + " — Bổ sung: " + text.strip()
    return text.strip()


def _detect_ambiguity(text: str, text_norm: str, active_matches: list, history: list | None) -> tuple[bool, list]:
    """Kiểm tra câu hỏi quá ngắn hoặc thiếu dữ kiện cốt lõi (Lớp 2)."""
    tokens = text_norm.split()
    if len(tokens) <= 1 and len(text.strip()) < 10:
        return True, [
            "Hạn nộp CP1 và CP2 hôm nay mấy giờ?",
            "Cách đặt tên repo chuẩn của lớp L3A?",
            "Em bị lỗi git push 403 thì cần hỏi ai?",
        ]

    # Nếu không phải lượt trả lời bổ sung cho câu hỏi làm rõ trước đó mà rơi vào mẫu mơ hồ kinh điển
    has_clarification_ctx = _was_clarification_requested(history)
    if not has_clarification_ctx and text_norm in _VAGUE_STANDALONE:
        if "han nop" in text_norm:
            return True, [
                "Hạn nộp CP1 và CP2 hôm nay (27/11) mấy giờ?",
                "Hạn nộp CP3 và CP4 ngày mai (28/11) mấy giờ?",
            ]
        if "loi" in text_norm or "khong nop" in text_norm:
            return True, [
                "Em bị lỗi HTTP 403 / conflict khi push GitHub",
                "Em bị lỗi HTTP 429 khi chạy eval API model",
                "Form nộp trên LMS không thấy link lớp L3A",
            ]
        return True, [
            "Hỏi hạn nộp các checkpoint hôm nay",
            "Hỏi quy tắc đặt tên repo L3A",
            "Cần chuyển Coach vì gặp lỗi kỹ thuật khi làm lab",
        ]

    if "loi" in tokens and len(tokens) <= 5 and not any(
        k in text_norm for k in ("403", "401", "400", "429", "git", "push", "conflict", "merge", "python", "api", "env", "lms", "teams")
    ):
        return True, [
            "Lỗi git push / merge conflict khi nộp bài",
            "Lỗi gọi model API (401 / 403 / 429) trong ai.py",
            "Lỗi `python run.py check` báo sai format TEAMS.md",
        ]

    if not active_matches and len(tokens) <= 3:
        return True, [
            "Hạn nộp bài lab hôm nay mấy giờ?",
            "Xem hướng dẫn lab chiều nay trên LMS hay GitHub?",
            "Tôi cần hỗ trợ kỹ thuật và chuyển coach trực ca",
        ]
    return False, []


def _needs_handoff(text_norm: str, active_matches: list, expired_matches: list) -> bool:
    has_escalation_intent = any(k in text_norm for k in _ESCALATION_KEYWORDS)
    has_rule_intent = any(k in text_norm for k in _RULE_ONLY_INDICATORS)

    # Nếu thông báo hết hiệu lực khớp mạnh hơn thông báo hiện hành (vd hỏi lịch Day 14 cũ) -> chặn dùng nguồn cũ & chuyển điều phối xác nhận
    top_active_score = active_matches[0].get("score", 0) if active_matches else 0
    top_expired_score = expired_matches[0].get("score", 0) if expired_matches else 0
    if expired_matches and top_expired_score > top_active_score:
        return True
    # Nếu học viên báo sự cố / lỗi thao tác hoặc xin gặp coach (trừ khi chỉ hỏi kênh hỗ trợ trong đề)
    if has_escalation_intent:
        if "kenh ho tro" in text_norm and active_matches and not any(
            err in text_norm for err in ("loi", "403", "401", "429", "conflict", "push", "khong vao", "nho coach", "gap coach")
        ):
            return False
        return True
    if not active_matches:
        return True
    if has_rule_intent and active_matches:
        return False
    return False


def _format_grounded_offline(active_matches: list, coach_info: dict, text_norm: str) -> str:
    top = active_matches[0]
    lines = [
        "**%s** (`%s`, cập nhật %s):" % (top["title"], top["code"], top["effective_date"]),
        top["summary"],
    ]
    for detail in top.get("details", [])[:3]:
        lines.append("- %s" % detail)

    # Chỉ ghép nguồn thứ hai khi thực sự liên quan cao
    if len(active_matches) > 1 and active_matches[1].get("score", 0) >= max(4.0, top.get("score", 0) * 0.65):
        second = active_matches[1]
        lines.append("")
        lines.append("**Bổ sung từ [`%s`] — %s:** %s" % (second["code"], second["title"], second["summary"]))

    if "kenh ho tro" in text_norm or "hoi ai" in text_norm or top.get("category") == "portal":
        coaches = coach_info.get("matched_coaches") or []
        if coaches:
            c0 = coaches[0]
            lines.append("")
            lines.append(
                "**Kênh & đầu mối hỗ trợ phù hợp:** %s (`%s`) · Kênh `%s` (%s)."
                % (c0["role_title"], c0["coach_id"], c0["channel"], c0["sla"])
            )

    lines.append("")
    lines.append("Nguồn đối chiếu: `[%s]` (%s)." % (top["code"], top["source_ref"]))
    return "\n".join(lines)


def answer(text: str, history: list | None = None) -> dict:
    """Xử lý một câu hỏi buổi lab L3A và trả về dict có khoá 'output' (str)."""
    raw_text = (text or "").strip()
    if not raw_text:
        note("dừng: đầu vào rỗng")
        return {
            "output": "Bạn vui lòng nhập câu hỏi cụ thể về buổi lab L3A (hạn nộp, đặt tên repo, tài liệu LMS/GitHub hoặc lỗi đang gặp).",
            "decision": "ask_clarification",
            "decision_label": "Chờ nhập câu hỏi",
            "steps": [
                {"label": "Nhận đầu vào", "status": "warn", "detail": "Chưa có nội dung câu hỏi"},
                {"label": "Tra nguồn", "status": "pending", "detail": "Chờ nội dung"},
                {"label": "Quyết định", "status": "pending", "detail": "Hỏi lại"},
            ],
            "citations": [],
            "clarifying_options": [
                "Bài lab hôm nay hạn nộp mấy giờ?",
                "Đặt tên repo nhóm L3A thế nào trước khi làm lab?",
                "Xem hướng dẫn lab chiều nay ở LMS hay GitHub chương trình?",
            ],
            "draft_handoff": None,
            "model_mode": "guard",
        }

    text_norm = normalize_vi(raw_text)

    # Bước 1: Kiểm tra rào chắn ngoài phạm vi / tấn công (Lớp 3 & 4)
    blocked_pat = _is_out_of_scope(text_norm, raw_text)
    if blocked_pat:
        note("dừng: từ chối ngoài phạm vi hoặc vi phạm quy tắc (%s)" % blocked_pat)
        refusal_text = (
            "Yêu cầu này nằm ngoài phạm vi hỗ trợ buổi lab L3A hoặc vi phạm nguyên tắc an toàn của hệ thống "
            "(không tiết lộ API key/`.env`, không bịa dữ liệu bằng chứng/benchmark, không sửa kết quả sau chốt và không tự gửi tin khi chưa qua điều phối duyệt).\n\n"
            "Nếu bạn đang gặp lỗi kỹ thuật thật khi cấu hình `.env` hoặc nộp bài, hãy mô tả lỗi cụ thể để mình tra tài liệu chính thức hoặc tạo bản nháp chuyển Coach trực ca."
        )
        return {
            "output": refusal_text,
            "decision": "refuse_out_of_scope",
            "decision_label": "Ngoài phạm vi · Đã chặn an toàn",
            "steps": [
                {"label": "Kiểm phạm vi", "status": "blocked", "detail": "Vi phạm ranh giới an toàn / ngoài phạm vi lab"},
                {"label": "Tra nguồn", "status": "skipped", "detail": "Không gọi công cụ gửi ngoài"},
                {"label": "Quyết định", "status": "blocked", "detail": "Từ chối & điều hướng an toàn"},
            ],
            "citations": [],
            "clarifying_options": [
                "Hướng dẫn nối model và cấu hình .env an toàn",
                "Quy tắc các mốc nộp bài Checkpoint Day 15",
            ],
            "draft_handoff": None,
            "model_mode": "policy_guard",
        }

    # Bước 2: Ghép ngữ cảnh hội thoại gần nhất và gọi các @tool tra cứu
    effective_query = _build_effective_query(raw_text, history)
    eff_norm = normalize_vi(effective_query)

    kb_result = search_lab_announcements(effective_query, include_expired=True)
    active_matches = kb_result.get("active_matches", [])
    expired_matches = kb_result.get("expired_matches", [])
    coach_result = lookup_coach_roster(effective_query)

    # Bước 3: Kiểm tra mơ hồ / thiếu thông tin (Lớp 2)
    is_ambiguous, quick_options = _detect_ambiguity(raw_text, text_norm, active_matches, history)
    if is_ambiguous:
        note("dừng: thiếu dữ kiện — hỏi lại học viên")
        clarify_text = (
            "Mình chưa rõ bạn đang hỏi mốc/sự cố nào của buổi lab L3A nên chưa thể chốt câu trả lời chính xác. "
            "Bạn chọn hoặc bổ sung nhanh một trong các ý dưới đây để mình tra đúng nguồn ngay:"
        )
        return {
            "output": clarify_text,
            "decision": "ask_clarification",
            "decision_label": "Hỏi lại để làm rõ",
            "steps": [
                {"label": "Tra nguồn & lịch", "status": "ok", "detail": "Đã kiểm %d thông báo" % kb_result.get("total_checked", 0)},
                {"label": "Kiểm dữ kiện", "status": "warn", "detail": "Thiếu bối cảnh mốc nộp hoặc mã lỗi"},
                {"label": "Quyết định", "status": "warn", "detail": "Hỏi lại học viên"},
            ],
            "citations": [],
            "clarifying_options": quick_options,
            "draft_handoff": None,
            "model_mode": "clarify_guard",
        }

    # Bước 4: Xác định trả lời có nguồn hay tạo bản nháp chuyển Coach (chờ điều phối duyệt)
    if _needs_handoff(eff_norm, active_matches, expired_matches):
        top_coach = (coach_result.get("matched_coaches") or [{}])[0]
        coach_id = top_coach.get("coach_id", "COORD-L3A")
        expired_dominant = bool(
            expired_matches and (not active_matches or expired_matches[0].get("score", 0) > active_matches[0].get("score", 0))
        )
        missing_ctx = ""
        if expired_dominant:
            missing_ctx = "Câu hỏi khớp thông báo hết hiệu lực [%s]; cần xác nhận nguồn mới nhất." % expired_matches[0]["code"]

        draft = build_handoff_draft(effective_query, coach_id, missing_ctx)
        context_lines = [
            "Coach đề xuất: %s (%s) · Kênh %s · %s"
            % (draft["coach_role"], draft["coach_id"], draft["channel"], draft["sla"])
        ]
        if active_matches:
            context_lines.append("Tài liệu liên quan [%s]: %s" % (active_matches[0]["code"], active_matches[0]["summary"]))
        if expired_matches:
            context_lines.append("Cảnh báo nguồn cũ [%s]: %s" % (expired_matches[0]["code"], expired_matches[0]["summary"]))

        reply = call_model(
            SYSTEM,
            "Tình huống cần tạo bản nháp chuyển coach cho điều phối duyệt.\nCăn cứ:\n%s\n\nCâu hỏi học viên:\n%s"
            % ("\n".join(context_lines), effective_query),
        )

        if reply["model"] == "fake" or not reply["text"].strip():
            model_mode = "offline_grounded"
            out_parts = []
            if expired_dominant:
                out_parts.append(
                    "Thông báo khớp nhất (`[%s]`) **đã hết hiệu lực** (%s) nên hệ thống không dùng làm căn cứ trả lời trực tiếp."
                    % (expired_matches[0]["code"], expired_matches[0]["effective_date"])
                )
            elif active_matches:
                out_parts.append(
                    "Tham khảo nhanh từ `[%s]`: %s" % (active_matches[0]["code"], active_matches[0]["summary"])
                )
            else:
                out_parts.append("Chưa có quy định cố định trong kho thông báo cho tình huống cụ thể này.")

            out_parts.append("")
            out_parts.append(
                "Đã tạo **bản nháp chuyển %s** (`%s` · kênh `%s`) ở trạng thái **chờ điều phối viên duyệt** — hệ thống không tự gửi ra ngoài."
                % (draft["coach_role"], draft["coach_id"], draft["channel"])
            )
            output_text = "\n".join(out_parts)
        else:
            model_mode = "live_llm"
            output_text = reply["text"].strip()

        ordered_cites = (expired_matches[:1] + active_matches[:1]) if expired_dominant else (active_matches[:1] + expired_matches[:1])
        citations = [
            {
                "code": m["code"],
                "title": m["title"],
                "status": m["status"],
                "effective_date": m["effective_date"],
                "source_ref": m["source_ref"],
                "summary": m["summary"],
                "details": m.get("details", []),
            }
            for m in ordered_cites
        ]
        note("dừng: tạo bản nháp chuyển %s (%s) chờ điều phối duyệt" % (draft["coach_id"], draft["draft_id"]))
        return {
            "output": output_text,
            "decision": "draft_handoff",
            "decision_label": "Nháp chuyển Coach · Chờ duyệt",
            "steps": [
                {"label": "Tra nguồn & lịch", "status": "ok", "detail": "Đã đối chiếu kho thông báo & lịch trực"},
                {"label": "Kiểm dữ kiện", "status": "warn", "detail": "Cần Coach / điều phối xử lý trực tiếp"},
                {"label": "Quyết định", "status": "warn", "detail": "Tạo bản nháp %s chờ duyệt" % draft["draft_id"]},
            ],
            "citations": citations,
            "clarifying_options": [],
            "draft_handoff": draft,
            "model_mode": model_mode,
        }

    # Bước 5: Trả lời trực tiếp kèm nguồn đang hiệu lực
    context_blocks = []
    for m in active_matches[:2]:
        block = "[%s | %s | hiệu lực %s]\n%s\nChi tiết: %s" % (
            m["code"],
            m["title"],
            m["effective_date"],
            m["summary"],
            " ; ".join(m.get("details", [])),
        )
        context_blocks.append(block)
    coaches = coach_result.get("matched_coaches") or []
    if coaches:
        c0 = coaches[0]
        context_blocks.append("[COACH: %s | %s | Kênh %s | %s]" % (c0["coach_id"], c0["role_title"], c0["channel"], c0["sla"]))

    reply = call_model(
        SYSTEM,
        "Căn cứ chính thức:\n%s\n\nCâu hỏi của học viên L3A:\n%s" % ("\n\n".join(context_blocks), effective_query),
    )

    if reply["model"] == "fake" or not reply["text"].strip():
        model_mode = "offline_grounded"
        output_text = _format_grounded_offline(active_matches, coach_result, eff_norm)
    else:
        model_mode = "live_llm"
        output_text = reply["text"].strip()
        # Bảo đảm mã nguồn luôn xuất hiện rõ trong câu trả lời nếu model quên ghi
        top_code = active_matches[0]["code"]
        if top_code not in output_text:
            output_text += "\n\nNguồn đối chiếu: `[%s]`." % top_code

    top_score = active_matches[0].get("score", 0) if active_matches else 0
    relevant_extras = [m for m in active_matches[1:2] if m.get("score", 0) >= max(4.0, top_score * 0.65)]
    citations = [
        {
            "code": m["code"],
            "title": m["title"],
            "status": m["status"],
            "effective_date": m["effective_date"],
            "source_ref": m["source_ref"],
            "summary": m["summary"],
            "details": m.get("details", []),
        }
        for m in ([active_matches[0]] + relevant_extras)
    ]
    note("dừng: trả lời kèm %d nguồn hiệu lực (%s)" % (len(citations), ", ".join(c["code"] for c in citations)))
    return {
        "output": output_text,
        "decision": "answer_with_sources",
        "decision_label": "Trả lời kèm nguồn hiệu lực",
        "steps": [
            {"label": "Tra nguồn & lịch", "status": "ok", "detail": "Khớp %d nguồn đang hiệu lực" % len(active_matches)},
            {"label": "Kiểm dữ kiện", "status": "ok", "detail": "Đủ dữ kiện để trả lời"},
            {"label": "Quyết định", "status": "ok", "detail": "Trả lời kèm mã nguồn"},
        ],
        "citations": citations,
        "clarifying_options": [],
        "draft_handoff": None,
        "model_mode": model_mode,
    }
