---
version: 1
slug: "codebase-ui-index-html"
primary_target: "codebase/ui/index.html"
related_targets: ["codebase/app.py"]
---

# Surface Brief — Cổng Hỗ Trợ Buổi Lab AI20K L3A

- **Scope & Mode:** Operate (`codebase/ui/index.html`, `codebase/app.py`)
- **Audience & Job:** Học viên AI20K L3A cần câu trả lời có nguồn xác thực nhanh trong buổi lab; điều phối viên duyệt bản nháp chuyển Coach; nhóm trình diễn Trace & nguồn đối chiếu khi cần.
- **Primary Action / States:** Hỏi đáp tối giản trên dòng hội thoại sạch; bấm trích dẫn hoặc nút `Chi tiết & Trace` để mở ngăn trượt kiểm chứng nguồn và trace; duyệt/chỉnh sửa nháp ở `Duyệt chuyển Coach`; tra cứu quy định và lịch trực ở `Thông báo & Ca trực`.
- **Constraints:** Chạy bằng `python run.py` không cần npm/pip; giữ hợp đồng `answer(text) -> {"output": str}`; không tự gửi tin ngoài khi chưa có người duyệt.
- **Memorable Moment:** Trải nghiệm hỏi đáp thoáng sạch như sản phẩm thật, ẩn toàn bộ chi tiết kỹ thuật vào ngăn trượt `Chi tiết & Trace` chỉ mở khi bấm kiểm chứng nguồn hoặc trace.

## Direction contract

THESIS: Tinh giản cổng hỗ trợ lab về bề mặt hỏi đáp sáng thoáng chuẩn sản phẩm thật — lược bỏ hộp trạng thái 3 bước, thẻ lồng thẻ và nhãn lặp lại, chỉ hiện trích dẫn gốc và nhật ký trace trong ngăn trượt theo yêu cầu.

OWN-WORLD: Cohort Dispatch Ledger — cột điều hướng xanh hải quân đậm `#132238` (`248px`) bên cạnh vùng làm việc trắng sạch `#FFFFFF` căn giữa tối đa `780px`, đường phân cách mảnh `#E6EBF1`, cobalt `#1D4ED8` cho hành động chính và trạng thái trích dẫn đang mở, chữ tự nhúng cục bộ `Be Vietnam Pro` + `JetBrains Mono`.

STORY: Học viên nhìn thẳng vào câu trả lời rõ ràng và nguồn trích dẫn gọn gàng ở chân đoạn; khi cần đối chiếu nguyên văn hoặc xem trace, bấm vào mã nguồn để mở ngăn trượt bên phải rồi đóng lại để giữ không gian yên tĩnh.

FIRST VIEWPORT: Bố cục 2 cột thoáng trên desktop `1440×900` (cột trái `248px` có nút tạo phiên mới, 3 tab chức năng và 4 câu hỏi gợi ý tối giản; vùng chính căn giữa với lời chào và ô nhập liệu hợp nhất ở đáy; ngăn phải `Chi tiết & Trace` đóng mặc định).

FORM: Candidate 7 — Cohort Dispatch Ledger (distilled 2-column + on-demand trace drawer), seed:035bd6ddbafd2e59.

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
