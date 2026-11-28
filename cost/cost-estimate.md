# Chi phí khi dùng thật

## 1. Đầu vào

| Persona | Tỷ lệ người dùng | Phiên / người / tháng | Lượt hỏi / phiên |
|---|---:|---:|---:|
| Dùng ít | 50% | 1 | 1 |
| Dùng vừa | 30% | 2 | 2 |
| Dùng nhiều | 20% | 4 | 3 |

Tỷ lệ, số phiên và số lượt hỏi trong bảng là *(tự ước tính)*. Ba kịch bản quy mô là **10**, **20** và **30 học viên** có khả năng sử dụng mỗi tháng, tương ứng thấp, cơ sở và cao. Quy mô cũng là *(tự ước tính)*. Khảo sát đo trải nghiệm hỗ trợ gấp ngoài lớp và chưa đo tần suất sử dụng trợ lý theo tháng. [Cấu hình persona](personas.yaml) · [Giả định trong §2](../spec.md) · [Tổng hợp khảo sát](../evidence/summary.md).

| Model tính giá | USD / 1 triệu token vào | USD / 1 triệu token ra | Nguồn giá, tra ngày 28/11/2026 |
|---|---:|---:|---|
| `gpt-4o-mini` | 0.15 | 0.60 | [OpenRouter GPT-4o mini](https://openrouter.ai/openai/gpt-4o-mini) |
| `gpt-4.1-mini` | 0.40 | 1.60 | [OpenRouter GPT-4.1 mini](https://openrouter.ai/openai/gpt-4.1-mini) |

Mô phỏng dùng tỷ lệ đạt **24/24 (100%)** từ lượt `run-2@20261128-092151`, ghi model `gpt-4o-mini`. [CSV lượt 2 đã chấm](../eval/run-2.csv).

## 2. Kết quả mô phỏng

Lượt `simulate-1@20261128-100512` chạy **50 phiên**, gồm 91 lượt hỏi, với seed **42** và **0 phiên lỗi**. [CSV mô phỏng](simulate-1.csv) · [Bản tóm tắt tự sinh](simulate-1-summary.md) · [Trace](../traces/simulate-1.jsonl).

| Model (giá) | Chi phí / phiên | Chi phí / task thành công | Chi phí / câu hỏi đạt | Chi phí / tháng — thấp (10 người) | Chi phí / tháng — cơ sở (20 người) | Chi phí / tháng — cao (30 người) | Chi phí / người / tháng (cơ sở) |
|---|---:|---:|---:|---:|---:|---:|---:|
| gpt-4o-mini (vào 0.15 · ra 0.6 $/1M) | $0.00021 | $0.00021 | $0.00012 | $0.0048 | $0.0095 | $0.0143 | $0.00048 |
| gpt-4.1-mini (vào 0.4 · ra 1.6 $/1M) | $0.00056 | $0.00056 | $0.00031 | $0.0127 | $0.0254 | $0.0382 | $0.0013 |

Chi phí mỗi task thành công bằng chi phí trung bình mỗi phiên chia cho tỷ lệ đạt của lượt 2. Mô phỏng đo token trên `openai/gpt-4o-mini` qua OpenRouter. Khung ghi cảnh báo vì định danh này khác định danh `gpt-4o-mini` trong lượt 2. Dòng `gpt-4.1-mini` áp giá niêm yết của model đó lên lượng token đã đo.

## 3. So với impact

- Impact dự kiến là **10 phút thao tác có thể giảm mỗi người mỗi tháng** *(tự ước tính)*. [Giả định trong §2](../spec.md).
- Ở kịch bản cơ sở, chi phí token theo giá `gpt-4o-mini` là **$0.00048/người/tháng**.
- **Kết luận.** Chi phí token ở quy mô thử nghiệm thấp. Nhóm có thể chạy pilot nhỏ để đo thời gian thực tế giảm được trước khi quyết định mở rộng.
