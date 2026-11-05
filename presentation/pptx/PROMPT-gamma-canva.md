# Prompt tạo slide trên Gamma / Canva Magic Design / Copilot

Dán toàn bộ khối dưới đây vào công cụ, chọn **16:9** và **tiếng Việt**. Sau khi tạo xong, soát lại từng con số theo `measurement-data/github-42057474702/comparison/comparison.md`.

```text
Tạo một bài thuyết trình kỹ thuật 26 slide, tỉ lệ 16:9, tiếng Việt, cho buổi chia sẻ nội bộ 25 phút với các anh kỹ sư senior.

CHỦ ĐỀ: "Tối ưu Dockerfile: nhỏ hơn, nhanh hơn, vẫn phải chạy đúng" – case study Python/FastAPI từ Dockerfile Contest 2025.
NGƯỜI TRÌNH BÀY: Ngô Tấn Tài (newnol). Xưng "em". Bài "TOP 2" là bài dự thi của chính người trình bày – ghi rõ "bài em".

PHONG CÁCH:
- Hiện đại, kỹ thuật, sạch. Nền sáng #F6F7F9 cho slide nội dung, nền navy #0B1F3A cho slide mở đầu, chuyển phần, kết luận.
- Màu nhấn: xanh Docker #2496ED. Màu cố định cho 3 recipe, dùng nhất quán ở mọi biểu đồ: Mặc định #7C8BA1, TOP 1 #2E9E6B, TOP 2 (bài em) #F06A35.
- Font sans-serif hỗ trợ tiếng Việt (Be Vietnam Pro, Inter hoặc Segoe UI). Code dùng font monospace trên khung terminal tối.
- Mỗi slide tối đa 1 ý chính, ít chữ, ưu tiên sơ đồ, biểu đồ, icon. Dùng logo Docker, Python, Alpine Linux, Debian, Trivy, Renovate, GitHub Actions.
- Hiệu ứng: chuyển slide fade; các thẻ/cột xuất hiện lần lượt theo click.

QUY TẮC BẮT BUỘC VỀ SỐ LIỆU:
- KHÔNG làm tròn, KHÔNG suy diễn, KHÔNG thêm số nào ngoài danh sách dưới đây.
- Biểu đồ phải vẽ đúng các giá trị đã cho. Mọi slide kết quả ghi chú nguồn: "Run 42057474702 · median 5 runner".
- Không viết "0 CVE", "an toàn tuyệt đối", "nhanh nhất" nếu số liệu không nói vậy.

DÀN Ý TỪNG SLIDE:
1. Tiêu đề (nền navy): "Tối ưu Dockerfile" · phụ đề "Nhỏ hơn · Nhanh hơn · Vẫn phải chạy đúng" · tên người trình bày · logo Docker + Python.
2. Lộ trình 25 phút, 5 thẻ: 01 Từ CTF (3′) · 02 Cơ chế (11′) · 03 Đo lường (2′) · 04 Kết quả (5′) · 05 Bài học (4′).
3. "Từ CTF: image không chỉ chứa app" – khung terminal (docker run -it … sh; id → root; ls -a → .env .git; which curl wget gcc) + 3 thẻ rủi ro: File thừa · Tool có sẵn · Quyền dư.
4. "Cùng một source, ba cách đóng gói" – 3 thẻ:
   Mặc định (docker-example.txt): uv:python3.13-alpine, COPY . . rồi uv sync, 1 stage, chạy root.
   TOP 1: builder bookworm-slim + uv → runtime distroless (không shell), non-root.
   TOP 2 · bài em: python:3.13-alpine @digest, pip --prefix, strip .so, xóa tests/docs, user 10001, pin fastapi==0.120.4 (sửa 1 dòng).
5. Chuyển phần (navy): "01 · Cơ chế: layer & cache".
6. "Image là các lớp xếp chồng" – sơ đồ 4 khối chồng từ dưới lên: FROM python:3.13-alpine → COPY pyproject.toml uv.lock → RUN install → COPY src/. Ghi chú: RUN/COPY tạo layer; ENV/CMD là metadata; layer cũ không bị sửa.
7. "Xóa ở bước sau ≠ image nhỏ đi" – so sánh 2 cột: hai lệnh RUN (file 50 MB vẫn ở layer 1, chỉ "whiteout") vs một lệnh RUN tải-dùng-xóa. Ghi "50 MB là ví dụ minh họa". Tự nhận: bài em dọn stdlib/pip ở RUN riêng nên phần đó gần như không giảm size.
8. "Thứ tự COPY quyết định cache" – 2 khung code: COPY . . → RUN uv sync (chạy lại) vs COPY manifest → RUN uv sync (CACHED) → COPY src. Số lớn: 9.50 s → 0.48 s khi chỉ sửa source.
9. "Có cache mount chưa chắc đã dùng được" – Layer cache vs cache mount; trích bài em: ENV PIP_NO_CACHE_DIR=1 + --mount=type=cache + --no-cache-dir → mount không có tác dụng.
10. "Multi-stage" – sơ đồ: Stage builder (build-base, gcc, cargo, pip install --prefix, strip) → COPY --from /install → Runtime (python + site-packages + src, user 10001).
11. "Chọn base: nhỏ chưa chắc nhanh" – 3 cột: Alpine (musl, có thể build wheel từ source) · Debian slim (glibc, wheel manylinux) · Distroless (không shell, khó debug).
12. "Tag có thể đổi · digest thì không" – python:3.13-alpine vs python:3.13-alpine@sha256:e5fa…; cảnh báo digest cũng "già" đi; giải pháp Renovate + CI rebuild.
13. Chuyển phần: "02 · Đo thế nào cho công bằng".
14. "3 recipe × 5 runner song song trên CI" – 5 thẻ: cùng commit 9b49c07 · linux/amd64 ubuntu-24.04 · 1 CPU / 512 MiB · 5 runner/recipe, báo median (min–max) · mỗi job: cold → warm → sửa source → chạy → Trivy. (Chừa chỗ chèn ảnh chụp trang GitHub Actions.)
15. "Chạy đúng nghĩa là request trả đúng" – GET /health/ → heartbeat HEALTHY; GET / → "Dockerfile Contest 2025". Kết quả: 15/15 PASS. Ghi chú: Coffee API là stub, đây là smoke test.
16. Chuyển phần: "03 · Kết quả".
17. Biểu đồ cột ngang nhóm "Kích thước image (MiB)":
    Chưa nén: Mặc định 200.5 · TOP 1 101.8 · TOP 2 bài em 65.5
    Nén gzip (≈ dung lượng tải): 87.9 · 32.9 · 22.9
    Tiêu đề: "Bài em nhỏ nhất: 65.5 MiB (−67%)".
18. Biểu đồ "Cold build (giây, median và min–max)": Mặc định 12.9 (11.8–14.3) · TOP 1 9.2 (8.7–10.6) · TOP 2 bài em 23.3 (20.0–26.6). Tiêu đề: "Nhỏ nhất ≠ build nhanh nhất". Giải thích: Alpine + musl cần build-base, cargo.
19. Biểu đồ nhóm "Build lại (giây)": Không đổi gì – 0.75 · 0.41 · 0.49; Thêm 1 dòng comment – 9.50 · 0.48 · 0.84. Số lớn "20×".
20. "RAM rõ ràng · startup không xếp hạng": cột RAM rỗi 55.1 · 54.3 · 48.4 MiB. Bảng startup median 3 lượt (giây): Mặc định 2.39 / 2.82 / 2.82; TOP 1 2.32 / 2.26 / 2.28; TOP 2 3.08 / 2.84 / 2.24. Ghi chú: thứ tự đổi giữa các lượt, polling 0.5 s.
21. Biểu đồ cột chồng "Trivy 0.76.2, ngày 05/11/2026 – số phát hiện theo tầng":
    Mặc định: OS 0, Python 70 (Critical 2, High 17)
    TOP 1: OS 69, Python 66 (Critical 3, High 19)
    TOP 2 bài em: OS 112, Python 5 (Critical 2, High 27)
    Ghi chú: "số lượng phát hiện ≠ mức độ rủi ro".
22. Timeline "'0 CVE' là ảnh chụp của một ngày": 11/2025 nộp bài, 0 CVE → digest Alpine 3.22.2 không đổi → 11/2026 quét lại 117 phát hiện, 112 ở OS. Bài học: pin digest + Renovate/CI rebuild + scan trên pipeline.
23. "Container lên ≠ request chạy đúng" – terminal: curl → 500 Internal Server Error; AttributeError: '_IncludedRouter' object has no attribute 'path'. 3 thẻ: Nguyên nhân (fastapi>=0.116.0 không cận trên → kéo 0.162) · Sửa (pin fastapi==0.120.4 → 15/15 PASS) · Bài học (lock + test request).
24. "Đọc đúng số trước khi kết luận" – 3 thẻ: 5 mẫu/recipe, 3 lượt chạy · so nguyên recipe, không tách từng kỹ thuật · chưa đo live API, tải, thời gian pull.
25. Kết luận (navy): "Nhỏ hơn là một số đo. Tối ưu là một kết luận có điều kiện." – 3 số lớn: −67% kích thước · 20× build lại nhanh hơn · 112 CVE ở base cũ.
26. "Cảm ơn các anh · Q&A" – github.com/newnol/DockerFile-Contest.

Thêm speaker notes ngắn (2–4 câu, giọng nói tự nhiên, xưng "em") cho từng slide, dựa đúng vào nội dung trên.
```

## Sau khi tạo

- Chèn ảnh từ `presentation/pptx/assets/`: `ci-run.png` (slide 14), `app-home.png` (slide 15), các file logo `logo-*.png`.
- Đối chiếu biểu đồ slide 17–21 với `comparison.md`. Các công cụ AI hay tự làm tròn số hoặc đổi thứ tự cột.
