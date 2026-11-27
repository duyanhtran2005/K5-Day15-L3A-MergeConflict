"""Kho tri thức & hàng đợi bản nháp cho Track A2 (Cổng hỗ trợ Lab L3A).

Module sâu giấu toàn bộ logic nạp dữ liệu, chuẩn hoá tìm kiếm tiếng Việt không dấu,
kiểm tra hiệu lực nguồn và lưu trữ hàng đợi bản nháp chờ điều phối viên duyệt.
Các hàm truy vấn đều không gây tác động ra ngoài; chỉ hành động lưu hàng đợi từ UI
mới ghi file data/handoff_queue.json.
"""
import datetime
import json
import os
import re
import threading
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_KNOWLEDGE_PATH = os.path.join(ROOT, "data", "lab_knowledge.json")
DEFAULT_QUEUE_PATH = os.path.join(ROOT, "data", "handoff_queue.json")

_QUEUE_LOCK = threading.Lock()


def normalize_vi(text: str) -> str:
    """Chuẩn hoá chuỗi tiếng Việt về chữ thường không dấu để đối chiếu từ khoá ổn định."""
    if not text:
        return ""
    text = text.replace("đ", "d").replace("Đ", "D")
    decomposed = unicodedata.normalize("NFD", text)
    stripped = "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")
    cleaned = re.sub(r"[^a-z0-9.\-_/#]+", " ", stripped.lower())
    return " ".join(cleaned.split())


def tokenize_vi(text: str) -> list:
    norm = normalize_vi(text)
    return [tok for tok in norm.split() if len(tok) >= 2]


class LabKnowledgeStore:
    """Adapter đọc dữ liệu lab Track A2 và quản lý hàng đợi duyệt chuyển tiếp."""

    def __init__(self, knowledge_path: str = DEFAULT_KNOWLEDGE_PATH, queue_path: str = DEFAULT_QUEUE_PATH):
        self.knowledge_path = knowledge_path
        self.queue_path = queue_path

    def load_knowledge(self) -> dict:
        with open(self.knowledge_path, encoding="utf-8") as f:
            return json.load(f)

    def search_announcements(self, query: str, include_expired: bool = False) -> dict:
        """Tìm thông báo khớp nhất dựa trên độ phủ từ khoá và cụm từ trọng tâm."""
        data = self.load_knowledge()
        q_norm = normalize_vi(query)
        q_tokens = set(tokenize_vi(query))

        scored_active = []
        scored_expired = []

        for item in data.get("announcements", []):
            score = 0
            matched_terms = []

            for kw in item.get("keywords", []):
                kw_norm = normalize_vi(kw)
                if not kw_norm:
                    continue
                if kw_norm in q_norm:
                    score += 4 if " " in kw_norm else 2
                    matched_terms.append(kw)
                else:
                    kw_parts = set(tokenize_vi(kw_norm))
                    overlap = kw_parts & q_tokens
                    if overlap and len(overlap) == len(kw_parts):
                        score += 2
                        matched_terms.append(kw)

            title_tokens = set(tokenize_vi(item.get("title", "")))
            summary_tokens = set(tokenize_vi(item.get("summary", "")))
            title_overlap = q_tokens & title_tokens
            summary_overlap = q_tokens & summary_tokens
            score += len(title_overlap) * 1.5 + len(summary_overlap) * 0.6

            if score >= 2.0:
                enriched = dict(item)
                enriched["score"] = round(score, 2)
                enriched["matched_terms"] = matched_terms[:5]
                if item.get("status") == "active":
                    scored_active.append(enriched)
                elif include_expired:
                    scored_expired.append(enriched)

        scored_active.sort(key=lambda x: x["score"], reverse=True)
        scored_expired.sort(key=lambda x: x["score"], reverse=True)

        return {
            "active_matches": scored_active[:3],
            "expired_matches": scored_expired[:2],
            "total_checked": len(data.get("announcements", [])),
        }

    def match_coach(self, topic: str, shift: str = "") -> dict:
        """Tìm coach hoặc điều phối viên phù hợp nhất theo chủ đề vấn đề."""
        data = self.load_knowledge()
        t_norm = normalize_vi(topic + " " + shift)
        t_tokens = set(tokenize_vi(t_norm))

        ranked = []
        for coach in data.get("coach_roster", []):
            score = 0
            hits = []
            for kw in coach.get("topics", []):
                kw_norm = normalize_vi(kw)
                if kw_norm in t_norm:
                    score += 3
                    hits.append(kw)
                elif kw_norm in t_tokens:
                    score += 2
                    hits.append(kw)
            if score > 0:
                entry = dict(coach)
                entry["score"] = score
                entry["matched_topics"] = hits[:4]
                ranked.append(entry)

        ranked.sort(key=lambda x: x["score"], reverse=True)
        if not ranked:
            # Mặc định chuyển về Điều phối viên lớp L3A khi chưa rõ nhóm kỹ thuật nào phụ trách
            coord = next(
                (c for c in data.get("coach_roster", []) if c.get("coach_id") == "COORD-L3A"),
                (data.get("coach_roster") or [{}])[0],
            )
            if coord:
                fallback = dict(coord)
                fallback["score"] = 1
                fallback["matched_topics"] = ["mặc định điều phối lớp"]
                ranked = [fallback]

        return {
            "matched_coaches": ranked[:2],
            "fallback_channel": "#l3a-lab-support",
        }

    def _ensure_queue_unlocked(self) -> list:
        if os.path.exists(self.queue_path):
            try:
                with open(self.queue_path, encoding="utf-8") as f:
                    items = json.load(f)
                if isinstance(items, list):
                    return items
            except (OSError, json.JSONDecodeError):
                pass
        data = self.load_knowledge()
        seed_items = [dict(d) for d in data.get("initial_demo_drafts", [])]
        self._write_queue_unlocked(seed_items)
        return seed_items

    def _write_queue_unlocked(self, items: list) -> None:
        os.makedirs(os.path.dirname(self.queue_path), exist_ok=True)
        tmp_path = self.queue_path + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, self.queue_path)

    def list_drafts(self) -> list:
        with _QUEUE_LOCK:
            return self._ensure_queue_unlocked()

    def enqueue_draft(self, draft: dict) -> dict:
        """Lưu bản nháp mới vào hàng đợi duyệt điều phối (chỉ gọi từ tương tác người dùng trên UI)."""
        with _QUEUE_LOCK:
            items = self._ensure_queue_unlocked()
            # Tránh tạo trùng nếu cùng draft_id đã tồn tại
            if any(x.get("draft_id") == draft.get("draft_id") for x in items):
                return draft
            items.insert(0, draft)
            self._write_queue_unlocked(items)
            return draft

    def act_on_draft(self, draft_id: str, action: str, note: str = "", edited_message: str = "") -> dict:
        """Xử lý duyệt / yêu cầu bổ sung / từ chối một bản nháp chuyển tiếp."""
        valid_actions = {
            "approve": "approved",
            "request_info": "needs_info",
            "reject": "rejected",
            "reopen": "pending_approval",
        }
        if action not in valid_actions:
            raise ValueError("Hành động không hợp lệ: %s" % action)

        with _QUEUE_LOCK:
            items = self._ensure_queue_unlocked()
            target = None
            for item in items:
                if item.get("draft_id") == draft_id:
                    item["status"] = valid_actions[action]
                    if edited_message.strip():
                        item["draft_message"] = edited_message.strip()
                    if note.strip():
                        item["coordinator_note"] = note.strip()
                    item["reviewed_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                    target = dict(item)
                    break
            if target is None:
                raise KeyError("Không tìm thấy bản nháp %s" % draft_id)
            self._write_queue_unlocked(items)
            return {"updated": target, "queue": items}

    def reset_demo_queue(self) -> list:
        with _QUEUE_LOCK:
            data = self.load_knowledge()
            seed_items = [dict(d) for d in data.get("initial_demo_drafts", [])]
            self._write_queue_unlocked(seed_items)
            return seed_items


_DEFAULT_STORE = LabKnowledgeStore()


def get_store() -> LabKnowledgeStore:
    return _DEFAULT_STORE
