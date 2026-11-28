# Tóm tắt mô phỏng simulate-1@20261128-100512

Do `python run.py simulate` sinh ra — không sửa tay. Chép bảng sang `cost/cost-estimate.md`.

| Persona | Số phiên mô phỏng | Lượt hỏi / phiên | Token vào / phiên | Token ra / phiên | Gọi model / phiên | Gọi công cụ / phiên |
|---|---:|---:|---:|---:|---:|---:|
| dung_it | 20 | 1 | 472 | 64 | 0.7 | 1.1 |
| dung_vua | 19 | 2 | 1030 | 137 | 1.4 | 2.1 |
| dung_nhieu | 11 | 3 | 1524 | 202 | 2.1 | 3.1 |

Tỉ lệ đạt dùng để tính: 24/24 (100%) — lượt run-2@20261128-092151

- Tỉ lệ đạt lấy từ lượt nhóm chọn: eval/run-2.csv (--rate-from). ⚠️ Lượt này chạy bằng gpt-4o-mini, mô phỏng đo trên openai/gpt-4o-mini — khác model.

| Model (giá) | Chi phí / phiên | Chi phí / task thành công | Chi phí / câu hỏi đạt | Chi phí / tháng — thấp (10 người) | Chi phí / tháng — cơ sở (20 người) | Chi phí / tháng — cao (30 người) | Chi phí / người / tháng (cơ sở) |
|---|---:|---:|---:|---:|---:|---:|---:|
| gpt-4o-mini (vào 0.15 · ra 0.6 $/1M) | $0.00021 | $0.00021 | $0.00012 | $0.0048 | $0.0095 | $0.0143 | $0.00048 |
| gpt-4.1-mini (vào 0.4 · ra 1.6 $/1M) | $0.00056 | $0.00056 | $0.00031 | $0.0127 | $0.0254 | $0.0382 | $0.0013 |

- Chi phí / task thành công = chi phí / phiên ÷ tỉ lệ đạt. Chi phí / câu hỏi đạt = chi phí / phiên ÷ số lượt hỏi trung bình mỗi phiên (1.8) ÷ tỉ lệ đạt — tỉ lệ đạt đo theo từng câu thử.
- Token đo trên model: openai/gpt-4o-mini. Giá tính theo từng model trong bảng — model khác bộ tách token thì số token thật có thể lệch; ghi rõ "đo trên model X, tính giá model Y" trong cost/cost-estimate.md.
- Phiên lỗi (không tính vào trung bình): 0/50.
