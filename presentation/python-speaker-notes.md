# Tối ưu Dockerfile — lời dẫn trình bày Python contest

Bản lời nói dành cho 20 slide, khoảng 25 phút tùy tốc độ nói và phần hỏi đáp. Xưng “mình” để dùng trực tiếp; có thể đổi thành “em” theo người nghe. Các dòng **Hình / thao tác**, **Chuyển** và **Bằng chứng** là chỉ dẫn cho người trình bày, không cần đọc nguyên văn.

Giữ mạch giảng của `Thuyet_trinh_Dockerfile_Optimize.docx` và `Dockerfile_Optimize_CTF_Agenda.html`: CTF → nhìn vào image → layers và cache → build/runtime, base, pin, strip → đo và kiểm chứng. Phần cuối thay ví dụ V1/V2 chưa đo bằng bốn recipe Python đã chạy CI thật. Không dùng số liệu hoặc đề xuất 9Router.

**Quy tắc đọc số:** kết quả rebuild tại run `41992840188`, commit `35be0461710f3f907d1c6e1fd54de68d1f915ea8`; không phải kết quả chấm thi năm 2025. Dung lượng là MiB local chưa nén, thời gian tính bằng giây. TOP 2 luôn được hiểu là **bản điều chỉnh, pin FastAPI 0.120.4**. `top-entry3` là mục Python TOP hiển thị thứ ba trên trang ban tổ chức, **không phải xác nhận hạng 3**. Các phần trăm được tính từ dữ liệu thô bằng Python, không trừ các số MiB đã làm tròn.

## Slide 1 — Tối ưu Dockerfile

**Lời nói**

Hôm nay mình chia sẻ cách tối ưu Dockerfile qua một ứng dụng Python. Nhưng câu hỏi không chỉ là làm sao cho image nhỏ nhất. Mình muốn biết trong image có những gì, phần nào cần cho ứng dụng chạy, phần nào chỉ phục vụ lúc build, và mỗi thay đổi có đánh đổi gì.

Mình sẽ đi từ cách nhìn image khi làm CTF, giải thích layers và cache, rồi đối chiếu với số liệu CI thật của bốn cách đóng cùng source. Điều kiện đầu tiên vẫn là ứng dụng phải chạy qua bài kiểm tra đã định nghĩa. Sau đó mới bàn đến dung lượng, thời gian build và khả năng duy trì. Riêng bảo mật, lần chạy này không có scan CVE mới, nên mình không đưa ra con số CVE hay kết luận image nào an toàn nhất.

**Hình / thao tác:** chỉ từ Dockerfile qua image đến container; đặt ba câu hỏi cạnh mũi tên: “mang gì?”, “build thế nào?”, “chạy được không?”. Không mở đầu bằng bảng xếp hạng.

**Chuyển:** “Vì sao mình lại bắt đầu quan tâm đến những thứ nằm bên trong image?”

**Bằng chứng:** [O1], [O2] cho mạch kể; [E1], [E2] cho phạm vi phép đo và giới hạn bảo mật.

## Slide 2 — Từ CTF

**Lời nói**

Khi làm một bài web CTF có Dockerfile để dựng môi trường local, mình không chỉ nhìn source của web. Dockerfile còn cho biết ứng dụng chạy bằng user nào, cần những thư viện nào, và thứ gì được mang vào môi trường chạy. Từ góc nhìn đó, image không còn là một cái hộp đen.

Câu hỏi hữu ích khi quay lại công việc đóng gói là: nếu một file hay công cụ không cần lúc chạy, tại sao nó còn nằm trong image? Ví dụ, lịch sử source, log hoặc bí mật bị COPY nhầm có thể tạo rủi ro lộ thông tin. Đây là ví dụ giả định để giải thích tư duy, không phải kết luận rằng bốn image hôm nay chứa những file đó; mình cũng không gán câu chuyện cho một challenge cụ thể chưa có bằng chứng.

Bớt công cụ thừa là một lớp giảm bề mặt tiếp xúc, không phải cơ chế đảm bảo container không thể bị xâm nhập. Có shell không có nghĩa là tự động leo thang quyền; không có shell cũng không thay thế việc giới hạn quyền, mount, mạng và bảo vệ bí mật. Từ CTF, điều mình giữ lại là thói quen kiểm tra những gì mình đưa vào sản phẩm.

**Hình / thao tác:** đi từ “challenge local” đến cây filesystem và ô USER. Nếu có hình `.env` hoặc `.git`, nói rõ đó là minh họa; không mở hay đọc file bí mật.

**Chuyển:** “Để kiểm tra tư duy đó, mình lấy một ứng dụng và nhìn bốn cách đóng gói khác nhau.”

**Bằng chứng:** [O1], [O2] cho bối cảnh gốc; [D1], [D5] cho kiểm soát build context và bí mật. Không có log CTF được dùng làm bằng chứng thực nghiệm.

## Slide 3 — Bốn cách đóng

**Lời nói**

Bốn cột này là bốn recipe, không phải bốn phép thử chỉ khác đúng một dòng. Default là cách đóng trong `docker-example.txt`: base uv trên Alpine, COPY toàn bộ context rồi mới sync dependencies. TOP 1 dùng builder Debian Bookworm slim và runtime distroless, chuyển Python, thư viện dùng chung và môi trường ảo sang stage chạy.

TOP 2 dùng Alpine nhiều stage, cài dependencies riêng rồi dọn khá mạnh. Bản mình đo ở đây đã pin FastAPI về 0.120.4 vì bản gốc gặp lỗi khi chạy request; mình sẽ quay lại lỗi đó ở phần cuối. Cột còn lại là `top-entry3`: mục Python được trang tổ chức ghi là “TOP”, hiển thị thứ ba. Mình không gọi nó là hạng 3. Recipe này dùng Debian slim, build wheels rồi cài offline vào runtime.

Cả bốn dùng cùng commit source trong lần CI này, nhưng base và tập phiên bản dependencies khác nhau. Vì vậy mình có thể so sánh trải nghiệm của cả recipe, không thể nói mọi chênh lệch đều do multi-stage, Alpine hay distroless. Cùng source chưa đủ để gọi đây là cùng một môi trường phần mềm.

**Hình / thao tác:** lần lượt chỉ bốn đường source → dependencies → runtime; gắn nhãn “đã điều chỉnh” ngay trên TOP 2 và “TOP, mục thứ ba” trên `top-entry3`.

**Chuyển:** “Trước khi đọc kết quả, mình cần một mô hình đúng về cách image giữ dữ liệu.”

**Bằng chứng:** [E3]–[E6] là bốn Dockerfile; [S1] là trang tổ chức; [E8] lưu nhãn và hash nguồn. [E2] nêu rõ đây là so sánh whole recipes.

## Slide 4 — Image layers

**Lời nói**

Có thể hình dung filesystem của image là những lớp thay đổi chồng lên nhau. RUN hoặc COPY ghi thay đổi filesystem vào các lớp; những chỉ thị như ENV, CMD hay USER chủ yếu cấu hình metadata. Không phải cứ đếm số dòng Dockerfile là biết có bao nhiêu lớp dữ liệu hoặc image nặng bao nhiêu.

Điểm quan trọng là lớp trước đã tạo ra thì lớp sau không sửa lại trực tiếp. Khi chạy container, mình nhìn thấy một filesystem hợp nhất, nên có thể không nhận ra dữ liệu nào vẫn nằm ở lớp phía dưới. Docker history giúp nối các thay đổi với lệnh build; image inspect cho biết danh sách layer và dung lượng image theo cách đo của Docker.

Trong dữ liệu thật, default có 9 filesystem layers, TOP 1 có 21, TOP 2 điều chỉnh có 12 và mục TOP thứ ba có 9. Nhưng TOP 1 vẫn nhỏ hơn default. Đây là ví dụ rất rõ: số lớp không phải đại diện cho tổng byte. Mình cần hỏi mỗi lớp chứa gì, thay vì coi ít layer hơn là tự động tốt hơn.

**Hình / thao tác:** lần lượt xếp base, dependencies, source; đặt ENV/CMD ra ngoài chồng filesystem. Chỉ con số 21 và 9 để bác bỏ cách đánh giá chỉ bằng đếm layer.

**Chuyển:** “Tính bất biến của lớp giải thích một chuyện rất dễ gặp: đã xóa file mà image vẫn không nhỏ đi như mình tưởng.”

**Bằng chứng:** [E1] trường `layer_count`; [E7] bước lưu `history.jsonl` và `image-inspect.json`; [D1], [D6].

## Slide 5 — Xóa chưa nhỏ

**Lời nói**

Giả sử mình tải một archive trong RUN thứ nhất, giải nén rồi đến RUN sau mới xóa archive. Ở filesystem cuối không còn thấy file đó, nhưng byte của archive vẫn được giữ trong lớp đã tạo trước. Lớp xóa phía trên chỉ làm file không còn xuất hiện trong góc nhìn hợp nhất. Đây là ví dụ cơ chế, không phải một số MiB tiết kiệm đã được đo riêng trong bài này.

Cách xử lý với file tạm là tải, sử dụng và dọn trong cùng bước tạo nó; hoặc để toàn bộ quá trình đó ở builder rồi chỉ chuyển artifact cần thiết sang runtime. Nhưng không có nghĩa phải gộp mọi RUN thành một lệnh khổng lồ: làm vậy có thể khiến một thay đổi nhỏ buộc cả nhóm công việc chạy lại.

Có ví dụ ngay trong recipe mục TOP thứ ba. Nó COPY thư mục `/wheels` vào runtime ở một bước, rồi pip install và xóa `/wheels` ở RUN sau. Wheels biến mất ở filesystem cuối nhưng dữ liệu đã COPY vẫn ở lớp dưới. Đây là điểm cần kiểm tra bằng history hoặc Dive nếu muốn cải tiến recipe, không phải bằng chứng rằng toàn bộ chênh lệch dung lượng của recipe chỉ đến từ wheels. Bài này chưa tách và đo riêng phần đó.

**Hình / thao tác:** hai cột “COPY /wheels → RUN install + rm” và “không đưa file tạm vào lớp runtime”; tô mờ file đã xóa nhưng giữ lớp dưới. Không gắn dung lượng giả cho archive hoặc wheels.

**Chuyển:** “Vậy nên gộp hay tách bước build? Mình quyết định theo vòng đời dữ liệu và tần suất thay đổi.”

**Bằng chứng:** [E6] dòng 87–92; [E7] lưu history; [D1], [D6]. Chưa có phép đo ablation cho wheels.

## Slide 6 — Cache đúng chỗ

**Lời nói**

Ở ứng dụng Python, code thường đổi nhiều hơn danh sách dependencies. Nếu COPY toàn bộ source trước bước cài thư viện, một thay đổi source có thể làm bước cài đặt không còn dùng lại được cache. Mình đang nối hai thứ có tần suất thay đổi khác nhau vào cùng một chuỗi phụ thuộc.

Cách bố trí thường dùng là đưa manifest và lockfile vào trước, cài dependencies, rồi mới đưa source vào. Nếu chỉ sửa code thì phần cài thư viện có cơ hội được dùng lại. Default của bài này COPY toàn bộ context trước `uv sync`; TOP 1 chỉ bind `uv.lock` và `pyproject.toml` cho bước sync, còn COPY source ở cuối runtime. TOP 2 điều chỉnh khai báo dependencies trước, sau đó mới COPY source.

Recipe mục TOP thứ ba có bước tạo wheels dependencies tách riêng, nhưng cũng build wheel của chính project sau khi COPY source. Đổi source có thể làm artifact của project thay đổi và kéo theo cài lại ở runtime. Vì thế mình cần theo toàn bộ đường phụ thuộc, không chỉ kiểm tra có một dòng “COPY manifest trước” hay chưa. Phần kết quả sửa source sẽ cho thấy sự khác biệt này.

**Hình / thao tác:** so hai chuỗi COPY source → install và manifest/lock → install → source. Dùng màu cache hit cho phần không phụ thuộc code; đánh dấu project wheel ở nhánh thứ ba.

**Chuyển:** “Khi nói cache, còn một chỗ dễ nhầm: dùng lại cả bước build khác với chỉ dùng lại file đã tải.”

**Bằng chứng:** [E3] dòng 4–10; [E4] dòng 38–42, 68; [E5] dòng 26–36, 89; [E6] dòng 49–55, 87–92; [D2].

## Slide 7 — Hai loại cache

**Lời nói**

Layer cache là khi đầu vào của một bước không đổi và BuildKit dùng lại kết quả, không chạy lại lệnh đó. Cache mount thì khác: RUN vẫn có thể phải thực thi, nhưng có sẵn các file package đã tải trong vùng cache để tái sử dụng. Một cái tiết kiệm việc làm lại cả bước; cái kia có thể tiết kiệm tải và xử lý bên trong bước.

TOP 1 mount `/root/.cache/uv` cho bước cài dependencies. TOP 2 có mount thư mục pip nhưng đồng thời đặt `PIP_NO_CACHE_DIR=1` và truyền `--no-cache-dir`. Vì vậy không nên thấy cú pháp mount rồi mặc định là pip đang dùng nó hiệu quả. Với `apk --no-cache` cũng cần kiểm tra hành vi thực tế thay vì suy ra từ tên thư mục mount.

Trong phép đo này, lần cold chạy trên builder mới; warm và source-change dùng lại builder của chính recipe đó. Cache mount được tạo trong cold có thể còn có ích ở các lần sau trong cùng job. Không có cache được chia sẻ giữa bốn recipe hay khôi phục từ GitHub Actions. Số dòng CACHED trong log là dấu vết để đọc, không phải phần trăm công việc được tiết kiệm hay số layer của image.

**Hình / thao tác:** bên trái là RUN bị bỏ qua; bên phải là RUN vẫn chạy, lấy package từ cache mount. Chỉ cặp mount pip và `--no-cache-dir` của TOP 2 để đặt câu hỏi kiểm chứng, không tuyên bố số giây mà mount tiết kiệm.

**Chuyển:** “Cache giải quyết việc build lại. Còn để không mang đồ nghề build đi cùng ứng dụng thì mình tách stage.”

**Bằng chứng:** [E4] dòng 38–42; [E5] dòng 13–27; [E2], [E7] về phạm vi cache; [D2].

## Slide 8 — Tách build runtime

**Lời nói**

Multi-stage là ranh giới giữa môi trường tạo ra ứng dụng và môi trường chạy ứng dụng. Builder có thể cần compiler, công cụ cài package hoặc cache. Stage cuối bắt đầu từ một base khác và chỉ nhận các artifact mình chủ động COPY sang. Những thứ chỉ nằm ở builder không tự động trở thành byte của runtime image.

TOP 1 chuyển interpreter Python, các thư viện hệ thống cần bổ sung, standard library và môi trường ảo sang distroless. TOP 2 chuyển `/install` sang Python Alpine rồi COPY source. Mục TOP thứ ba chuyển wheels và cài offline. Cả ba đều nhiều stage, nhưng bộ dữ liệu được chuyển và những lớp tạo trong runtime không giống nhau, nên multi-stage không đảm bảo kết quả nhỏ hơn theo một tỷ lệ cố định.

Điều khó là chuyển đủ nhưng không chuyển thừa. Thiếu shared library có thể làm native extension không import được; thiếu package data hoặc metadata có thể chỉ lộ ra ở một nhánh chức năng. User non-root cũng là một phần cấu hình runtime cần kiểm tra: TOP 1 inspect ra user 65532, TOP 2 là app, mục TOP thứ ba là 10001:10001; default không khai báo USER trong kết quả inspect. Các thông tin đó không đủ để tự mình chứng minh toàn bộ chính sách bảo mật khi triển khai.

**Hình / thao tác:** khoanh compiler/cache ở builder; chỉ mũi tên artifact đi sang runtime. Với TOP 1, tách rõ Python, `.venv` và shared libraries để người nghe thấy trách nhiệm tương thích.

**Chuyển:** “Ranh giới stage còn phụ thuộc nền bên dưới: mình chọn base theo nhu cầu chạy, không theo số MB của base một mình.”

**Bằng chứng:** [E4] dòng 14–25, 49–68; [E5] dòng 57–89; [E6] dòng 60–92; [E1] trường `configured_user`; [D3].

## Slide 9 — Chọn base image

**Lời nói**

Alpine thường được chọn vì nền nhỏ, nhưng nó dùng musl. Debian slim dùng glibc; distroless giảm các công cụ tiện ích trong môi trường chạy. Với Python có native extensions, câu hỏi là có wheel tương thích không, nếu phải compile thì tốn gì, và shared libraries nào phải có lúc chạy. Base nhỏ chưa chắc dẫn đến build lạnh nhanh hoặc tổng image nhỏ nhất cho mọi workload.

Trong bốn recipe, default và TOP 2 điều chỉnh thuộc nhánh Alpine. TOP 1 build trên Bookworm slim rồi chạy distroless Debian 12. Mục TOP thứ ba dùng `python:3.13-slim`. Wolfi cũng là một lựa chọn có thể khảo sát, như tài liệu gốc đã nhắc tới, nhưng không nằm trong bốn phép đo này nên mình không đặt nó lên bảng kết quả.

Đổi nền còn tác động đến cách debug và cập nhật. Distroless cần chuẩn bị luồng chẩn đoán phù hợp thay vì trông chờ có shell bên trong. Với bất kỳ base nào, mình vẫn phải test đúng kiến trúc và dependency thực tế. Kết quả hôm nay chỉ có linux/amd64; dù Dockerfile TOP 1 có nhánh cho arm64, mình không dùng phép đo amd64 để khẳng định arm64 đã chạy đạt.

**Hình / thao tác:** ba nhánh Alpine/musl, Debian slim/glibc, distroless/runtime; nối nhánh builder slim → runtime distroless. Wolfi nếu xuất hiện phải đặt ngoài vùng “đã đo”.

**Chuyển:** “Chọn được base chưa xong; mình còn cần biết lần sau đang build đúng đầu vào nào.”

**Bằng chứng:** [E3]–[E6] các chỉ thị FROM; [E1] trường `platform`; [O1] phần base; [D1], [D7].

## Slide 10 — Pin đầu vào

**Lời nói**

Một tag có thể trỏ sang nội dung mới theo thời gian. Pin bằng digest giúp chỉ định nội dung base mình chọn, nhưng không tự động khóa mọi đầu vào khác: dependencies Python, công cụ build, package hệ điều hành và nguồn tải vẫn cần được quản lý. Ngược lại, pin xong mà không cập nhật thì có thể giữ luôn một bản cũ cần vá.

TOP 1 pin cả builder và runtime theo digest, nhưng sau `uv sync --frozen` lại cài riêng Starlette 0.49.1 với `--no-deps`. Vì thế chỉ nhìn chữ frozen rồi nói toàn bộ môi trường trùng nguyên lockfile là không đúng. TOP 2 pin base theo digest, nhưng ngoài FastAPI 0.120.4 đã điều chỉnh thì nhiều dependencies vẫn là khoảng phiên bản. Default và mục TOP thứ ba còn dùng base tag có thể thay đổi.

Điều mình muốn lưu là source commit, Dockerfile chính xác, hash recipe, base reference và danh sách package thực tế sau build. Digest là công cụ truy vết và tái lập một phần đầu vào, không phải chứng chỉ bảo mật. Quy trình tốt là cập nhật có chủ đích, build, test và lưu bằng chứng mới, chứ không đóng băng vĩnh viễn.

**Hình / thao tác:** tag ở hai thời điểm có thể trỏ khác nội dung; digest trỏ cố định. Bên dưới thêm chuỗi “base + dependencies + source + tooling”; highlight lệnh Starlette riêng của TOP 1.

**Chuyển:** “Sau khi khóa và truy vết đầu vào, vẫn còn những cách giảm byte mạnh hơn — nhưng chúng có giá.”

**Bằng chứng:** [E4] dòng 1, 41–42, 49; [E5] dòng 11, 28–36, 57; [E8] hash recipe; [D1] về pin và cập nhật.

## Slide 11 — Strip có giá

**Lời nói**

Strip tác động lên thông tin trong file binary, không phải là cách nén mọi loại file. Ví dụ với ELF, `--strip-debug` và `--strip-all` không giống nhau. Những phần hỗ trợ debug hoặc bảng symbol có thể bị loại bỏ tùy chế độ và loại file; các phần cần cho thực thi, liên kết động vẫn phải đúng. Vì vậy không nên mô tả strip là cứ xóa mọi symbol mà chương trình luôn chạy bình thường.

TOP 2 chạy `strip --strip-all` trên các file `.so*` và `.a` trong `/install`, đồng thời bỏ qua lỗi bằng `|| true`. Sau đó recipe còn giảm `.dist-info`, xóa license, tài liệu và một số phần standard library. Mỗi nhóm này có rủi ro riêng: chẩn đoán sự cố, package discovery, dữ liệu dùng lúc chạy hoặc nghĩa vụ thông báo license. Không phải cứ gọi tên file là test hay docs thì đã chắc chắn mọi ứng dụng đều không dùng nó.

Lần CI hiện tại cho thấy bản TOP 2 điều chỉnh qua smoke test, nhưng chưa đo riêng mỗi bước dọn giúp giảm bao nhiêu byte, cũng chưa kiểm hết tác động đến mọi chức năng. Mình không lấy con số 65.42 MiB để kết luận riêng strip tiết kiệm bao nhiêu. Nếu làm tiếp, mình sẽ bật hoặc tắt từng nhóm dọn, giữ các đầu vào khác và chạy test tương ứng; đó mới là cách xác định lợi ích có đáng đánh đổi không.

**Hình / thao tác:** minh họa các phần `.text`, `.dynsym`, `.symtab`, `.debug_*`; tô phần có thể bị bỏ theo chế độ, không đánh dấu toàn bộ symbols là có thể xóa. Bên cạnh chia ba rủi ro: strip, metadata/license, stdlib.

**Chuyển:** “Từ đây, mình chuyển từ giải thích cơ chế sang cách đo: trước hết phải chốt điều kiện so sánh.”

**Bằng chứng:** [E5] dòng 39–52, 94–116; [O1] phần strip và ba chỗ cần kiểm tra; [D8]. Không có ablation hay kiểm chứng tuân thủ license trong workflow.

## Slide 12 — Đo công bằng

**Lời nói**

Bảng kết quả gắn với một run và một commit cụ thể, không phải những con số cũ trên bài viết cuộc thi. Cả bốn recipe lấy cùng source commit, build cho linux/amd64 trên runner GitHub Actions ubuntu-24.04. Nhưng mỗi recipe có runner riêng; cùng loại runner không có nghĩa là cùng máy, cùng đường mạng hay cùng trạng thái hạ tầng.

Mỗi recipe được lấy một mẫu cho từng chế độ. Cold dùng builder mới và `--pull --no-cache`; warm lặp lại đầu vào không đổi trên chính builder ấy; source-change chỉ nối thêm một comment Python vào `app.py`. Đồng hồ bao quanh lệnh buildx có `--load`, nên thời gian gồm export/load image, không gồm thiết lập builder. Cold ở đây là không dùng lại layer cache của builder cũ, không phải bảo đảm mọi cache ở registry hay hạ tầng mạng trên thế giới đều trống.

Runtime được kiểm tra sau chuỗi build, tức image cuối là image sau thay đổi comment không chức năng. Container bị giới hạn 1 CPU, 512 MiB RAM, ép PORT=5000 và WORKERS=1 để dễ đối chiếu. Đây là chuẩn hóa có chủ đích, không phải chạy nguyên mọi giá trị mặc định của bài dự thi. Và vì dependencies cùng base khác nhau, kết quả là so sánh cả recipe, không phải thí nghiệm cô lập một kỹ thuật.

**Hình / thao tác:** đọc ba ô cold → warm → comment-only. Đặt chân chú “n=1 mỗi chế độ/recipe; runner riêng; gồm export/load”. Tách giới hạn CPU/RAM runtime khỏi tài nguyên runner build.

**Chuyển:** “Bốn job chạy song song giúp mình thu kết quả độc lập, nhưng cũng đặt giới hạn cho cách đọc thời gian.”

**Bằng chứng:** [E7] dòng 36–49, 64–78; [E9] workflow; [E1], [E2].

## Slide 13 — Build song song

**Lời nói**

Workflow dùng matrix gồm default, top1, top2 và top-entry3, cho tối đa bốn job chạy song song và tắt fail-fast. Mỗi job thiết lập builder, chạy ba chế độ build theo thứ tự, kiểm tra runtime rồi lưu artifact. Job tổng hợp chờ các nhánh và đọc result JSON để dựng bảng chung.

Điểm mình thích ở cách tổ chức này là lỗi ở một recipe không làm mất bằng chứng của các recipe khác. Artifact vẫn được yêu cầu tải lên với `if: always()`. Nhưng trạng thái job CI thành công chưa đủ để nói runtime thành công: script có thể ghi runtime failed vào JSON rồi kết thúc phần thu thập. Mình phải đọc trường kết quả và log, không chỉ nhìn dấu tích xanh.

Chạy song song ở đây là song song bốn phép đo trên các runner khác nhau, không phải chứng minh một image build nhanh gấp bốn lần. Mình cũng không cộng thời gian các recipe rồi gọi đó là thời gian chờ của cả workflow. Với chỉ một mẫu, ảnh hưởng pull base, tải package và export vẫn còn; những thứ này cần lặp lại nếu muốn có kết luận hiệu năng ổn định.

**Hình / thao tác:** bốn làn runner độc lập, mỗi làn cold → warm → source → runtime → artifact; gom về compare. Đánh dấu runtime status nằm bên trong artifact chứ không chỉ trên badge job.

**Chuyển:** “Bây giờ mình đọc từng loại kết quả, bắt đầu từ dung lượng image.”

**Bằng chứng:** [E9] dòng 14–20, 26–45; [E7] dòng 69–99, 102–119; [E2].

## Slide 14 — Kích thước image

**Lời nói**

Default là 200.51 MiB. TOP 1 là 101.82 MiB, giảm 49.22% so với default. TOP 2 điều chỉnh là 65.42 MiB, giảm 67.37%. Mục TOP hiển thị thứ ba là 207.48 MiB, lớn hơn default 3.48%. Các tỷ lệ này tính từ số byte thô; MiB trên biểu đồ chỉ làm tròn để đọc.

Đây là dung lượng local chưa nén từ Docker image inspect, không phải số byte tải xuống registry hay dung lượng chiếm thêm khi máy đã chia sẻ sẵn nhiều layer. Vì vậy mình không dùng bảng này để hứa thời gian pull giảm theo đúng một tỷ lệ tương ứng. Cũng không lấy con số MB lịch sử của cuộc thi để ghép với phép đo hiện tại.

Hai điều đáng nhớ là recipe nhiều stage vẫn có thể lớn hơn baseline, và image có nhiều layer hơn vẫn có thể nhỏ hơn. Với mục TOP thứ ba, cách đưa wheels vào runtime là một chỗ có thể khảo sát; với TOP 2, dọn mạnh là một đánh đổi cần kiểm chứng. Bảng này cho biết kết quả cuối của cả recipe, chưa cho biết từng kỹ thuật đóng góp riêng bao nhiêu.

**Hình / thao tác:** biểu đồ thanh cùng trục bắt đầu từ 0, thứ tự default, TOP 1, TOP 2 điều chỉnh, TOP mục thứ ba. Đọc MiB và phần trăm; không đổi nhãn thành MB.

**Chuyển:** “Nhỏ hơn là một trục. Khi build từ đầu thì thứ tự có còn giống vậy không?”

**Bằng chứng:** [E1] trường `image_bytes`; [E2] bảng tổng hợp; [C1] công thức tỷ lệ. Không có phép đo registry compressed size.

## Slide 15 — Build lạnh

**Lời nói**

Trong mẫu cold này, default mất 14.640 giây, TOP 1 mất 11.850 giây, TOP 2 điều chỉnh mất 22.579 giây và mục TOP thứ ba mất 34.172 giây. So với default, TOP 1 ít hơn 2.790 giây, tức 19.06%; TOP 2 nhiều hơn 7.939 giây, tức 54.23%; mục TOP thứ ba nhiều hơn 19.532 giây, tức 133.42%.

Nếu chỉ nhìn dung lượng, mình có thể nghĩ TOP 2 là lựa chọn thắng trên mọi mặt. Nhưng ở cold build mẫu này, nó nhỏ nhất mà không nhanh nhất. Các bước tải base, giải dependencies, build hoặc cài package, dọn artifact và export/load đều có thể góp vào thời gian. Recipe và dependencies khác nhau, nên chưa thể quy toàn bộ phần chậm hơn cho Alpine, strip hay một lệnh cụ thể.

Mình cố ý nói “trong mẫu này”. Chỉ một lần đo trên runner độc lập không cho mình khoảng dao động hay độ tin cậy thống kê. Nếu quyết định vận hành dựa vào cold build, bước tiếp theo là lặp nhiều lần, cố định đầu vào và đọc log từng bước. Điều kết quả hiện tại đủ để bác bỏ là giả định “image nhỏ nhất chắc chắn build lạnh nhanh nhất”.

**Hình / thao tác:** thanh cold cùng đơn vị giây; dùng một dấu nối giữa “nhỏ nhất” ở TOP 2 và “không nhanh nhất”. Nhắc `--load` nằm trong đồng hồ.

**Chuyển:** “Nhưng hằng ngày mình thường sửa code hơn là build từ số không. Lúc đó cache mới bộc lộ rõ.”

**Bằng chứng:** [E1] trường `builds.cold.seconds`; [E7] dòng 36–49; [C1] chênh lệch cold. Không có thống kê nhiều mẫu.

## Slide 16 — Sửa source

**Lời nói**

Ở lần warm không thay đầu vào, bốn thời gian lần lượt là default 0.712 giây, TOP 1 0.307 giây, TOP 2 điều chỉnh 0.553 giây và mục TOP thứ ba 0.894 giây. Những con số này cho thấy việc lặp lại nguyên đầu vào tận dụng cache tốt, nhưng đó chưa phải tình huống chỉnh code thường ngày.

Khi chỉ thêm một comment vào file ứng dụng, default lên 9.853 giây, TOP 1 là 0.491 giây, TOP 2 điều chỉnh là 0.928 giây và mục TOP thứ ba là 21.354 giây. So với default ở đúng chế độ source-change, TOP 1 ít thời gian hơn 95.02%, TOP 2 ít hơn 90.58%. Mục TOP thứ ba lại nhiều thời gian hơn 116.73%. Đây là tỷ lệ của mẫu đo, không phải lời hứa mọi lần sửa tính năng đều nhanh tương ứng.

Kết quả phù hợp với cấu trúc đã xem: default đặt source trước cài dependencies; TOP 1 và TOP 2 tách phần dependencies khỏi COPY source; recipe wheels còn phải build artifact project và xử lý các bước sau nó. Muốn giải thích chính xác thời gian nằm ở đâu thì mình mở log source-change, không suy ra chỉ từ tổng số giây. Bài thử chỉ đổi comment, không đổi lockfile, không thêm dependency và không kiểm chứng mọi loại thay đổi source.

**Hình / thao tác:** hai hàng warm/source-change, tô bước bị invalidated sau comment. Nhấn “comment-only” cạnh các phần trăm; đọc cả bốn giá trị, không chỉ hai cột tốt nhất.

**Chuyển:** “Cache tốt và image nhỏ vẫn chưa đủ. Bây giờ mình hỏi image đó có xử lý request được không.”

**Bằng chứng:** [E1] trường `builds.warm` và `builds.source-change`; [E7] dòng 41–49; [E3]–[E6]; [C1]. Log đầy đủ có trong thư mục artifact từng recipe.

## Slide 17 — Chạy mới tính

**Lời nói**

Ở run đang trình bày, cả bốn image đều PASS bài smoke. Cụ thể, script gọi `/health/`, parse JSON và yêu cầu heartbeat bằng HEALTHY; sau đó gọi homepage và tìm chuỗi “Dockerfile Contest 2025”. Đây mạnh hơn việc chỉ thấy container đang Running, vì ứng dụng có thể khởi động xong mà request vẫn trả lỗi.

Thời gian từ bắt đầu docker run đến khi cả hai kiểm tra đạt là default 2.370 giây, TOP 1 1.804 giây, TOP 2 điều chỉnh 2.849 giây và mục TOP thứ ba 1.897 giây. Con số đó gồm thao tác khởi chạy và nhịp polling, không phải latency xử lý một request hay benchmark throughput. Script nghỉ 0.5 giây giữa các lần probe chưa đạt, nên không nên diễn giải chênh lệch nhỏ như một tính chất chắc chắn của framework.

Mình ép 1 CPU, 512 MiB RAM, PORT=5000 và WORKERS=1. Coffee API được trỏ tới stub HTTP nội bộ: `/hot` trả status 200 và danh sách rỗng. Cách này tách kiểm tra đóng gói khỏi việc API bên ngoài đang sống hay chết, nhưng không kiểm chứng tích hợp live hoặc luồng có dữ liệu thật. PASS ở đây cũng không đồng nghĩa mọi endpoint, tải cao, native extension, Docker HEALTHCHECK hay vận hành doanh nghiệp đều đã được xác nhận.

**Hình / thao tác:** container → health JSON → homepage; nhánh coffee trỏ tới “stub /hot → []”, không vẽ cloud API như thể đã gọi live. Gắn 1 CPU/512 MiB và PORT/WORKERS vào khung test.

**Chuyển:** “Một lần chạy trước đã cho thấy vì sao phải test request, chứ không dừng ở build thành công.”

**Bằng chứng:** [E1] trường `runtime`, `startup_seconds`; [E7] dòng 15–19, 63–85; [E2]. Không có kiểm thử hiệu năng tải hay tích hợp API live.

## Slide 18 — Bài học dependency

**Lời nói**

TOP 2 nguyên bản dùng khoảng phiên bản FastAPI mở. Trong run trước, nó resolve FastAPI 0.162.0 cùng prometheus-fastapi-instrumentator 7.1.0. Container ghi application startup complete, nhưng request health trả 500. Traceback đi qua instrumentator, đọc `route.path` rồi gặp lỗi `'_IncludedRouter' object has no attribute 'path'`.

Để tiếp tục khảo sát cách đóng gói, lần chạy hiện tại thay đầu vào FastAPI thành đúng 0.120.4. Danh sách package sau build ghi Starlette 0.49.3 và instrumentator 7.1.0; bản điều chỉnh này qua health JSON và homepage. Mình ghi rõ thay đổi đó vì nếu âm thầm sửa rồi vẫn gọi kết quả là bản gốc, người nghe sẽ hiểu sai cả tính tái lập lẫn độ tương thích.

Bài học không phải “cứ hạ FastAPI là xong” hay “bản mới luôn lỗi”. Đây là một tổ hợp dependency cụ thể gặp lỗi trên đường xử lý request cụ thể. Pin bản biết chạy giúp khoanh vấn đề, nhưng chưa thay thế lockfile đầy đủ, kiểm tra tương thích khi nâng cấp và scan bảo mật mới. Mình không nói bản 0.120.4 đã được xác nhận không có CVE; workflow này không có dữ liệu để kết luận điều đó.

**Hình / thao tác:** hai nhánh “bản gốc: build được, request 500” và “đã điều chỉnh: FastAPI 0.120.4, smoke PASS”. Giữ nhãn adapted cạnh mọi con số TOP 2.

**Chuyển:** “Muốn phân biệt thay đổi thực sự với lời mô tả, mình cần lần ngược từ con số đến artifact.”

**Bằng chứng:** [F1] packages và container.log của run `41990729849`, dòng lỗi đầu tiên 7–23; [F2] packages hiện tại; [E5] dòng 30; [E2]. Không khẳng định tính tương thích toàn bộ hệ sinh thái.

## Slide 19 — Đọc bằng chứng

**Lời nói**

Khi có một con số trên slide, mình muốn người nghe tìm lại được từ nguồn nào ra. Điểm bắt đầu là run CI và commit. Từ đó mở `comparison.json` để lấy dữ liệu thô, `comparison.md` để đọc điều kiện đo, rồi vào artifact riêng của từng recipe. `result.json` chứa trạng thái; cold, warm và source-change log cho biết bước nào thực thi lại.

Để biết image thực sự có gì, mình đọc `image-inspect.json`, `history.jsonl` và `packages.json`. Để biết lỗi request nằm đâu, mình đọc `container.log` thay vì chỉ nhìn tên image hoặc nhãn “production-ready”. Nếu dùng Dive để xem từng layer thêm/xóa file gì, mình sẽ nói rõ đó là thao tác cần chạy trên đúng image. Lần này chưa có báo cáo Dive thực đo; hình Dive từ tài liệu cũ chỉ là minh họa cơ chế, không dùng làm số liệu wasted space.

Cũng phải đọc đúng ý nghĩa field. `last_probe_error` có thể còn giữ lỗi của lần probe đầu dù `runtime` cuối cùng là passed; script không xóa field cũ khi probe sau thành công. Ngược lại, `base_images` rỗng trong JSON không chứng minh image không có base đã pin: field này lấy RepoDigests của image local, không phải provenance của toàn bộ FROM. Còn label “trivy-passed” chỉ là một chuỗi trong recipe, không phải kết quả scan mới.

**Hình / thao tác:** chuỗi run → commit → recipe hash → result/log/inspect/packages. Tách “đã đo” khỏi “chưa đo”: registry compressed size, Dive wasted space, CVE, full equivalence. Không bịa screenshot terminal.

**Chuyển:** “Khi mỗi nhận định có đường dẫn kiểm tra được, mình mới có thể kết luận vừa đủ.”

**Bằng chứng:** [E7] dòng 55–62, 78–89, 99; [E1] trường `last_probe_error`, `base_images`; [E5] dòng 64; [D6].

## Slide 20 — Tối ưu có chứng

**Lời nói**

Sau bốn recipe, mình không chọn một người thắng chung cho mọi tiêu chí. Trong mẫu này, TOP 1 giảm khoảng một nửa dung lượng so với default và có cold, warm, source-change cùng startup thấp nhất trong bốn cột đã đo. TOP 2 điều chỉnh nhỏ nhất, giảm 67.37%, nhưng cold và startup không thấp nhất. Mục TOP thứ ba dùng multi-stage nhưng vẫn lớn hơn default và tốn nhiều thời gian hơn khi đổi comment.

Điều có thể mang về áp dụng không phải là chép nguyên một Dockerfile thắng giải. Đầu tiên là đặt cache theo phần ít thay đổi và phần hay thay đổi. Tiếp theo là tách công cụ build khỏi runtime, chọn base theo tương thích, truy vết đầu vào và thận trọng với các bước dọn mạnh. Sau mỗi thay đổi, mình kiểm tra request thật trong phạm vi bài test rồi đo lại đúng thứ mình quan tâm.

Nếu cần khẳng định ở mức triển khai thực tế, phần còn thiếu vẫn phải làm: lặp phép đo để thấy độ dao động, cố định và đối chiếu dependencies, kiểm thử chức năng rộng hơn, test với API live hoặc dữ liệu đại diện, kiểm tra license và scan CVE mới có thời điểm cùng phiên bản cơ sở dữ liệu. Kết luận hôm nay vừa đủ là: tối ưu tốt không chỉ có số MB đẹp, mà có đầu vào rõ, phép đo rõ và giới hạn được nói rõ.

**Hình / thao tác:** vòng “Inspect → Change → Test → Measure”; bên ngoài ghi “lưu bằng chứng”. Kết ở phương pháp, không gắn nhãn enterprise-ready hoặc zero-CVE cho recipe nào.

**Chuyển:** “Mình xin dừng ở đây. Mọi con số đều có nguồn bên dưới; mình sẵn sàng mở lại log nếu có câu hỏi về một bước cụ thể.”

**Bằng chứng:** [E1], [E2], [C1]; phương pháp gốc [O1], [O2]. Các kiểm tra bổ sung vừa nêu là việc chưa làm, không phải kết quả đã đạt.

# Nguồn và bằng chứng đầy đủ

## Tài liệu gốc và phạm vi sử dụng

- **[O1]** `Thuyet_trinh_Dockerfile_Optimize.docx`, trong thư mục gốc repository. Đã đọc toàn bộ nội dung: câu chuyện CTF; layers, xóa file, gộp/tách RUN, thứ tự COPY, hai loại cache, Dive; CVE, multi-stage, base, digest, strip; kiểm tra lại V1 và đo trước khi kết luận. Bản notes này rút về đúng 20 tiêu đề đã thống nhất, giữ phương pháp giảng thay vì giữ các ô “tự bổ sung” và bảng V1/V2 chưa đo.
- **[O2]** `Dockerfile_Optimize_CTF_Agenda.html`, trong thư mục gốc repository. Dùng để giữ cách giải thích bằng sơ đồ layers/cache và mạch CTF → kiểm chứng; không lấy mô phỏng Dive, ví dụ filesystem hoặc nhãn lịch sử làm bằng chứng thực nghiệm hiện tại. Không sửa HTML.
- **[S1]** Trang ban tổ chức: https://devops.vn/webinar/dockerfile-contest-2025/ . Nguồn các recipe Python TOP 1, TOP 2 và mục ghi “TOP” hiển thị thứ ba. Không xác nhận mục thứ ba là rank 3. Những tuyên bố lịch sử như 105 MB hoặc 0 CVE không được thay thế hay nhập vào phép đo mới.

## Run, source và dữ liệu thô

- **[E1]** Run chính: https://github.com/newnol/DockerFile-Contest/actions/runs/41992840188 . Commit: `35be0461710f3f907d1c6e1fd54de68d1f915ea8`. Dữ liệu gốc local: `measurement-data/github-41992840188/comparison/comparison.json`.
- **[E2]** Báo cáo có điều kiện đo: `measurement-data/github-41992840188/comparison/comparison.md`.
- **[E3]** Default: `benchmarks/dockerfiles/default.Dockerfile` tại commit trên; bản đọc tại `/home/taint73/.hermes/profiles/restored/cache/scratch/python-contest-comparison/benchmarks/dockerfiles/default.Dockerfile`. Nguồn ban đầu là `docker-example.txt`.
- **[E4]** TOP 1: `benchmarks/dockerfiles/top1.Dockerfile` tại commit trên; bản đọc trong cùng thư mục scratch.
- **[E5]** TOP 2 điều chỉnh: `benchmarks/dockerfiles/top2.Dockerfile` tại commit trên; thay FastAPI range bằng `fastapi==0.120.4`; bản đọc trong cùng thư mục scratch.
- **[E6]** Mục TOP hiển thị thứ ba: `benchmarks/dockerfiles/top-entry3.Dockerfile` tại commit trên; bản đọc trong cùng thư mục scratch.
- **[E7]** Script đo: `benchmarks/measure.py` tại commit trên; bản đọc tại `/home/taint73/.hermes/profiles/restored/cache/scratch/python-contest-comparison/benchmarks/measure.py`. Đã kiểm tra đường đo thời gian, thay đổi comment, inspect, thu package, stub và runtime probes.
- **[E8]** Metadata recipe: `benchmarks/sources.json` tại commit trên; bản đọc trong cùng thư mục scratch. Các SHA-256 bên dưới đã được tính lại từ byte của từng Dockerfile và khớp metadata, không chỉ chép từ mô tả.
- **[E9]** Workflow: `.github/workflows/benchmark.yml` tại commit trên; bản đọc tại `/home/taint73/.hermes/profiles/restored/cache/scratch/python-contest-comparison/.github/workflows/benchmark.yml`. Matrix 4 recipe, ubuntu-24.04, builder riêng, fail-fast false, upload artifact ngay cả khi bước trước lỗi.

Các đường dẫn source cố định có thể mở theo mẫu `https://github.com/newnol/DockerFile-Contest/blob/35be0461710f3f907d1c6e1fd54de68d1f915ea8/<đường-dẫn-file>`; chúng khác với working tree mặc định hiện tại của repository.

Artifact từng recipe nằm dưới `measurement-data/github-41992840188/benchmark-default/`, `benchmark-top1/`, `benchmark-top2/`, `benchmark-top-entry3/`. Trong mỗi thư mục, đối chiếu `result.json`, `cold.log`, `warm.log`, `source-change.log`, `image-inspect.json`, `history.jsonl`, `packages.json`, `container.log`, `container-inspect.json` và `stats.json` nếu có. `stats.json` chỉ là snapshot, không được dùng như kết quả benchmark tải trong bài trình bày.

## Bằng chứng lỗi và điều chỉnh TOP 2

- **[F1]** Run trước: https://github.com/newnol/DockerFile-Contest/actions/runs/41990729849 . Local: `measurement-data/github-41990729849/benchmark-top2/packages.json` ghi FastAPI 0.162.0 và instrumentator 7.1.0; `container.log` có `AttributeError: '_IncludedRouter' object has no attribute 'path'` và GET `/health/` trả 500. Log server startup thành công không phủ định lỗi request này.
- **[F2]** Local hiện tại: `measurement-data/github-41992840188/benchmark-top2/packages.json` ghi FastAPI 0.120.4, Starlette 0.49.3, prometheus-fastapi-instrumentator 7.1.0. `comparison.json` ghi runtime passed. Đây là bằng chứng smoke của bản điều chỉnh, không phải kết quả của nguyên bản.

## Bảng số dùng khi tập nói

| Recipe | Image MiB | Cold s | Warm s | Source-change s | Startup s | Smoke |
|---|---:|---:|---:|---:|---:|---|
| Default | 200.51 | 14.640 | 0.712 | 9.853 | 2.370 | PASS |
| TOP 1 | 101.82 | 11.850 | 0.307 | 0.491 | 1.804 | PASS |
| TOP 2 — điều chỉnh FastAPI 0.120.4 | 65.42 | 22.579 | 0.553 | 0.928 | 2.849 | PASS |
| TOP — mục Python hiển thị thứ ba | 207.48 | 34.172 | 0.894 | 21.354 | 1.897 | PASS |

**[C1] Công thức và kiểm tra số bằng Python:** `MiB = image_bytes / 1048576`; `giảm_size_% = (1 - bytes_recipe / bytes_default) * 100`; `tăng_thời_gian_% = (seconds_recipe / seconds_default - 1) * 100`; `giảm_thời_gian_% = (1 - seconds_recipe / seconds_default) * 100`. Tính từ JSON thô, chỉ làm tròn ở bước hiển thị. Các kết quả trung gian được lưu trong `python-sources.json` đi kèm để kiểm tra lại.

| Recipe | Giảm size so với default | Chênh cold (s) | Tăng cold | Giảm source-change |
|---|---:|---:|---:|---:|
| TOP 1 | 49.22% | -2.790 | -19.06% | 95.02% |
| TOP 2 — điều chỉnh | 67.37% | +7.939 | +54.23% | 90.58% |
| TOP — mục thứ ba | -3.48% | +19.532 | +133.42% | -116.73% |

Dấu âm ở cột “giảm” nghĩa là lớn/chậm hơn, không phải tiết kiệm. Một mẫu mỗi chế độ/recipe; không có median, độ lệch chuẩn hay ý nghĩa thống kê được tuyên bố.

### Hash recipe đã đối chiếu

- Default: `890f4d065737befb4e93bc401ab9e0638de303060fcd0a4ff4c00f594ecd4f5f`.
- TOP 1: `436ccdd77bd2f9ce312f9044b5a161524f26ff56497fe390cb6ea6f2052c42c7`.
- TOP 2 điều chỉnh: `fe3372eb07aa8e4d48c5264f1c8c72382e0d1e284cd689fb1d553445825e0416`.
- TOP 2 nguyên bản, theo metadata nguồn, không phải file đang đo: `dcc1eb2ecb5ef0aba200ac64e63528df008d42e6919aae77f2e31da8b924c2c9`.
- Mục TOP thứ ba: `88fd4d678ae9bcf4ce283523a352b590f527f969e237a5021eda2fcac24357c6`.

## Tài liệu kỹ thuật để giải thích cơ chế

Các liên kết sau là nguồn kỹ thuật tham khảo cho cơ chế, không phải nguồn số đo CI và không phải bằng chứng đã chạy thêm công cụ tại đây:

- **[D1]** Docker build best practices: https://docs.docker.com/build/building/best-practices/ . Build context, lựa chọn base, pin và cập nhật đầu vào.
- **[D2]** Docker cache optimization: https://docs.docker.com/build/cache/optimize/ . Thứ tự layer, bind mount và cache mount.
- **[D3]** Docker multi-stage builds: https://docs.docker.com/build/building/multi-stage/ . Chuyển artifact từ builder sang stage cuối.
- **[D5]** Docker build secrets: https://docs.docker.com/build/building/secrets/ . Không đưa bí mật vào image bằng COPY hoặc dùng ARG/ENV để thay thế cơ chế secrets mount.
- **[D6]** Dive: https://github.com/wagoodman/dive . Kiểm tra thay đổi filesystem theo layer; chưa có phép chạy Dive thực đo cho bốn image trong bộ dữ liệu này.
- **[D7]** Distroless: https://github.com/GoogleContainerTools/distroless . Phạm vi runtime image và lựa chọn debug image.
- **[D8]** GNU binutils strip: https://sourceware.org/binutils/docs/binutils/strip.html . Phân biệt các chế độ strip; phải kiểm thử trên artifact thực tế.

# Hỏi đáp dự kiến

**1. Vậy nên dùng recipe nào?**

Trong một mẫu này, TOP 1 cân bằng tốt giữa size và các thời gian đã đo; TOP 2 điều chỉnh ưu tiên size. Chọn để triển khai còn cần đối chiếu dependency, chức năng, debug, license, cập nhật và scan. Chưa có bằng chứng để gọi một recipe tốt nhất cho mọi ứng dụng.

**2. Tại sao TOP 2 không phải nguyên bản?**

Nguyên bản resolve FastAPI 0.162.0 với instrumentator 7.1.0 và health request lỗi `_IncludedRouter`. Bản đang báo cáo pin FastAPI 0.120.4, resolve Starlette 0.49.3 và smoke PASS. Nhãn “đã điều chỉnh” là bắt buộc; không ghi đè lịch sử lỗi.

**3. Vì sao mục TOP thứ ba lớn hơn cả default dù có multi-stage?**

Multi-stage không quyết định byte cuối; runtime vẫn nhận những thứ recipe COPY vào. Recipe này COPY wheels vào một layer rồi xóa ở RUN sau, đồng thời có base và dependencies khác. Đây là những điểm cần kiểm tra, chưa phải phân rã định lượng nguyên nhân của toàn bộ 207.48 MiB.

**4. Tại sao không gọi nó là TOP 3?**

Trang tổ chức chỉ ghi TOP cho mục đó. Thứ tự hiển thị không đủ để suy ra thứ hạng. Trong dữ liệu kỹ thuật giữ ID `top-entry3`, khi nói dùng “mục TOP hiển thị thứ ba”.

**5. Image nhỏ nhất có ít CVE nhất không?**

Không suy ra được từ size. Workflow hiện tại không scan CVE. Muốn so phải chạy scanner mới, lưu image identity, phiên bản scanner, thời điểm và phiên bản database; đọc findings chứ không tin label `trivy-passed`.

**6. Đã PASS là giữ nguyên chức năng chưa?**

Chưa. Chỉ xác nhận health JSON và homepage với coffee stub `/hot` trả `[]`, trong cấu hình runtime đã chuẩn hóa. Chưa kiểm toàn bộ endpoints, dữ liệu thật, metrics dưới tải, tích hợp live, license hoặc sự tương đương chức năng đầy đủ.

**7. Vì sao cold không chỉ là tốc độ compile?**

Đồng hồ bao quanh `docker buildx build --load`, gồm pull và xử lý build, export/load; setup builder nằm ngoài. Runner và mạng khác nhau, mỗi recipe một mẫu. Chưa có số đo riêng để gán toàn bộ thời gian cho compile.

**8. Có nên gộp tất cả RUN cho ít layer?**

Không. Gộp những thao tác tạo và dọn file tạm để không giữ byte thừa ở layer cũ. Tách phần ít đổi và phần hay đổi khi có lợi cho cache. Theo dữ liệu này, TOP 1 có 21 layers nhưng vẫn nhỏ hơn default 9 layers.

**9. Muốn xác nhận kết quả ổn định hơn thì làm gì trước?**

Lặp nhiều lần trong điều kiện kiểm soát, ghi phân bố thay vì chỉ một số; cố định các đầu vào có thể thay đổi, giữ riêng cold/warm/source-change. Nếu muốn biết một kỹ thuật giúp bao nhiêu, thay đúng kỹ thuật đó và giữ phần còn lại không đổi, thay vì so các whole recipe khác dependency.

**10. Có nên xóa license, metadata và stdlib để lấy thêm vài MiB?**

Không xóa chỉ vì tên có vẻ không cần. Cần xác định lợi ích bằng phép đo riêng, kiểm tra đường chạy dùng chúng và nghĩa vụ phân phối. Smoke test qua không chứng minh việc xóa đó an toàn hay đáp ứng license.
