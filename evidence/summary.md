# Tổng hợp bằng chứng vấn đề

## 1. Nguồn đã dùng

| Nguồn | Đạt ngưỡng? | Ghi chú |
|---|---|---|
| Khảo sát Google Forms về hỗ trợ gấp ngoài lớp | **Đạt.** Có 20 học viên L3A khác nhau, đều ngoài nhóm MergeConflict, theo xác nhận của Linh. | 21 phiếu nhận được trong ngày 27–28/11/2026. Loại S21 vì việc chính là xin nghỉ học. [Bộ câu hỏi](survey/questions.md) · [Log ẩn danh](survey/results.csv). |
| Quan sát trao đổi Discord về lab | Nguồn đối chiếu gồm 9 trường hợp trong mẫu ảnh, có 5 ví dụ nguyên văn đã ẩn danh. | [Ghi chép quan sát Discord](data-mining-yeu-cau-01.md). |

## 2. Số chính

Mẫu số là 20 phiếu S01–S20. Cả 20 cho biết đã từng cần hỗ trợ gấp về lab ngoài lớp trong 30 ngày qua. Linh xác nhận đối tượng và việc ở ngoài nhóm vì biểu mẫu thiếu trường xác minh này. Cột `pham_vi` trong CSV ghi rõ phiếu được đưa vào mẫu.

| Quan sát | Số phiếu | Cách đếm |
|---|---:|---|
| Mất thời gian tìm thông tin hoặc tìm đúng kênh để hỏi | 14/20 | Cột F, chọn “Tìm thông tin hoặc tìm đúng kênh để hỏi”. |
| Mất thời gian chờ người phụ trách phản hồi | 13/20 | Cột F, chọn “Chờ người phụ trách phản hồi”. |
| Chờ ticket được duyệt hoặc phân công | 8/20 | Cột F, chọn “Chờ ticket được duyệt hoặc phân công”. |
| Tạo ticket hoặc nhập lại nội dung đã gửi | 7/20 | Cột F, chọn “Tạo ticket hoặc nhập lại nội dung đã gửi”. |
| Xác nhận đã tạo ticket | 9/20 | Cột E, 7 phiếu được yêu cầu và đã tạo, 2 phiếu tự tạo. |
| Mất ít nhất 15 phút mới có hướng xử lý | 15/20 | Cột G, gồm 7 phiếu từ 15 đến dưới 30 phút, 5 phiếu từ 30 đến dưới 60 phút và 3 phiếu từ 60 phút trở lên. |
| Nộp bài muộn hoặc không nộp được | 6/20 | Cột H, chọn “Nộp bài muộn hoặc không nộp được”. |

Cột F và H cho phép chọn nhiều đáp án. Mỗi phiếu được tính một lần cho từng lựa chọn. Thời gian ở cột G là tổng thời gian từ lúc bắt đầu tìm hoặc hỏi đến khi có hướng xử lý. S07 có hai đáp án khác nhau về việc tạo ticket ở cột D và E. Số 9/20 dùng câu hỏi trực tiếp ở cột E. [Bảng đối chiếu cột và câu hỏi](survey/questions.md#câu-hỏi).

## 3. Trích dẫn và ví dụ nguyên văn

Các câu dưới đây lấy từ cột `mo_ta_cho_phep_trich` theo mã phản hồi trong [log khảo sát ẩn danh](survey/results.csv).

- **S05** — “Tôi cần xác nhận tên repo cho tên lab, lúc đấy là 22h và deadline là 23h59, do trong repo và trên lms yêu cầu tên repo khác nhau nên tôi không biết đặt tên repo là gì.”
- **S06** — “tôi Ping Labcoach trên dc và thường thì phản hồi sẽ chậm và mơ hồ”
- **S07** — “gặp vấn đề khi deploy lên railway mất 5-10 phút, sau đó nhờ Ai đưa ra cách làm nhưng vẫn không hiểu và cần đến sự trợ giúp của labcoach nhưng đã tan tầm nên phải nhắn tin thì mất thêm 15 phút để labcoach có thể hỗ trợ”
- **S08** — “lên discord hỏi và tạo ticket, đợi khá lâu để có câu trả lời”
- **S14** — “tôi cần đối chiếu về thời gian deadline của bài lab do có sự không nhất quán giữa repo và thông báo của lab coach.”
- **S15** — “Tôi cần hỏi hạn nộp lab, nhắn trong kênh chat nhưng chưa có ai trả lời, việc nộp bài bị gián đoạn tầm 10p cho đến khi tôi tự tìm và đọc lại tài liệu.”
- **S20** — “Hỏi chat chung về hạn nộp lab vì không biết lab buổi chiều nộp cùng ngày hay ngày hôm sau.”

## 4. Các nguồn có khớp nhau không

Khảo sát có ca mâu thuẫn hướng dẫn đặt tên repo (S05) và hạn nộp (S14). Mẫu quan sát Discord cũng ghi nhận học viên hỏi lại vì quy định đặt tên repo giữa các nguồn khác nhau (Q01) và cần xác nhận hạn nộp (Q08). Hai nguồn cho thấy nhu cầu xác nhận hướng dẫn về bài lab. [Ghi chép quan sát Discord](data-mining-yeu-cau-01.md).

## 5. Kết luận

Khảo sát ủng hộ giả thuyết học viên mất thời gian tìm kênh hỏi và chờ phản hồi khi cần hỗ trợ gấp ngoài lớp. Hai bước này được chọn nhiều nhất, với 14/20 và 13/20 phiếu. Kết quả hỗ trợ việc ưu tiên trả lời kèm nguồn và chỉ dẫn đúng người phụ trách.

Mẫu gồm người từng cần hỗ trợ gấp ngoài lớp, được tiếp cận qua nhóm preclass và bạn bè. Các số mô tả 20 phiếu tự báo cáo trong mẫu. S11 và S13 tìm người phụ trách ca hoặc phòng để hỏi về điểm danh, nên nhóm vẫn tính vào nhu cầu tìm người hỗ trợ. Mẫu quan sát Discord hỗ trợ thêm việc xem xét nhu cầu trong thread phòng lab.
