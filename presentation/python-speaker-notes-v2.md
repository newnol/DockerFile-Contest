# Tối ưu Dockerfile — lời dẫn Python contest (bản 3)

Người trình bày: Ngô Tấn Tài (newnol). Khán giả: các anh đồng nghiệp senior. Dài khoảng 25 phút, 42 slide.

Số liệu: run `42057474702`, commit `9b49c07`. 3 recipe × 5 runner độc lập, báo cáo median (min–max). TOP 2 là bài của em, đã điều chỉnh một dòng `fastapi==0.120.4`.

Phân bổ thời gian: Mở đầu & CTF (1–4) ≈ 3 phút · Cơ chế (5–26) ≈ 11 phút · Thiết kế đo (27–30) ≈ 2 phút · Kết quả (31–37) ≈ 5 phút · Bài học (38–42) ≈ 4 phút.

## Slide 1 — Tối ưu Dockerfile

**Nói:** Hôm nay em dùng một ứng dụng FastAPI từ cuộc thi để nói về tối ưu Dockerfile. Image nhỏ đi thì ai cũng thấy, nhưng em muốn nhìn thêm: build lại có nhanh không khi sửa code, container có lên được không, và sau một năm thì image đó còn "sạch" không. Em sẽ đi từ cơ chế của layer, rồi tới số đo thật trên CI, rồi mới rút ra bài học.

## Slide 2 — Từ CTF

**Nói:** Em đến với chủ đề này từ CTF. Với bài web có Dockerfile dựng local, việc đầu tiên em làm là đọc Dockerfile: chạy bằng user nào, cài gì, COPY những file nào vào. Dockerfile nói khá nhiều về môi trường mà source sẽ chạy trong đó. Em giữ đúng cách đặt câu hỏi đó cho bài hôm nay.

## Slide 3 — Mở image

**Nói:** Mở một image ra, ngoài runtime và source còn có thể có compiler, cache tải package, hoặc file lỡ COPY từ build context như `.git`, `.env`. Đây là ví dụ minh hoạ, không phải phát hiện trong ba image đo hôm nay. Cách phòng là `.dockerignore`, và bí mật cần lúc build thì dùng secret mount, đừng COPY rồi xoá sau — vì xoá sau không lấy lại được byte, em sẽ nói ngay đoạn tới.

## Slide 4 — Ba cách đóng

**Nói:** Ba recipe, cùng một source. Default là bản mẫu: Alpine cộng uv, COPY tất cả trước rồi mới `uv sync`. TOP 1 build trên Debian slim, rồi chuyển Python, shared libs và venv sang Distroless. TOP 2 là bài của em: Alpine cộng pip, multi-stage, dọn khá mạnh; bản đo đã pin FastAPI 0.120.4, lý do em nói ở phần sau. Ba recipe khác nhau cả base lẫn dependency, nên em so cả recipe chứ không phải thử một biến.

## Slide 5 — Xếp từng lớp

**Nói:** Filesystem của image là chồng các lớp thay đổi. Base đã có lớp sẵn, mỗi RUN hoặc COPY ghi thêm một lớp phía trên. ENV, CMD, USER chủ yếu là metadata nên không tốn dung lượng đáng kể. Vì vậy đếm số dòng Dockerfile không cho biết image nặng bao nhiêu.

## Slide 6 — Nhìn hợp nhất

**Nói:** Khi vào container, em thấy một filesystem hợp nhất: file hiện ra ở một đường dẫn, nhưng không biết lớp nào đã thêm nó. Lớp trên không ghi đè byte của lớp dưới. Muốn lần ngược thì dùng `docker history`, `docker inspect`, hoặc Dive. Trong bộ dữ liệu này em có history và inspect, chưa có báo cáo Dive.

## Slide 7 — Thêm rồi xóa

**Nói:** Ví dụ: RUN đầu tải một archive và giải nén, RUN sau xoá archive. Vào container liệt kê file thì archive không còn, dễ tưởng nó đã biến mất. Đây là ví dụ cơ chế, em không gán con số MiB nào cho nó.

## Slide 8 — Byte vẫn còn

**Nói:** Thực ra archive vẫn nằm nguyên ở lớp A. Lớp B chỉ đánh dấu đường dẫn đó là đã xoá, nên ở góc nhìn cuối nó không hiện, còn byte vẫn nằm trong image và vẫn phải tải. Hệ quả: file tạm sinh ra ở một bước thì phải dọn ngay trong chính bước đó, hoặc không cho nó vào stage cuối.

## Slide 9 — Dọn cùng bước

**Nói:** Tải, dùng, xoá trong cùng một RUN thì file không đi vào lớp lưu lại. Cách khác là làm ở builder rồi chỉ chuyển artifact cần chạy sang stage cuối. Nhưng đừng vì vậy mà gộp mọi thứ thành một RUN khổng lồ. Em nhóm theo vòng đời dữ liệu: phần ít đổi tách khỏi phần hay đổi, để cache còn tác dụng, và đó là chuyện của các slide kế tiếp.

## Slide 10 — Source đổi trước

**Nói:** Default `COPY . .` toàn bộ context trước, rồi mới cài uv và `uv sync`. Source là thứ đổi hằng ngày, còn lockfile hiếm khi đổi. Cách xếp này đặt phần hay đổi lên quá sớm trong chuỗi.

## Slide 11 — Cache mất theo

**Nói:** BuildKit tính cache theo đầu vào từng bước. Source đổi một chữ thì kết quả `COPY . .` đổi, kéo theo mọi bước phía sau, kể cả cài dependency dù danh sách thư viện không đổi. Chỉ cần thêm một dòng comment cũng đủ. Đó là lý do build lại nguyên đầu vào nhanh không nói được gì về tốc độ lúc đang sửa code; lát nữa số đo sẽ cho thấy.

## Slide 12 — Đổi thứ tự

**Nói:** Cách sửa là đảo thứ tự: manifest và lockfile vào trước, cài dependency, rồi mới COPY source. Hai thứ có nhịp thay đổi khác nhau thì nằm ở hai chỗ khác nhau. TOP 1 bind riêng `uv.lock` và `pyproject.toml` cho bước sync, source chỉ COPY ở cuối. TOP 2 của em cũng khai báo dependency trước, source sau.

## Slide 13 — Cache được giữ

**Nói:** Giờ source đổi nằm sau bước cài dependency. Nếu đầu vào bước cài không đổi, BuildKit dùng lại kết quả; chỉ phần source và các bước phụ thuộc nó phải làm lại. Đây là chỗ khác biệt lớn nhất của Default so với hai recipe còn lại trong phần số đo.

## Slide 14 — Bỏ qua RUN

**Nói:** Khi đầu vào khớp, BuildKit bỏ qua RUN và log ghi CACHED. Em lưu ý: số dòng CACHED không phải số lớp, cũng không phải phần trăm công việc tiết kiệm. Còn khi RUN buộc phải chạy, bên trong nó vẫn có thể tận dụng một loại cache khác, là cache mount.

## Slide 15 — Tải lại ít

**Nói:** Cache mount giữ một thư mục riêng giữa các lần build; RUN vẫn chạy, nhưng công cụ cài package đỡ phải tải lại. Vùng mount không nằm trong image cuối. TOP 1 mount `/root/.cache/uv`. Trong bài đo, ba recipe không chia sẻ cache với nhau và không restore cache từ GitHub Actions; chỉ lượt cold của cùng job làm ấm cache cho warm và source-change.

## Slide 16 — Mount bị vô hiệu

**Nói:** Chỗ này em tự nhận lỗi của mình. Trong bài TOP 2, em mount `/root/.cache/pip` nhưng lại đặt `PIP_NO_CACHE_DIR=1` và truyền thêm `--no-cache-dir`. Pip không ghi gì vào thư mục đó, nên cache mount hoàn toàn không có tác dụng. Em đã có dòng mount trông rất đúng bài, nhưng không kiểm tra xem nó có chạy thật không. Bài học: thấy cấu hình cache không có nghĩa là có cache; phải đọc log hoặc đo. Với apk cũng tương tự, em mount cache mà lại dùng `apk --no-cache`.

## Slide 17 — Builder cần gì

**Nói:** Builder cần compiler, header, uv hoặc pip, dữ liệu tải package — những thứ để tạo ra môi trường ứng dụng chứ không phải để chạy nó. Multi-stage cho phép stage cuối bắt đầu từ một base riêng; thứ chỉ có trong builder không tự xuất hiện ở runtime, em chủ động chọn cái gì COPY sang.

## Slide 18 — Chuyển artifact

**Nói:** TOP 1 chuyển Python, standard library, vài shared lib bổ sung và venv sang Distroless. TOP 2 chuyển thư mục `/install` sang Python Alpine rồi thêm source. Default thì không chuyển gì cả, vì chỉ có một stage. Vẽ mũi tên `COPY --from` thì dễ, nhưng quyết định mũi tên mang theo gì mới là thứ định hình runtime.

## Slide 19 — Runtime giữ gì

**Nói:** Runtime phải có interpreter, dependency, source và đúng những shared lib thực sự cần. Thiếu thư viện thì lỗi ngay lúc import; thiếu package data hay metadata thì có khi chỉ lộ ở một nhánh chức năng nào đó. Về user, theo `docker inspect`: TOP 1 chạy user 65532, TOP 2 chạy user app, Default không khai báo USER nên là root. Em đọc đó là cấu hình thực tế, không phải chứng nhận bảo mật.

## Slide 20 — Chọn base image

**Nói:** Alpine dùng musl, Debian dùng glibc, Distroless bỏ gần hết tiện ích trong runtime. Default và TOP 2 chạy Alpine, TOP 1 chạy Distroless Debian 12. Em không chọn chỉ vì base nhỏ. Với Python có native extension, wheel có sẵn hay không quyết định có phải compile hay không, và TOP 2 chính là ví dụ: nó cài `build-base`, `cargo` rồi compile, nên cold build rất chậm, số liệu sẽ cho thấy.

## Slide 21 — Kiểm tra tương thích

**Nói:** Em kiểm tra wheel đúng nền và kiến trúc, shared lib mà Python hoặc extension cần, rồi import và gọi thử request. Với Distroless thì nên chuẩn bị sẵn luồng debug, đừng đợi sự cố mới đi tìm shell. Số đo hôm nay chỉ có linux/amd64. TOP 1 có nhánh arm64 trong Dockerfile, nhưng viết ra chưa phải đã chạy đạt.

## Slide 22 — Tag có đổi

**Nói:** Tag là con trỏ có thể trỏ sang nội dung mới. Giữ nguyên dòng FROM, build vào thời điểm khác vẫn có thể ra base khác. Default dùng tag trôi như vậy, ngay cả uv cũng không pin phiên bản. Tag tiện để theo một dòng phiên bản, nhưng không đủ để truy lại một lần build cụ thể.

## Slide 23 — Digest giữ nội dung

**Nói:** Pin theo digest thì nội dung base được chốt. TOP 1 pin cả builder và runtime, TOP 2 của em cũng pin base theo digest. Nhờ vậy truy vết rõ hơn, build lặp lại ổn định hơn. Nhưng đừng vội thấy yên tâm, slide sau có hai lý do vì sao pin chưa đủ.

## Slide 24 — Pin chưa hết

**Nói:** Thứ nhất, pin base mới là một phần đầu vào: TOP 1 sync theo lockfile rồi còn cài riêng Starlette 0.49.1, TOP 2 pin mỗi FastAPI còn lại phần lớn là khoảng phiên bản. Thứ hai, pin thì phải có lịch cập nhật. Digest của em chốt từ tháng 11 năm 2025 và không bao giờ được build lại. Em sẽ cho các anh thấy cái giá của việc đó ở slide CVE.

## Slide 25 — Strip bỏ gì

**Nói:** Strip loại thông tin trong binary, không phải nén file. TOP 2 chạy `strip --strip-all` trên các `.so` và `.a` trong `/install`, kèm `|| true` để bỏ qua lỗi. Lệnh chạy qua không có nghĩa mọi file đã strip thành công, hay mọi đường chạy vẫn đúng. Với runtime smoke thì qua, nhưng em chỉ có kết quả đó.

## Slide 26 — Dọn có giá

**Nói:** TOP 2 còn xoá `.dist-info`, license, tài liệu và một số phần standard library. Mất debug info thì chẩn đoán khó hơn, mất metadata có thể ảnh hưởng lúc chạy, và license còn có nghĩa vụ phân phối riêng. Em chưa tách từng nhóm dọn ra để đo lợi ích, nên 65 MiB là của cả recipe, không phải của riêng strip. Đến đây em chuyển sang cách đo.

## Slide 27 — Chốt điều kiện

**Nói:** Ba recipe dùng cùng commit `9b49c07`, build linux/amd64 trên GitHub Actions ubuntu-24.04, mỗi recipe 5 lần. Container chạy giới hạn 1 CPU, 512 MiB, PORT=5000, WORKERS=1. Em muốn nói rõ đây là một lần đo lại hôm nay, không phải bảng chấm của cuộc thi năm 2025. Các số cũ như 105 MB, 0 CVE, 1,5 giây là đo trên Mac arm64 hồi đó, em không dùng lại.

## Slide 28 — Ba lượt build

**Nói:** Mỗi recipe build ba lượt. Cold: builder mới, `--pull --no-cache`. Warm: lặp lại nguyên đầu vào. Source-change: chỉ thêm một dòng comment vào file Python, không đổi chức năng. Đồng hồ bao quanh buildx có `--load`, nên tính cả bước export image nhưng không tính dựng builder.

## Slide 29 — 15 runner riêng

**Nói:** 3 recipe nhân 5 lần là 15 job, mỗi job một runner GitHub riêng, nên nhiễu về phần cứng và mạng nằm ngay trong dải min–max. Lý do em lặp 5 lần là để nhìn được độ phân tán chứ không tin một mẫu. Em báo median và để dải min–max ngay cạnh. Phần cài đặt gói giống hệt nhau qua 5 lần của mỗi recipe.

## Slide 30 — Gom bằng chứng

**Nói:** Mỗi job upload artifact: history, inspect, log build, kết quả runtime smoke, rồi một job riêng gom lại thành bảng so sánh. Runtime smoke qua 5/5 cho cả ba recipe. Cần nói rõ phần không đo: không gọi API thật (Coffee API trỏ vào stub cục bộ), không đo tải hay throughput, không tách từng kỹ thuật, và không đo thời gian pull từ registry.

## Slide 31 — Kích thước image

**Nói:** Dung lượng không nén: Default 200,50 MiB, TOP 1 101,82, TOP 2 65,46. Gzip của `docker save`, em dùng làm xấp xỉ dung lượng truyền: 87,9, 32,9 và 22,9 MiB. Kích thước gần như không đổi giữa các lần. TOP 2 của em nhỏ nhất, chỉ khoảng một phần ba Default. Nhưng nhỏ là một chiều; các slide sau cho thấy cái giá.

## Slide 32 — Nhỏ chưa nhanh

**Nói:** Cold build: Default 12,86 giây (11,84–14,26), TOP 1 9,23 (8,68–10,61), TOP 2 23,30 (20,04–26,62). Bài của em nhỏ nhất nhưng build lạnh chậm nhất, khoảng gấp đôi Default, vì phải cài `build-base` và `cargo`, compile package, rồi strip. Dải của TOP 2 không chồng lên hai recipe còn lại, nên khác biệt này là thật. Image nhỏ chưa chắc build nhanh.

## Slide 33 — Build có cache

**Nói:** Build lại nguyên đầu vào: Default 0,75 giây, TOP 1 0,41, TOP 2 0,49. Cả ba đều dưới một giây vì mọi bước đều CACHED, nên lượt này gần như không phân biệt được recipe. Đừng lấy nó làm tiêu chí.

## Slide 34 — Khi sửa source

**Nói:** Đây mới là trường hợp thường ngày. Chỉ thêm một comment: Default mất 9,50 giây, TOP 1 0,475, TOP 2 0,839. Default build lại gần như từ đầu vì `COPY . .` đứng trước `uv sync`, đúng như em nói ở slide 10 và 11, nên cài lại toàn bộ dependency. TOP 1 và TOP 2 của em chỉ chạy lại phần source, nhanh hơn Default khoảng mười lần. Đây là lợi ích rõ nhất của việc xếp thứ tự lớp.

## Slide 35 — Container đã lên

**Nói:** Startup tính từ `docker run` đến khi `/health/` báo healthy và trang chủ render, poll mỗi 0,5 giây: Default 2,39 giây, TOP 1 2,32 (1,69–2,50), TOP 2 3,08 (2,25–3,38). Do độ phân giải poll 0,5 giây, chênh dưới khoảng nửa giây không có ý nghĩa, và dải của ba recipe chồng lên nhau. Em chạy lại thêm hai lượt 15 job (run 42058703830 và 42059152289): median startup của TOP 2 thành 2,84 rồi 2,24 giây, thứ tự đổi giữa các lượt, nên em không xếp hạng startup. Thời gian stop khoảng 0,35 giây cho cả ba.

## Slide 36 — RAM khi rỗi

**Nói:** RAM 5 giây sau khi lên: Default 55,1 MiB, TOP 1 54,3, TOP 2 48,4. Chênh khoảng 6 MiB và dải của TOP 2 (48,1–48,6) tách khỏi hai recipe còn lại, nhưng đây là RAM khi rỗi, một worker, chưa có request. Em không suy ra gì về lúc chịu tải.

## Slide 37 — CVE sau một năm

**Nói:** Em chạy Trivy 0.76.2 một lần cho mỗi recipe hôm nay, 5/11/2026. Default: 2 critical, 17 high; toàn bộ 70 lỗ hổng nằm ở package Python của `uv.lock` cũ, còn lớp OS sạch. TOP 1: 3 critical, 19 high; khoảng 69 ở Debian 12 và 66 ở Python. TOP 2 của em: 2 critical, 27 high; trong đó 112 nằm ở package Alpine 3.22.2 như openssl, musl, zlib, vì base pin digest từ tháng 11 năm 2025 và không được build lại; chỉ 5 ở package Python. Tức là việc nâng dependency hồi thi có tác dụng, nhưng pin digest mà không cập nhật thì base già đi. Bài nộp của em từng ghi 0 CVE, đó là ảnh chụp một ngày. Em không nói những CVE này khai thác được; một con số đếm chưa phải rủi ro.

## Slide 38 — Request mới biết

**Nói:** Smoke test chỉ chứng minh container lên và trả được trang. Nó không phải test chức năng, không phải load test. Cái lỗi dưới đây cho thấy vì sao: image build thành công không có nghĩa ứng dụng chạy đúng.

## Slide 39 — FastAPI lệch phiên bản

**Nói:** Bản TOP 2 nguyên gốc để `fastapi` không pin phiên bản trong lúc cài. Khi pip tự resolve ra FastAPI 0.162 thì `prometheus-fastapi-instrumentator` hỏng, và run 41990729849 là lần fail gốc. Đây là lỗi của em: submission lúc đó chạy được vì tình cờ resolve ra bản cũ. Pin lỏng thì build hôm nay có thể khác build năm ngoái.

## Slide 40 — Pin rồi thử

**Nói:** Em sửa đúng một dòng: `fastapi==0.120.4`, và đó là bản đã đo hôm nay. Vì vậy nói "bài của em" ở đây là bài đã điều chỉnh một dòng, không phải nguyên bản. Sau khi pin, runtime smoke qua 5/5. Em dùng cùng cách này cho lần sau: pin, build, chạy thử request.

## Slide 41 — Đọc đúng số

**Nói:** Mấy điều em muốn các anh nhớ khi đọc bảng. Một, em so cả recipe, base và dependency khác nhau nên không tách được kỹ thuật nào đóng góp bao nhiêu. Hai, median kèm dải; chênh trong dải nhiễu thì không kết luận. Ba, gzip là xấp xỉ transfer size. Bốn, CVE chỉ là một lần quét hôm nay, và số đếm không phải rủi ro. Năm, em chưa đo API thật, tải, hay thời gian pull.

## Slide 42 — Đo rồi chọn

**Nói:** Tóm lại ba bài học. Thứ nhất, thứ tự lớp quyết định tốc độ lúc sửa code: Default 9,5 giây so với dưới một giây. Thứ hai, nhỏ chưa nhanh: TOP 2 nhỏ nhất nhưng cold chậm nhất, và cache mount của em không hoạt động vì tự tắt cache pip. Thứ ba, pin phải đi kèm cập nhật: digest cũ và FastAPI không pin đều cho em thấy cái giá. Hoàn hảo thì không có, nên chọn theo thứ mình cần: tốc độ CI, kích thước, hay độ tươi của base. Em xin hết, mời các anh hỏi.

## Câu hỏi có thể gặp

**Vì sao lặp 5 lần?** Mỗi lần là một runner riêng nên phần cứng và mạng khác nhau. 5 lần đủ để thấy độ phân tán và loại trường hợp xa bất thường; em báo median kèm min–max, không tuyên bố ý nghĩa thống kê.

**Vì sao TOP 2 phải điều chỉnh?** FastAPI 0.162 làm hỏng `prometheus-fastapi-instrumentator` khi pip tự resolve. Em chỉ thêm đúng một dòng pin `fastapi==0.120.4`. Lần fail gốc là run 41990729849.

**Vì sao bài nộp ghi 0 CVE mà giờ có CVE?** 0 CVE là ảnh chụp tại thời điểm đó, đo trên Mac arm64. Hôm nay Trivy cho TOP 2 khoảng 112 lỗi ở Alpine 3.22.2 vì digest cũ không được rebuild; ở package Python chỉ còn 5.

**Gzip có bằng dung lượng trên registry không?** Không hoàn toàn. Em gzip kết quả `docker save`, chỉ là xấp xỉ; registry nén theo từng layer và có thể ra số khác.

**Vì sao không tách từng kỹ thuật?** Mục tiêu là so các recipe hoàn chỉnh như người ta nộp. Tách từng kỹ thuật cần thí nghiệm riêng, em chưa làm, nên không quy kết tốc độ hay dung lượng cho kỹ thuật nào.

**Bài này có đo hiệu năng khi chạy thật không?** Không. API ngoài trỏ vào stub, không có tải hay throughput; chỉ là smoke test đóng gói.
