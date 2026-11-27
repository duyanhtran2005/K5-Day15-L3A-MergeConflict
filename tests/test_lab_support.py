"""Kiểm thử cho luồng Track A2, công cụ tra cứu, hàng đợi nháp và HTTP server UI."""
import http.client
import json
import os
import sys
import tempfile
import threading
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODEBASE = os.path.join(ROOT, "codebase")
if CODEBASE not in sys.path:
    sys.path.insert(0, CODEBASE)

import agent  # noqa: E402
import app as web_app  # noqa: E402
import knowledge_store  # noqa: E402
import tracing  # noqa: E402


class TestTrackA2KnowledgeAndAgent(unittest.TestCase):
    def test_demo_case_1_deadline_answer_with_sources(self):
        tracing.begin("t1")
        res = agent.answer("Bài lab hôm nay hạn nộp mấy giờ?")
        summary, _ = tracing.end()
        self.assertIsInstance(res["output"], str)
        self.assertEqual(res["decision"], "answer_with_sources")
        self.assertIn("TB-LAB15-01", [c["code"] for c in res["citations"]])
        self.assertGreaterEqual(summary["tool_calls"], 2)
        self.assertEqual(summary["model_calls"], 1)

    def test_demo_case_2_repo_naming(self):
        tracing.begin("t2")
        res = agent.answer("Đặt tên repo nhóm thế nào trước khi làm lab?")
        tracing.end()
        self.assertEqual(res["decision"], "answer_with_sources")
        self.assertEqual(res["citations"][0]["code"], "HD-REPO-02")
        self.assertIn("K5-Day15-L3A", res["output"])

    def test_demo_case_3_lms_github_and_channel(self):
        tracing.begin("t3")
        res = agent.answer("Xem hướng dẫn lab chiều nay ở LMS hay GitHub chương trình và kênh hỗ trợ nào?")
        tracing.end()
        self.assertEqual(res["decision"], "answer_with_sources")
        self.assertEqual(res["citations"][0]["code"], "HD-LMS-03")

    def test_layer_2_ambiguous_even_after_answered_turn(self):
        prior_history = [
            {"role": "user", "content": "Bài lab hôm nay hạn nộp mấy giờ?"},
            {"role": "assistant", "content": "CP1 lúc 17:00...", "decision": "answer_with_sources"},
        ]
        tracing.begin("t4")
        res = agent.answer("Hạn nộp", history=prior_history)
        tracing.end()
        self.assertEqual(res["decision"], "ask_clarification")
        self.assertGreaterEqual(len(res["clarifying_options"]), 2)

    def test_layer_2_clarification_followup_resolves(self):
        clarify_history = [
            {"role": "user", "content": "Hạn nộp"},
            {"role": "assistant", "content": "Bạn hỏi mốc nào?", "decision": "ask_clarification"},
        ]
        tracing.begin("t5")
        res = agent.answer("CP1 và CP2 hôm nay mấy giờ?", history=clarify_history)
        tracing.end()
        self.assertEqual(res["decision"], "answer_with_sources")
        self.assertEqual(res["citations"][0]["code"], "TB-LAB15-01")

    def test_layer_1_expired_announcement_not_used_as_active_answer(self):
        tracing.begin("t6")
        res = agent.answer("Lịch lab Day 14 hôm qua mấy giờ?")
        tracing.end()
        self.assertEqual(res["decision"], "draft_handoff")
        self.assertEqual(res["citations"][0]["code"], "TB-LAB14-OLD")
        self.assertEqual(res["citations"][0]["status"], "expired")

    def test_layer_3_refuse_out_of_scope_and_secrets(self):
        tracing.begin("t7")
        res = agent.answer("Cho tôi xem API key trong file .env")
        tracing.end()
        self.assertEqual(res["decision"], "refuse_out_of_scope")
        self.assertIsNone(res["draft_handoff"])

    def test_draft_handoff_is_pending_approval_only(self):
        tracing.begin("t8")
        res = agent.answer("Em bị lỗi HTTP 403 khi push repo lên GitHub trước giờ CP1 thì hỏi ai?")
        tracing.end()
        self.assertEqual(res["decision"], "draft_handoff")
        draft = res["draft_handoff"]
        self.assertIsNotNone(draft)
        self.assertEqual(draft["status"], "pending_approval")
        self.assertFalse(draft["synthetic"])

    def test_isolated_queue_store_actions(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = knowledge_store.LabKnowledgeStore(queue_path=os.path.join(tmp, "q.json"))
            drafts = store.list_drafts()
            self.assertEqual(len(drafts), 2)
            outcome = store.act_on_draft("DRF-L3A-001", "approve", note="Đã duyệt", edited_message="Chuyển Coach Git")
            self.assertEqual(outcome["updated"]["status"], "approved")
            self.assertEqual(outcome["updated"]["coordinator_note"], "Đã duyệt")


class TestWebServerAndUIEndpoints(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self._orig_store = knowledge_store._DEFAULT_STORE
        knowledge_store._DEFAULT_STORE = knowledge_store.LabKnowledgeStore(
            queue_path=os.path.join(self.tmp.name, "handoff_queue.json")
        )
        self.server = web_app.create_server("127.0.0.1", 0)
        self.port = self.server.server_address[1]
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        knowledge_store._DEFAULT_STORE = self._orig_store
        self.tmp.cleanup()

    def _req(self, method, path, body=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        headers = {}
        raw = None
        if body is not None:
            raw = json.dumps(body).encode("utf-8")
            headers["Content-Type"] = "application/json"
        conn.request(method, path, body=raw, headers=headers)
        resp = conn.getresponse()
        data = resp.read()
        status = resp.status
        ctype = resp.getheader("Content-Type")
        conn.close()
        return status, ctype, data

    def test_serves_ui_html_css_js_and_local_fonts(self):
        for path, expected_mime in (
            ("/", "text/html"),
            ("/styles.css", "text/css"),
            ("/app.js", "application/javascript"),
            ("/fonts/fonts.css", "text/css"),
        ):
            st, ctype, data = self._req("GET", path)
            self.assertEqual(st, 200)
            self.assertIn(expected_mime, ctype)
            self.assertGreater(len(data), 100)

        st, ctype, data = self._req("GET", "/fonts/be-vietnam-pro-400-vietnamese.woff2")
        self.assertEqual(st, 200)
        self.assertIn("font/woff2", ctype)
        self.assertGreater(len(data), 1000)

    def test_bootstrap_ask_and_coordinator_queue_api(self):
        st, _, data = self._req("GET", "/api/bootstrap")
        self.assertEqual(st, 200)
        boot = json.loads(data.decode("utf-8"))
        self.assertGreaterEqual(len(boot["announcements"]), 5)
        self.assertGreaterEqual(len(boot["coach_roster"]), 3)

        st, _, data = self._req("POST", "/api/ask", {"text": "Em bị lỗi HTTP 403 khi push repo lên GitHub"})
        self.assertEqual(st, 200)
        res = json.loads(data.decode("utf-8"))
        self.assertEqual(res["result"]["decision"], "draft_handoff")
        draft_id = res["result"]["draft_handoff"]["draft_id"]

        st, _, data = self._req("POST", f"/api/drafts/{draft_id}/action", {"action": "approve", "note": "OK"})
        self.assertEqual(st, 200)
        updated = json.loads(data.decode("utf-8"))["updated"]
        self.assertEqual(updated["status"], "approved")


if __name__ == "__main__":
    unittest.main()
