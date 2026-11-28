"""Nối model — chỗ DUY NHẤT trong bản chạy thử gọi model AI. NHÓM VIẾT phần gọi model thật.

Hợp đồng (giữ nguyên để khung đo được token):
    call_model(system: str, user: str) -> dict với 4 khoá
        "text":       str   chữ model trả về
        "model":      str   tên model đã gọi (để tra giá ở bảng giá model)
        "tokens_in":  int   số token vào, lấy từ trường usage trong phản hồi API — KHÔNG ước lượng
        "tokens_out": int   số token ra, gồm cả token suy luận / suy nghĩ nếu API tính riêng
    @model_call (từ tracing.py) tự ghi mỗi lần gọi vào trace; agent.py gọi call_model bao nhiêu lần
    cũng được, khung tự cộng token.
    Lỗi gọi model (hết lượt, sai key, mất mạng): cứ để exception bay ra — khung ghi lỗi vào cột error.

Chế độ giả (mặc định khi .env chưa có MODEL_PROVIDER, hoặc MODEL_PROVIDER=fake):
    trả một câu giả cố định, model "fake", token 0 — để luồng chạy hết từ trước CP2 (guide bước 3.2).
    Lượt `run.py eval` / `run.py simulate` chạy bằng model giả KHÔNG được tính.

Nối model thật: điền .env (chép từ .env.example), rồi viết nhánh gọi API ở dưới theo docs/connect-model.md
(có ví dụ OpenAI, Claude, model chạy trên máy, và cách nối nhà cung cấp khác). Không dán API key vào file này.
"""
import json
import os
import urllib.error
import urllib.request

from tracing import model_call

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOW_RAW = False

URL_OPENAI = "https://api.openai.com/v1/chat/completions"
URL_CLAUDE = "https://api.anthropic.com/v1/messages"
URL_OLLAMA = "http://localhost:11434/api/chat"
URL_GEMINI_TMPL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


def load_env(path=os.path.join(ROOT, ".env")):
    """Đọc file .env (KEY=VALUE mỗi dòng) vào biến môi trường, không ghi đè biến đã có. Khung — không cần sửa."""
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_env()
MODEL_PROVIDER = (os.environ.get("MODEL_PROVIDER") or "fake").strip().lower()
MODEL_NAME = (os.environ.get("MODEL_NAME") or "").strip()
API_KEY = (os.environ.get("API_KEY") or "").strip()

PROVIDER_KEY_ENVS = {
    "openai": ("OPENAI_API_KEY",),
    "anthropic": ("ANTHROPIC_API_KEY",),
    "claude": ("ANTHROPIC_API_KEY",),
    "gemini": ("GEMINI_API_KEY", "GOOGLE_API_KEY"),
    "google": ("GEMINI_API_KEY", "GOOGLE_API_KEY"),
}


def current_provider() -> str:
    """Trả về MODEL_PROVIDER đang kích hoạt theo biến môi trường / .env."""
    return (os.environ.get("MODEL_PROVIDER") or MODEL_PROVIDER or "fake").strip().lower()


def _resolve_api_key(provider: str) -> str:
    key = (os.environ.get("API_KEY") or API_KEY).strip()
    if key:
        return key
    for env_name in PROVIDER_KEY_ENVS.get(provider, ()):
        candidate = (os.environ.get(env_name) or "").strip()
        if candidate:
            return candidate
    return ""


def post_json(url: str, headers: dict, body: dict, timeout: int = 60) -> dict:
    """Gửi POST JSON, trả về JSON phản hồi. Chỉ dùng thư viện chuẩn (urllib)."""
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        method="POST",
        headers=dict({"Content-Type": "application/json"}, **headers),
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise RuntimeError("HTTP %d: %s" % (e.code, e.read().decode("utf-8", "replace")[:300]))
    if SHOW_RAW:
        print(json.dumps(data, ensure_ascii=False, indent=2)[:3000])
    return data


def call_openai(system: str, user: str, model_name: str, api_key: str) -> dict:
    url = (os.environ.get("OPENAI_BASE_URL") or URL_OPENAI).strip()
    messages = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": user}]
    data = post_json(
        url,
        {"Authorization": "Bearer " + api_key},
        {"model": model_name, "messages": messages, "temperature": 0},
    )
    usage = data["usage"]
    return {
        "text": data["choices"][0]["message"]["content"],
        "tokens_in": usage["prompt_tokens"],
        "tokens_out": usage["completion_tokens"],
    }


def call_claude(system: str, user: str, model_name: str, api_key: str) -> dict:
    data = post_json(
        URL_CLAUDE,
        {"x-api-key": api_key, "anthropic-version": "2023-06-01"},
        {
            "model": model_name,
            "max_tokens": 1024,
            "system": system or "",
            "messages": [{"role": "user", "content": user}],
            "temperature": 0,
        },
    )
    text = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")
    usage = data["usage"]
    return {
        "text": text,
        "tokens_in": usage["input_tokens"],
        "tokens_out": usage["output_tokens"],
    }


def call_ollama(system: str, user: str, model_name: str) -> dict:
    url = (os.environ.get("OLLAMA_URL") or URL_OLLAMA).strip()
    messages = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": user}]
    data = post_json(
        url,
        {},
        {"model": model_name, "messages": messages, "stream": False, "options": {"temperature": 0}},
        timeout=300,
    )
    return {
        "text": data["message"]["content"],
        "tokens_in": data.get("prompt_eval_count", 0),
        "tokens_out": data.get("eval_count", 0),
    }


def call_gemini(system: str, user: str, model_name: str, api_key: str) -> dict:
    url = URL_GEMINI_TMPL.format(model=model_name)
    body = {
        "contents": [{"role": "user", "parts": [{"text": user}]}],
        "generationConfig": {"temperature": 0},
    }
    if system:
        body["systemInstruction"] = {"parts": [{"text": system}]}
    data = post_json(url, {"x-goog-api-key": api_key}, body)
    candidates = data.get("candidates") or []
    if not candidates:
        raise RuntimeError(f"Gemini không trả về candidate: {json.dumps(data, ensure_ascii=False)[:300]}")
    parts = candidates[0].get("content", {}).get("parts", [])
    answer_parts = [p.get("text", "") for p in parts if not p.get("thought") and "text" in p]
    text = "".join(answer_parts or [p.get("text", "") for p in parts if "text" in p])
    usage = data.get("usageMetadata") or {}
    return {
        "text": text,
        "tokens_in": usage.get("promptTokenCount", 0),
        "tokens_out": (usage.get("candidatesTokenCount") or 0) + (usage.get("thoughtsTokenCount") or 0),
    }


def call_provider(system: str, user: str, model_name: str = "", api_key: str = "") -> dict:
    """Điểm mở rộng cho nhà cung cấp khác nếu nhóm cần tự viết thêm."""
    raise RuntimeError(f"Nhà cung cấp MODEL_PROVIDER={current_provider()} chưa được hỗ trợ trong codebase/ai.py")


@model_call
def call_model(system: str, user: str) -> dict:
    provider = current_provider()
    if provider == "fake":
        last = (user.strip().splitlines() or [""])[-1]
        return {"text": "[câu trả lời giả — chưa nối model] " + last[:60], "model": "fake", "tokens_in": 0, "tokens_out": 0}

    model_name = (os.environ.get("MODEL_NAME") or MODEL_NAME).strip()
    if not model_name:
        raise RuntimeError(f"Thiếu MODEL_NAME trong .env cho MODEL_PROVIDER={provider}")

    api_key = _resolve_api_key(provider)
    if provider != "ollama" and not api_key:
        raise RuntimeError(f"Thiếu API_KEY trong .env cho MODEL_PROVIDER={provider}")

    if provider == "openai":
        r = call_openai(system, user, model_name, api_key)
    elif provider in {"anthropic", "claude"}:
        r = call_claude(system, user, model_name, api_key)
    elif provider == "ollama":
        r = call_ollama(system, user, model_name)
    elif provider in {"gemini", "google"}:
        r = call_gemini(system, user, model_name, api_key)
    else:
        r = call_provider(system, user, model_name=model_name, api_key=api_key)

    return {
        "text": r["text"],
        "model": model_name,
        "tokens_in": int(r["tokens_in"]),
        "tokens_out": int(r["tokens_out"]),
    }
