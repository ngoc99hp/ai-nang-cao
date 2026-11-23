# Demo — Misconception Clustering

## Chạy

```bash
./demo/start.sh          # bật giao diện + sandbox chấm bài
./demo/stop.sh           # tắt
```

Mở http://127.0.0.1:8501. Nếu xem từ máy khác, tạo SSH tunnel trước:
`ssh -p 2222 -N -L 8501:127.0.0.1:8501 tuyendv@63.250.52.57`, rồi mở http://localhost:8501.

## 4 trang

| Trang | Dành cho | Nội dung |
|---|---|---|
| Tổng quan | hội đồng | quy trình 5 bước, số liệu chính |
| Giảng viên: macro-feedback | giảng viên | chọn bài tập → các cụm lỗi, số SV mắc, đặc trưng, luật ILA, bài minh họa + diff, heatmap |
| Nộp bài: chẩn đoán lỗi | sinh viên | dán code C (hoặc chọn bài mẫu) → chấm test → cụm misconception, lý do, luật khớp, so với bản đúng gần nhất |
| Thực nghiệm | hội đồng | E1–E5: bảng + hình |

## Kịch bản demo gợi ý (5 phút)

1. **Tổng quan**: quy trình chấm → OAV → K-modes → ILA → macro-feedback.
2. **Giảng viên**, bài `smallest`: cụm C0 có 36 SV so sánh `<` thay vì `<=`, bỏ sót giá trị bằng nhau.
   Mở cụm để xem luật ILA và diff của bài minh họa.
3. **Nộp bài**, bài `smallest`:
   - chọn mẫu `smallest_so_sanh_nghiem_ngat` → Chấm: trượt 8/16 test, chẩn đoán C0;
   - sửa `<` thành `<=` ở cả 4 dòng `if` → Chấm lại: bài đúng.
4. Thử thêm `grade_nguong_nghiem_ngat` và `median_thieu_ve_doi_xung`.
5. **Thực nghiệm**: ablation E3 cho thấy nhóm D quyết định chất lượng.

## Kiến trúc an toàn

```
trình duyệt ──► aai-ui (Streamlit, 127.0.0.1:8501)       không có gcc, không chạy code
                   │ ghi job json
                   ▼
               work/queue/in ──► aai-sandbox: worker + src/runner.py
                                 không mạng · root fs chỉ đọc · code/dữ liệu mount chỉ đọc
                                 ghi được: work/queue + tmpfs tạm · 1 CPU / 1 GB / 128 tiến trình
               work/queue/out ◄──┘  (ulimit CPU/RAM/output từng lần chạy, diệt cả nhóm tiến trình sau đó)
```

`aai-lab` (môi trường nghiên cứu) **không** chạy bài nộp từ giao diện.
Đã thử với các bài độc hại: lặp/in vô hạn, ăn RAM, ghi file dự án, mở mạng, fork bomb, `#include "/dev/zero"`,
tự diệt worker. Tất cả đều bị chặn hoặc báo lỗi, và sandbox tự hồi phục.
Log của worker: `docker logs aai-sandbox`.

## Cập nhật dữ liệu demo

Sau khi sửa tên cụm (`results/tables/p5_cluster_names.csv`) hoặc chạy lại thí nghiệm:

```bash
docker exec aai-lab python -W ignore scripts/p7_build_demo.py
docker compose restart sandbox ui
```

## Giới hạn

- Bài mới không có bản tự sửa của SV → nhóm D so với **bản đúng gần nhất** trong kho
  (IntroClass + lời giải tự viết), nên kém chính xác hơn lúc gom cụm.
  Ví dụ: 16/18 bài minh họa thật được gán lại đúng cụm của nó.
- `digits_quen_so_0` bị gán vào cụm "log10" thay vì "quên n = 0": các cụm digits kém thuần.
