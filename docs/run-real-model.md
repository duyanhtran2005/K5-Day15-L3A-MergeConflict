# Hướng dẫn chạy bản trợ lý lab với model thật

Hướng dẫn này dùng nhánh `main` và cấu hình GPT-4o mini qua OpenRouter của bản demo CP4.

## 1. Cập nhật nhánh `main`

```bash
git switch main
git pull --ff-only origin main
```

## 2. Tạo file `.env` (không commit key)

Nếu chưa có `.env`, sao chép `.env.example` thành `.env` tại thư mục gốc repo:

- Windows PowerShell: `copy .env.example .env`
- macOS / Linux: `cp .env.example .env`

Mở `.env` và điền bốn dòng sau:

```env
MODEL_PROVIDER=openai
MODEL_NAME=openai/gpt-4o-mini
OPENAI_BASE_URL=https://openrouter.ai/api/v1/chat/completions
API_KEY=<khóa OpenRouter của bạn>
```

Thay giá trị mẫu của `API_KEY` bằng khóa OpenRouter của bạn. Giữ `MODEL_PROVIDER=openai` để dùng nhánh gọi API tương thích OpenAI trong `codebase/ai.py`. Nếu cần chạy ngoại tuyến, đặt `MODEL_PROVIDER=fake`.

## 3. Lệnh chạy kiểm thử

1. Kiểm tra nối model qua khung đánh giá (chạy 3 câu đầu `B01`–`B03`, không tính là một lượt chấm chính thức):

   ```bash
   python run.py eval --try
   ```

   Thấy dòng `Nối model được: có token > 0` là đạt.

2. Chạy trợ lý dòng lệnh tương tác:

   ```bash
   python run.py
   ```

   Gõ từng câu thử dưới đây rồi nhấn `Enter`. Dùng B01 và B20 cho demo CP4. Nhấn `Enter` hai lần ở dòng trống hoặc `Ctrl+C` để thoát.

   | Mã | Nhập vào sau dấu `>` | Kết quả cần kiểm |
   |---|---|---|
   | `B01` | `[Thread: 3A-LAB-C302] Lab 10 chiều 27/4 mấy giờ hết hạn nộp vậy ạ?` | Trả hạn nộp `17:00 ngày 27/04/2027` và link `C302-01`; trace chỉ gọi `search_lab_thread` cho `3A-LAB-C302`. |
   | `B06` | `[Thread: 3A-LAB-C302] Cho em xin chỗ đọc hướng dẫn Lab 10 chiều 27/4 với.` | Báo chưa có hướng dẫn Lab 10 trong `3A-LAB-C302`, chưa xác minh được coach `C302`, gợi ý hỏi tiếp trong thread; không tra hay lộ `F307-01`. |
   | `B08` | `[Thread: 3A-LAB-C204] Anh chị ơi, Lab 13 sáng 5/5 em không vào được tài liệu thì hỏi coach nào?` | Đề xuất `Coach mẫu A · L3A · C204 · ca sáng ngày 05/05/2027`, giữ trạng thái chờ học viên xác nhận (`Chưa gửi tag.`). |
   | `B12` | `[Thread: 3A-LAB-C204] Lab 13 ca sáng 05/05/2027. Ăn gì ngon ở gần trường vậy?` | Từ chối câu ăn uống ngoài phạm vi hỗ trợ lab; `gọi model 0 lần · công cụ 0 lần`, không gợi ý coach hay tạo bản nháp. |
   | `B20` | `[Thread: 3A-LAB-C204] Em thấy repo K5 có tài liệu hướng dẫn Lab 13 dành riêng cho buổi chiều. Em cần hướng dẫn áp dụng cho Lab 13 ngày 05/05/2027 trong thread này, em xem ở đâu ạ?` | Hỏi học viên học Lab 13 ngày 05/05/2027 vào ca sáng, chiều hay tối. Hiển thị `gọi model 0 lần · công cụ 0 lần`. |

3. Xem hai lượt CP4 đã lưu bằng `python run.py score eval/run-1.csv` và `python run.py score eval/run-2.csv`. Nếu thực hiện một lượt đánh giá mới, dùng lệnh sau:

   ```bash
   python run.py eval --wait 4
   ```
