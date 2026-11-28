# Hướng dẫn pull nhánh và chạy bản nối model thật (dành cho Linh & nhóm)

Tài liệu này hướng dẫn cách lấy nhánh `feature/real-model-routing`, tạo file `.env` cục bộ (không commit lên GitHub) và chạy kiểm thử bản trợ lý lab đã nối model thật ở bước đánh giá nguồn và chọn bước xử lý.

## 1. Lấy nhánh mới nhất về máy

```bash
git fetch origin
git checkout -b feature/real-model-routing origin/feature/real-model-routing
```

Nếu đã có nhánh `feature/real-model-routing` trên máy thì cập nhật bằng:

```bash
git checkout feature/real-model-routing
git pull origin feature/real-model-routing
```

## 2. Tạo file `.env` (không commit key)

Sao chép `.env.example` thành `.env` tại thư mục gốc repo:

- Windows PowerShell: `copy .env.example .env`
- macOS / Linux: `cp .env.example .env`

Mở `.env`, điền đúng 3 dòng (không dấu ngoặc kép, không dư khoảng trắng):

```env
MODEL_PROVIDER=openai
MODEL_NAME=gpt-4o-mini
API_KEY=<nhập_API_key_của_nhóm>
```

> Lưu ý: Nếu máy đã đặt biến môi trường `OPENAI_API_KEY` (hoặc `GEMINI_API_KEY` khi dùng `MODEL_PROVIDER=gemini`), có thể để trống `API_KEY=`. File `.gitignore` đã loại trừ `.env` để không commit nhầm. Muốn chạy ngoại tuyến không gọi API thật thì đặt `MODEL_PROVIDER=fake`.

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

   Gõ lần lượt 4 câu thử trọng tâm dưới đây rồi nhấn `Enter` (nhấn `Enter` 2 lần ở dòng trống hoặc `Ctrl+C` để thoát):

   | Mã | Nhập vào sau dấu `>` | Kết quả cần kiểm |
   |---|---|---|
   | `B01` | `[Thread: 3A-LAB-C302] Lab 10 chiều 27/4 mấy giờ hết hạn nộp vậy ạ?` | Trả hạn nộp `17:00 ngày 27/04/2027` và link `C302-01`; trace chỉ gọi `search_lab_thread` cho `3A-LAB-C302`. |
   | `B06` | `[Thread: 3A-LAB-C302] Cho em xin chỗ đọc hướng dẫn Lab 10 chiều 27/4 với.` | Báo chưa có hướng dẫn Lab 10 trong `3A-LAB-C302`, chưa xác minh được coach `C302`, gợi ý hỏi tiếp trong thread; không tra hay lộ `F307-01`. |
   | `B08` | `[Thread: 3A-LAB-C204] Anh chị ơi, Lab 13 sáng 5/5 em không vào được tài liệu thì hỏi coach nào?` | Đề xuất `Coach mẫu A · L3A · C204 · ca sáng ngày 05/05/2027`, giữ trạng thái chờ học viên xác nhận (`Chưa gửi tag.`). |
   | `B12` | `[Thread: 3A-LAB-C204] Lab 13 ca sáng 05/05/2027. Ăn gì ngon ở gần trường vậy?` | Từ chối câu ăn uống ngoài phạm vi hỗ trợ lab; `gọi model 0 lần · công cụ 0 lần`, không gợi ý coach hay tạo bản nháp. |

3. Chạy cả bộ câu thử (khi nhóm đã hoàn tất đủ 20–30 câu CP3):

   ```bash
   python run.py eval --wait 4
   ```
