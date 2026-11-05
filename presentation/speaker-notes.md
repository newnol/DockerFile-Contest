# Ghi chú thuyết trình — 9Router từ Alpine sang Wolfi

Bản cập nhật 20 slide. Giữ các giải thích nền tảng của bản cũ, chuyển kết luận thành thử nghiệm có đánh đổi. Bản cũ được lưu ở archive-before-evidence-update/. Không dùng notes cũ của slide 11/14/15/16 để nói tình trạng hiện tại.

## 1. Alpine → Wolfi

Mở từ câu hỏi CTF: image thực sự chứa gì? Chúng ta không trình diễn khai thác; ta hiểu artifact để đóng gói đúng. Thesis mới là dung lượng, tương thích và bảo mật có đánh đổi. Build xanh không đồng nghĩa tối ưu.

## 2. Tách đúng phiên bản

DockerFile-Contest/main là lab Python. newnol/9router-wolfi là packaging-only. Main checkout 0.5.112, có bằng chứng build/smoke/publish riêng ở run 41964645341. Báo cáo mới trong bài thuộc nhánh 0.4.41, không gán kết quả sang main.

## 3. Filesystem layers

Layer lưu thay đổi filesystem; merged view khác artifact từng lớp. Không phải mọi chỉ thị Dockerfile đều tạo filesystem layer chứa dữ liệu. Ít layer không mặc nhiên nhỏ hay nhanh.

## 4. Xóa chưa mất

Xóa ở layer sau không thu hồi bytes lớp trước. Tạo–dùng–dọn cùng bước hoặc giữ intermediate ngoài runner. Không dùng xóa sau làm cơ chế bảo vệ secret.

## 5. Thứ tự COPY

Manifest trước source giúp cơ hội dùng cache. Packaging hiện cài npm không có lockfile được COPY ở bước đó, nên không gọi là dependency hoàn toàn khóa. Không hứa tăng tốc chưa đo.

## 6. Hai lớp cache

Layer hit có thể bỏ qua RUN; cache mount giữ download khi RUN vẫn chạy. GHA layer cache không mặc nhiên đồng nghĩa mount được khôi phục giữa runner. Phân biệt cold/warm và điều kiện cache.

## 7. Tách giai đoạn

Builder giữ compiler; runner chỉ nhận artifact cần thiết. Standalone không tự thay thế kiểm tra custom server, native module và lazy runtime dependency. Multi-stage không tự bảo đảm nhỏ.

## 8. Chọn nền tảng

Wolfi đã được dùng, không còn chỉ là đề xuất. Workload quyết định compatibility. Cùng apk không có nghĩa trộn package Alpine/Wolfi. Không tuyên bố zero CVE hoặc trust chỉ vì digest.

## 9. Runtime tối thiểu

Non-root và least privilege đã có cấu hình. ffmpeg hoặc lazy dependencies không tự là rác. Smoke ghi/restart marker không chứng minh named volume sau recreate hoặc media chức năng đầy đủ.

## 10. Khóa nguồn vào

Source/base pin giúp truy vết, không khóa mọi dependency. Renovate quản lý thay đổi qua PR, không tự chứng minh CI hoặc reviewer đã chấp nhận. Chi tiết PR trên slide là snapshot lịch sử bản cũ, không tuyên bố trạng thái live.

## 11. Grype đã chạy

Run 41969796033 thuộc 0.4.41 đã scan đúng image sau smoke, upload grype-results và publish. Artifact gốc đã tải lại qua nightly.link và SHA256 khớp metadata GitHub. Grype 0.118.0, DB built 2026-11-04T06:20:59Z. Đếm vulnerability matches, không tự gọi là số lỗi độc lập. Chưa có scan Alpine tương đương.

## 12. Kiểm chứng runtime

Bộ smoke main cũ có health/dashboard, UID, SQLite query, require modules và restart marker. Run 0.4.41 mới cũng có bước smoke success. Không mở rộng thành mọi chức năng đã pass; chưa có kiểm thử live provider, media, named volume recreate hoặc shutdown timing đầy đủ.

## 13. Kiểm thử động

Strix chưa chạy; chỉ là nhánh đánh giá tùy chọn cần phạm vi riêng, lab cách ly và dữ liệu giả. Không có finding ứng dụng mới nào được khẳng định trong bài.

## 14. Pipeline có scan thật

Checkout pin → build → smoke exact image → Grype JSON → tag/push tested image. Nhánh 0.4.41 có scan thật. Workflow dùng fail-on medium nhưng xử lý exit 2 để findings không chặn publish; lỗi scanner vẫn khác finding. Không gọi pipeline xanh là qua security gate chặn severity.

## 15. Kết quả quan sát ban đầu

Đây là snapshot run cũ, không phải kết quả mới nhất. Docker Hub API tag 0.4.41 linux/amd64 trả size 168816869 bytes = 168.82 MB decimal ≈161.00 MiB. Vì vậy số 161 trên UI không nên ghi đơn vị MB rồi chia cho Wolfi 642.13 MB để ra 3.99 lần.

Grype source.target.imageSize = 642131628 bytes. Chưa xác minh trường này cùng định nghĩa với registry nén, nên không tính tỷ lệ hai phía. Raw manifest trong cùng report có tổng layer size khác (653895168 bytes), củng cố yêu cầu không đồng nhất các trường size. Build khác thời điểm, tập dependency có thể khác. Cold/warm, startup/RAM chưa benchmark; smoke và publishing chỉ là bằng chứng đúng phạm vi.

## 16. Layer nào chiếm chỗ?

Report cũ có 24 layer. Decode config history, bỏ empty_layer, ghép theo thứ tự với metadata layer. Next riêng 192489756 bytes; ffmpeg/libstdc++ và thư mục 171571449; nodejs-22 135571915; standalone 58762327; sql.js 31132473; phần còn lại khoảng 52.61 MB. Ba bước đầu 77.81% imageSize. Dữ liệu ghép nằm ở evidence/layer-history.json. Không gọi đây là registry compressed size đã đối chứng.

## 17. 17 matches cần phân loại

Report cũ có High 3, Medium 7, Low 1, Unknown 6. 11 ID CVE và 6 ID GHSA, không coi là 17 lỗi độc lập vì alias có thể trùng vấn đề. Node 22.23.2-r1 có 12 matches, fix version báo 22.23.4-r0. ffmpeg-9.0 9.0.2-r9 có 5, không chỉ ra fix version. Unknown không phải an toàn; cần triage applicability.

## 18. Đã bỏ COPY next riêng

Commit 52c69a291eb4bb76157c8be57160eee43b1099cb bỏ COPY toàn bộ node_modules/next riêng, giữ standalone. Run 41986499721 hoàn thành success trong khi cập nhật bài. Đã tải báo cáo mới và xác thực ZIP hash theo artifact metadata.

Cùng trường Grype imageSize: 642131628 → 449641868 bytes, giảm 192489760 bytes ≈192.49 MB, 29.98%. Đây là thay đổi quan sát giữa hai artifact, phù hợp với layer Next bị bỏ; không coi là thử nghiệm đơn biến hoàn toàn vì dependency build có thể thay đổi. Smoke pass không là tương đương chức năng đầy đủ.

## 19. Run mới đã thành công

Job 127108360812 thuộc run 41986499721 / packaging commit 52c69a2. API xác nhận build upstream, build Wolfi, compare local size, smoke, scan, upload và publish đều success.

Grype mới 0.118.0 dùng DB built 2026-11-05T06:21:06Z, khác DB cũ. 18 matches: High 4, Medium 7, Low 1, Unknown 6. Package distribution: Node 12, ffmpeg 5, glibc-2.44 2.44-r13 một match; 12 có fix version, 6 chưa có. Không quy tăng 17→18 cho thay đổi Dockerfile vì DB thay đổi.

Workflow mới rebuild upstream và Wolfi cùng upstream commit/amd64/runner, caches tách riêng, so docker image inspect .Size local unpacked bytes. Chưa trích được giá trị upstream local từ job summary vào hồ sơ này; không bịa con số hoặc dùng Grype thay cho nó. Build order/cache/network ảnh hưởng timing; duration job không là benchmark cold/warm. Smoke và Grype ở workflow này chỉ áp dụng Wolfi, chưa là đối chứng bảo mật/chức năng hai phía.

## 20. Đo → sửa → kiểm chứng

Chốt ba việc: kiểm tra runtime rộng hơn sau bỏ Next riêng; triage Node/ffmpeg/glibc và scan cùng DB; đối chứng cùng revision/arch/size definition/workload. Kết quả tốt nhất của bài không phải lời hứa Wolfi thắng mọi mặt, mà là biết đọc kết quả trái kỳ vọng và thiết kế vòng thử tiếp theo.

## Nguồn mới và provenance

- https://github.com/newnol/9router-wolfi/actions/runs/41969796033
- https://github.com/newnol/9router-wolfi/actions/runs/41986499721/job/127108360812
- https://github.com/newnol/9router-wolfi/commit/52c69a291eb4bb76157c8be57160eee43b1099cb
- https://hub.docker.com/v2/repositories/decolua/9router/tags/0.4.41
- ZIP cũ SHA256 604cd72699f6ad8e8f4fa1d9f3a90f6dbc5dfc6a44a5b874c54f01d433c9a4b4.
- ZIP mới SHA256 79d184df582a3b57e5f26f00eeefd505ec91bffbc8f1219d123314a0483367c9.
- Cả hai khớp digest GitHub artifact metadata. JSON gốc, ZIP, API snapshots, Dockerfile/workflow pinned và history được lưu trong evidence/.
- Không build, publish hay scan lại từ máy này; chỉ đọc bằng chứng CI và render presentation local.
