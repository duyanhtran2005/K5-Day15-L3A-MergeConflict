"""Nối model — chỗ DUY NHẤT trong bản chạy thử gọi model AI.

Hợp đồng (giữ nguyên để khung đo được token):
    call_model(system: str, user: str) -> dict với 4 khoá:
        "text":       str   chữ model trả về
        "model":      str   tên model đã gọi
        "tokens_in":  int   số token vào, lấy từ usage trong phản hồi API
        "tokens_out": int   số token ra, gồm cả token suy luận nếu API tính riêng
"""
import json
import os
import urllib.error
import urllib.parse
import urllib.request

from tracing import model_call

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOW_RAW = False


def load_env(path=os.path.join(ROOT, ".env")):
    """Đọc file .env (KEY=VALUE mỗi dòng) vào biến môi trường, không ghi đè biến đã có."""
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
OPENAI_BASE_URL = (os.environ.get("OPENAI_BASE_URL") or "https://api.openai.com/v1/chat/completions").strip()


def post_json(url: str, headers: dict, body: dict, timeout: int = 60) -> dict:
    """Gửi POST JSON bằng thư viện chuẩn urllib và trả về JSON phản hồi."""
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


def call_openai(system: str, user: str) -> dict:
    """Gọi OpenAI hoặc endpoint tương thích OpenAI theo docs/connect-model.md."""
    messages = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": user}]
    data = post_json(
        OPENAI_BASE_URL,
        {"Authorization": "Bearer " + API_KEY},
        {"model": MODEL_NAME, "messages": messages},
    )
    usage = data.get("usage") or {}
    return {
        "text": data["choices"][0]["message"]["content"],
        "tokens_in": int(usage.get("prompt_tokens", 0)),
        "tokens_out": int(usage.get("completion_tokens", 0)),
    }


def call_claude(system: str, user: str) -> dict:
    """Gọi Anthropic Messages API theo docs/connect-model.md."""
    url = "https://api.anthropic.com/v1/messages"
    data = post_json(
        url,
        {"x-api-key": API_KEY, "anthropic-version": "2023-06-01"},
        {
            "model": MODEL_NAME,
            "max_tokens": 1024,
            "system": system or "",
            "messages": [{"role": "user", "content": user}],
        },
    )
    text = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")
    usage = data.get("usage") or {}
    return {
        "text": text,
        "tokens_in": int(usage.get("input_tokens", 0)),
        "tokens_out": int(usage.get("output_tokens", 0)),
    }


def call_ollama(system: str, user: str) -> dict:
    """Gọi Ollama cục bộ theo docs/connect-model.md."""
    url = "http://localhost:11434/api/chat"
    messages = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": user}]
    data = post_json(url, {}, {"model": MODEL_NAME, "messages": messages, "stream": False}, timeout=300)
    return {
        "text": data["message"]["content"],
        "tokens_in": int(data.get("prompt_eval_count", 0)),
        "tokens_out": int(data.get("eval_count", 0)),
    }


def call_gemini(system: str, user: str) -> dict:
    """Gọi Google Gemini generateContent REST API bằng thư viện chuẩn."""
    model_id = urllib.parse.quote(MODEL_NAME or "gemini-2.5-flash", safe="")
    url = "https://generativelanguage.googleapis.com/v1beta/models/%s:generateContent" % model_id
    payload = {
        "contents": [{"role": "user", "parts": [{"text": user}]}],
    }
    if system:
        payload["systemInstruction"] = {"parts": [{"text": system}]}
    data = post_json(url, {"x-goog-api-key": API_KEY}, payload)
    candidates = data.get("candidates") or []
    parts = ((candidates[0].get("content") or {}).get("parts") or []) if candidates else []
    text = "".join(p.get("text", "") for p in parts if isinstance(p, dict))
    usage = data.get("usageMetadata") or {}
    tokens_in = int(usage.get("promptTokenCount", 0))
    tokens_out = int(usage.get("candidatesTokenCount", 0)) + int(usage.get("thoughtsTokenCount", 0))
    return {
        "text": text,
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
    }


@model_call
def call_model(system: str, user: str) -> dict:
    """Gọi model theo cấu hình .env (giữ nhánh fake chuẩn của khung để eval/simulate nhận diện)."""
    if MODEL_PROVIDER == "fake":
        last = (user.strip().splitlines() or [""])[-1]
        return {"text": "[câu trả lời giả — chưa nối model] " + last[:60], "model": "fake", "tokens_in": 0, "tokens_out": 0}
    if MODEL_PROVIDER == "openai":
        r = call_openai(system, user)
    elif MODEL_PROVIDER == "anthropic":
        r = call_claude(system, user)
    elif MODEL_PROVIDER == "ollama":
        r = call_ollama(system, user)
    elif MODEL_PROVIDER == "gemini":
        r = call_gemini(system, user)
    else:
        raise RuntimeError("MODEL_PROVIDER=%s chưa được hỗ trợ trong codebase/ai.py" % MODEL_PROVIDER)
    return {
        "text": r["text"],
        "model": MODEL_NAME or MODEL_PROVIDER,
        "tokens_in": int(r["tokens_in"]),
        "tokens_out": int(r["tokens_out"]),
    }
