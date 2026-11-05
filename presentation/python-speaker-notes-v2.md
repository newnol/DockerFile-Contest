# Tối ưu Dockerfile — lời dẫn Python contest, bản 2

40 slide theo mạch mở dần sơ đồ, dùng để nói khoảng 25 phút tùy nhịp và hỏi đáp. Đọc phần **Lời nói**; ba dòng còn lại là cue cho người trình bày. Mỗi slide là một trạng thái tiếp theo của hình, không phải lý do để nói lại toàn bộ hình trước. “Bấm” dưới đây là chỉ dẫn chuyển trạng thái/slide cho bản thiết kế mới, không khẳng định HTML cũ đã có hiệu ứng đó.

Số liệu rebuild: run `41992840188`, commit `35be0461710f3f907d1c6e1fd54de68d1f915ea8`. TOP 2 trong mọi số đo là **bản điều chỉnh FastAPI 0.120.4**; `top-entry3` là **mục TOP hiển thị thứ ba, chưa xác nhận hạng 3**. MiB là dung lượng local chưa nén; thời gian dùng giây. Phụ lục giữ nguồn, giới hạn phép đo và hỏi đáp để không phải ngắt lời nói bằng cùng một lưu ý ở mỗi hình.

## Slide 1 — Tối ưu Dockerfile

**Lời nói**

Mình dùng một ứng dụng Python để bàn về cách tối ưu Dockerfile. Image nhỏ đi là dễ thấy nhất. Nhưng mình còn muốn biết nó build lại ra sao khi sửa code, và ứng dụng bên trong có xử lý request được không. Bài này đi từ cách đọc image đến bốn recipe đã chạy CI, rồi mới chọn theo kết quả.

**Hình / thao tác:** hiện Dockerfile → image → container; chưa mở bảng số. Bấm chuyển sang bối cảnh CTF.

**Chuyển:** “Cách nhìn này bắt đầu từ việc đọc môi trường của một bài web CTF.”

**Bằng chứng:** [O1], [O2] cho mạch giải thích; [E1], [E2] cho dữ liệu hiện tại.

## Slide 2 — Từ CTF

**Lời nói**

Với bài web CTF có Dockerfile để dựng local, mình có thêm một cách đọc ứng dụng: nó chạy bằng user nào, cài thư viện gì, COPY những file nào vào trong. Dockerfile cho biết khá nhiều về môi trường mà source sẽ chạy.

Ở đây mình giữ cách đặt câu hỏi đó, không kể lại một challenge hay lần khai thác cụ thể chưa có log chứng minh.

**Hình / thao tác:** từ ô challenge local, mở Dockerfile và hai nhánh USER/COPY; giữ nguyên image để slide sau mở bên trong.

**Chuyển:** “Nhìn vào COPY, mình sẽ kiểm tra xem image thực sự mang theo gì.”

**Bằng chứng:** [O1], [O2]; bối cảnh CTF là phương pháp đọc, không phải kết quả pentest bốn image.

## Slide 3 — Mở image

**Lời nói**

Trong image có source và runtime, nhưng cũng có thể có compiler, cache tải package hoặc file đưa nhầm từ build context. `.git`, log hay `.env` trên hình chỉ là ví dụ giả định, không phải phát hiện trong bốn image này. Mình dùng `.dockerignore` để giới hạn context; bí mật cần cho build thì dùng secrets mount, đừng COPY rồi xóa sau.

Bỏ công cụ thừa giúp giảm phần phải mang theo. Có hay không có shell vẫn không thay được việc kiểm soát quyền, mount và mạng.

**Hình / thao tác:** mở image thành cây filesystem; phân nhóm runtime/build/file minh họa. Không mở file bí mật. Bấm thu cây thành bốn nhánh recipe.

**Chuyển:** “Cùng ứng dụng đó, bốn Dockerfile chọn mang theo những thứ khác nhau.”

**Bằng chứng:** [D1], [D5]; [O1], [O2] cho góc nhìn kiểm tra image.

## Slide 4 — Bốn cách đóng

**Lời nói**

Default dùng uv trên Alpine, COPY toàn bộ context rồi sync dependencies. TOP 1 build trên Bookworm slim, chuyển Python, shared libraries và venv sang distroless. TOP 2 dùng Alpine nhiều stage và dọn mạnh; bản đo đã pin FastAPI 0.120.4. Nhánh cuối dùng Debian slim, build wheels rồi cài offline. Trang tổ chức ghi nhánh đó là TOP, hiển thị thứ ba, nên mình không gọi là hạng 3.

Cả bốn lấy cùng commit source nhưng khác base và dependencies. Mình so cả recipe, không coi đây là phép thử chỉ đổi một biến.

**Hình / thao tác:** lần lượt hiện bốn đường source → dependencies → runtime. Giữ nhãn “điều chỉnh” trên TOP 2 và “TOP, mục thứ ba” trên nhánh cuối ở mọi hình kết quả.

**Chuyển:** “Muốn hiểu chúng khác nhau ở đâu, trước hết cần nhìn đúng cách image giữ dữ liệu.”

**Bằng chứng:** [E3]–[E6], [E8], [S1]; điều kiện so sánh [E2].

## Slide 5 — Xếp từng lớp

**Lời nói**

Filesystem của image được tạo từ các lớp thay đổi. Base đã có các lớp riêng; RUN hoặc COPY có thể ghi thêm thay đổi phía trên. ENV, CMD hay USER chủ yếu đặt metadata, nên đếm dòng Dockerfile không cho mình dung lượng image.

Ở hình này mình chỉ thêm base, dependencies rồi source. Chưa xóa gì cả.

**Hình / thao tác:** hiện từng lớp từ dưới lên; đặt ENV/CMD/USER cạnh chồng lớp, không vẽ thành ba lớp dữ liệu. Bấm giữ chồng lớp để mở góc nhìn container.

**Chuyển:** “Container lại cho mình thấy các lớp đó như một filesystem chung.”

**Bằng chứng:** [D1], [D6]; inspect/history được thu theo [E7].

## Slide 6 — Nhìn hợp nhất

**Lời nói**

Khi vào container, mình thường nhìn filesystem hợp nhất. File hiện ra ở một đường dẫn, còn lớp đã thêm nó thì không hiện ngay trước mắt. Lớp trên cũng không viết lại trực tiếp byte của lớp dưới.

Để lần ngược, mình đọc history cùng inspect, hoặc dùng Dive trên đúng image để xem thay đổi từng lớp. Bộ dữ liệu này có history và inspect, chưa có báo cáo Dive thực đo.

**Hình / thao tác:** thêm khung “filesystem nhìn thấy” cạnh chồng lớp; nối các file sang góc nhìn hợp nhất. Giữ cả hai khung cho ví dụ thêm/xóa.

**Chuyển:** “Vì hai góc nhìn khác nhau, xóa file chưa chắc làm image nhẹ đi.”

**Bằng chứng:** [E7] bước lưu `history.jsonl`, `image-inspect.json`; [D6].

## Slide 7 — Thêm rồi xóa

**Lời nói**

Giả sử RUN đầu tải một archive, giải nén rồi kết thúc. RUN sau mới xóa archive. Ở filesystem cuối, mình không còn thấy archive nữa. Nếu chỉ kiểm tra bằng cách liệt kê file trong container, mình có thể tưởng phần dữ liệu đó đã biến mất hoàn toàn.

Đây là ví dụ cơ chế; mình không gắn cho archive một con số MiB chưa đo.

**Hình / thao tác:** thêm archive ở lớp A, rồi dấu xóa ở lớp B; cho archive biến mất ở khung hợp nhất. Chưa xóa hình archive dưới lớp A.

**Chuyển:** “Mình tạm ẩn khung hợp nhất để nhìn lại lớp đã tạo trước đó.”

**Bằng chứng:** [D1], [D6]; ví dụ tương ứng trong recipe ở [E6] dòng 87–92.

## Slide 8 — Byte vẫn còn

**Lời nói**

Archive vẫn nằm trong lớp A. Lớp B làm đường dẫn đó không còn xuất hiện ở góc nhìn cuối, chứ không thu hồi byte đã ghi ở lớp trước.

Recipe mục TOP thứ ba gặp đúng dạng này: COPY `/wheels` vào runtime, sau đó mới pip install và xóa `/wheels` ở RUN kế tiếp. Đó là một chỗ có thể cải tiến. Mình chưa đo tách phần wheels nên chưa biết nó đóng góp bao nhiêu vào tổng dung lượng.

**Hình / thao tác:** tô lại archive ở lớp A, giữ dấu xóa phía trên; thay ví dụ bằng cặp COPY `/wheels` → RUN install + rm. Không gắn wasted-space giả.

**Chuyển:** “Với file tạm do chính bước build tạo ra, mình nên dọn ngay trong bước đó.”

**Bằng chứng:** [E6] dòng 87–92; [D6].

## Slide 9 — Dọn cùng bước

**Lời nói**

Tải, dùng rồi xóa file tạm trong cùng RUN thì file đó không còn trong phần filesystem được lưu sau bước ấy. Cách khác là làm ở builder, chỉ chuyển artifact cần chạy sang stage cuối.

Nhưng đừng từ đó gộp mọi RUN thành một lệnh dài. Mình muốn nhóm việc theo vòng đời dữ liệu, đồng thời tránh buộc phần ít đổi chạy lại mỗi khi source đổi.

**Hình / thao tác:** cạnh nhánh hai RUN, hiện download && extract && rm trong một RUN; chỉ áp dụng cho file được tạo ở bước này, không vẽ như sửa được lớp COPY cũ.

**Chuyển:** “Thứ tự source và dependencies là ví dụ dễ thấy nhất của chuyện chạy lại.”

**Bằng chứng:** [D1], [D2], [D3]; chưa có phép đo riêng lợi ích của thao tác dọn.

## Slide 10 — Source đổi trước

**Lời nói**

Default COPY toàn bộ context trước khi cài uv và chạy `uv sync`. Khi source đổi, đầu vào của COPY đổi trước cả phần cài dependencies. Dù danh sách thư viện vẫn như cũ, chuỗi build phía sau đã phụ thuộc vào kết quả COPY mới.

Trong công việc thường ngày, code hay đổi hơn manifest và lockfile. Cách xếp này đặt phần hay đổi quá sớm.

**Hình / thao tác:** hiện COPY . . → install → sync; chỉ đổi màu một file source và ô COPY trước, chưa tô toàn chuỗi.

**Chuyển:** “Từ ô COPY đó, mình lần theo phần cache bị ảnh hưởng.”

**Bằng chứng:** [E3] dòng 4–10; [D2].

## Slide 11 — Cache mất theo

**Lời nói**

Sau khi COPY không còn dùng kết quả cũ, các bước phụ thuộc phía sau phải được xét lại; với chuỗi này, phần cài đặt không dùng lại cache cũ như trước. Một comment trong source cũng đủ làm thay đổi đầu vào COPY, dù nó không thay đổi chức năng ứng dụng.

Chuyện này giải thích vì sao build nguyên đầu vào lần hai nhanh chưa nói được nhiều về tốc độ lúc chỉnh code.

**Hình / thao tác:** lan màu invalidated từ COPY xuống install và sync. Dừng tại chuỗi phụ thuộc; không tô các nhánh build không liên quan như thể mọi cache đều mất.

**Chuyển:** “Mình có thể đổi thứ tự mà không cần đổi mục tiêu của từng bước.”

**Bằng chứng:** [D2]; [E7] dòng 41–49 cho thay đổi comment trong bài đo.

## Slide 12 — Đổi thứ tự

**Lời nói**

Mình đưa manifest và lockfile vào trước, cài dependencies rồi mới COPY source. Hai phần có nhịp thay đổi khác nhau giờ nằm ở hai chỗ khác nhau trong chuỗi.

TOP 1 chỉ bind `uv.lock` và `pyproject.toml` cho bước sync, còn source COPY về cuối runtime. TOP 2 điều chỉnh cũng khai báo dependencies trước rồi mới COPY source. Không nhất thiết recipe nào cũng phải dùng cùng một cú pháp COPY manifest.

**Hình / thao tác:** di chuyển source xuống cuối; giữ manifest/lock → install thành cụm riêng. Hiện bind mount ở TOP 1 như đầu vào build, không phải file tự được lưu vào layer.

**Chuyển:** “Thử đổi lại đúng file source ban nãy.”

**Bằng chứng:** [E4] dòng 38–42, 68; [E5] dòng 26–36, 89; [D2].

## Slide 13 — Cache được giữ

**Lời nói**

Lần này source đổi sau bước cài dependencies. Nếu đầu vào của bước cài không đổi và cache còn sẵn, BuildKit dùng lại kết quả đó; phần source và các bước phụ thuộc nó mới cần làm tiếp.

Nhánh wheels cần nhìn kỹ hơn: recipe mục TOP thứ ba còn build wheel của chính project sau COPY source. Source đổi có thể đổi artifact rồi kéo theo cài lại ở runtime. Có manifest ở đầu chưa đủ, mình phải theo hết đường phụ thuộc.

**Hình / thao tác:** giữ xanh cụm dependencies, đổi màu source; thêm nhánh source → project wheel → runtime install ở mục TOP thứ ba.

**Chuyển:** “Cache vừa dùng là dùng lại kết quả cả bước, khác với giữ file package đã tải.”

**Bằng chứng:** [E6] dòng 49–55, 87–92; [D2].

## Slide 14 — Bỏ qua RUN

**Lời nói**

Layer cache cho phép dùng lại kết quả bước build khi đầu vào phù hợp. RUN đó không cần thực thi lại. Nhìn log thấy CACHED thì mình biết có kết quả được tái sử dụng, nhưng số dòng CACHED không phải số lớp filesystem hay phần trăm công việc tiết kiệm được.

Còn nếu RUN buộc phải chạy, bên trong nó vẫn có thể tận dụng một kiểu cache khác.

**Hình / thao tác:** đánh dấu RUN được bỏ qua, mũi tên đi thẳng đến kết quả cũ. Giữ hình này ở trái để so với RUN thực thi ở slide sau.

**Chuyển:** “Ở phía bên kia, lệnh vẫn chạy nhưng có sẵn một phần dữ liệu tải về.”

**Bằng chứng:** [D2]; [E7] trường `cached_log_lines`.

## Slide 15 — Tải lại ít

**Lời nói**

Cache mount giữ dữ liệu trong một vùng riêng để những lần RUN sau có thể dùng lại. RUN vẫn thực thi; công cụ cài package có thể bớt tải lại file nếu nó dùng cache đó. Vùng mount không tự trở thành nội dung image cuối.

TOP 1 mount `/root/.cache/uv`. Trong bài đo, cold có thể làm ấm cache mount cho warm hoặc source-change của cùng job. Bốn recipe không chia sẻ cache với nhau, cũng không restore cache từ GitHub Actions.

**Hình / thao tác:** thêm kho cache ngoài layer, nối vào RUN đang chạy; không nối kho đó trực tiếp sang runtime image. So cạnh RUN bị bỏ qua của slide trước.

**Chuyển:** “Có mount đúng thư mục vẫn chưa chắc công cụ đã dùng nó.”

**Bằng chứng:** [E4] dòng 38–42; [E2], [E7]; [D2].

## Slide 16 — Mount bị vô hiệu

**Lời nói**

TOP 2 mount thư mục pip nhưng lại đặt `PIP_NO_CACHE_DIR=1` và truyền `--no-cache-dir`. Cấu hình này tắt cache pip theo cách thông thường, nên mình không thể thấy dòng mount rồi kết luận nó đã giúp tải ít hơn.

Với apk, recipe cũng mount cache và dùng `apk --no-cache`; muốn biết lợi ích phải xem hành vi thực tế. Mình chưa đo riêng số giây các mount này tiết kiệm.

**Hình / thao tác:** giữ mũi tên mount nhưng gạch đường pip sử dụng cache do hai tùy chọn trên; không gạch layer cache của toàn build.

**Chuyển:** “Cache giúp build lại. Để không mang công cụ build vào lúc chạy, mình cần một ranh giới khác.”

**Bằng chứng:** [E5] dòng 13–27, 76–77; [D2].

## Slide 17 — Builder cần gì

**Lời nói**

Builder có thể cần compiler, headers, uv hay pip và dữ liệu tải package. Những thứ đó phục vụ việc tạo ra môi trường ứng dụng, nhưng không nhất thiết phải đi cùng container lúc chạy.

Multi-stage cho mình bắt đầu stage cuối từ một base riêng. Dữ liệu chỉ nằm trong builder không tự xuất hiện trong runtime image; mình chủ động chọn thứ sẽ COPY sang.

**Hình / thao tác:** hiện builder với toolchain/cache/artifact; đặt khung runtime rỗng cạnh bên. Chưa vẽ mũi tên chuyển toàn bộ builder.

**Chuyển:** “Phần cần chuyển phụ thuộc ứng dụng được đóng gói thành gì.”

**Bằng chứng:** [D3]; các stage trong [E4]–[E6].

## Slide 18 — Chuyển artifact

**Lời nói**

TOP 1 chuyển Python, standard library, shared libraries bổ sung và venv sang distroless. TOP 2 chuyển `/install` sang Python Alpine rồi thêm source. Mục TOP thứ ba chuyển wheels để cài offline.

Cả ba đều multi-stage nhưng không chuyển cùng một bộ dữ liệu. Vẽ mũi tên COPY --from thì dễ; quyết định mũi tên đó mang gì mới quyết định nội dung runtime.

**Hình / thao tác:** mở lần lượt ba mũi tên có nhãn Python/libs/venv, `/install`, wheels. Compiler và cache giữ lại phía builder.

**Chuyển:** “Mình cần giữ đủ để chạy, chứ không phải cố chuyển ít file nhất bằng mọi giá.”

**Bằng chứng:** [E4] dòng 59–68; [E5] dòng 85–89; [E6] dòng 87–92; [D3].

## Slide 19 — Runtime giữ gì

**Lời nói**

Runtime phải có interpreter, dependencies, source hoặc artifact ứng dụng, cùng dữ liệu và shared libraries thực sự cần. Thiếu một thư viện có thể lỗi ngay lúc import; thiếu package data hay metadata có khi chỉ lộ ở một nhánh chức năng.

Cấu hình user cũng nằm ở đây. Inspect ghi TOP 1 là 65532, TOP 2 là app, mục TOP thứ ba là 10001:10001; default không khai báo USER. Mình đọc đó như cấu hình thực tế, không như chứng nhận bảo mật đầy đủ.

**Hình / thao tác:** khép khung runtime quanh phần được giữ, thêm USER bên ngoài filesystem; không cho dấu PASS chỉ từ việc COPY đủ ô trên hình.

**Chuyển:** “Danh sách cần giữ còn phụ thuộc base mình chọn.”

**Bằng chứng:** [E1] trường `configured_user`; [E4]–[E6]; [D3].

## Slide 20 — Chọn base image

**Lời nói**

Alpine dùng musl, Debian slim dùng glibc. Distroless giảm các tiện ích trong runtime; TOP 1 build trên Bookworm slim rồi chuyển sang distroless Debian 12. Default và TOP 2 điều chỉnh dùng Alpine, còn mục TOP thứ ba dùng Python slim.

Mình không chọn chỉ bằng dung lượng base. Với Python có native extension, khả năng dùng wheel sẵn và thư viện cần lúc chạy có thể thay đổi cả cách build. Wolfi được tài liệu gốc nhắc tới nhưng không nằm trong bốn phép đo này.

**Hình / thao tác:** chia ba nhánh Alpine/musl, slim/glibc, distroless; nối đúng builder slim → distroless. Nếu có Wolfi, đặt ngoài vùng đã đo.

**Chuyển:** “Trước khi đổi base, mình cần kiểm tra phần native có đi cùng được không.”

**Bằng chứng:** FROM trong [E3]–[E6]; [O1], [D7].

## Slide 21 — Kiểm tra tương thích

**Lời nói**

Mình kiểm tra wheel đúng nền và kiến trúc, các shared libraries mà Python hoặc extension cần, rồi thử import và request. Nếu phải compile thay vì dùng wheel sẵn, base nhỏ có thể làm build lạnh tốn thêm việc.

Distroless cũng cần luồng debug phù hợp, đừng đợi sự cố mới tìm shell. Bộ số hôm nay chỉ đo linux/amd64. TOP 1 có nhánh arm64 trong Dockerfile, nhưng nhánh được viết ra chưa phải bằng chứng arm64 đã chạy đạt.

**Hình / thao tác:** theo mũi tên wheel/ABI → shared libs → import/request; đánh dấu amd64 trong vùng đã đo, arm64 ngoài vùng xác nhận.

**Chuyển:** “Tương thích hôm nay rồi, lần sau mình có chắc vẫn lấy đúng đầu vào đó không?”

**Bằng chứng:** [E4] dòng 14–25; [E1] trường `platform`; [D7].

## Slide 22 — Tag có đổi

**Lời nói**

Một tag có thể trỏ tới nội dung mới theo thời gian. Mình giữ nguyên dòng FROM nhưng build ở thời điểm khác vẫn có thể lấy base khác. Default và mục TOP thứ ba dùng base tag như vậy.

Tag tiện cho việc theo một dòng phiên bản. Khi cần truy lại lần build cụ thể, mình phải ghi rõ nội dung đã dùng thay vì chỉ lưu tên tag.

**Hình / thao tác:** giữ một tag ở hai thời điểm, lần lượt nối đến nội dung A và B. Chưa gọi B là bản đã kiểm thử.

**Chuyển:** “Digest giúp chỉ định nội dung base mình muốn giữ.”

**Bằng chứng:** [E3], [E6] các FROM; [D1].

## Slide 23 — Digest giữ nội dung

**Lời nói**

Pin base bằng digest chỉ định nội dung image được tham chiếu. TOP 1 pin builder và runtime; TOP 2 cũng pin base theo digest. Nhờ vậy, mình truy vết phần base rõ hơn so với chỉ dùng tag thay đổi được.

Nhưng đây mới là một phần đầu vào. Cài package gì, dùng công cụ nào và source ở commit nào vẫn cần được ghi lại.

**Hình / thao tác:** thay mũi tên tag bằng tham chiếu digest cố định; mở ba ô còn lại dependencies/source/tooling, chưa gắn khóa cho chúng.

**Chuyển:** “Có digest và có lockfile vẫn cần đọc các lệnh cài sau đó.”

**Bằng chứng:** [E4] dòng 1, 49; [E5] dòng 11, 57; [D1].

## Slide 24 — Pin chưa hết

**Lời nói**

TOP 1 sync theo lockfile với `--frozen`, rồi cài riêng Starlette 0.49.1 bằng `--no-deps`. Vì vậy môi trường cuối không đơn giản là nguyên lockfile. TOP 2 điều chỉnh pin FastAPI 0.120.4, nhưng nhiều dependency khác vẫn là khoảng phiên bản.

Mình lưu commit, hash Dockerfile, base reference và package thực tế sau build. Pin cũng cần lịch cập nhật và test lại; giữ bản cũ mãi có thể giữ luôn lỗi cần vá.

**Hình / thao tác:** mở lệnh cài Starlette sau frozen và các range của TOP 2; nối đầu vào tới `packages.json`. Không biến digest thành huy hiệu “an toàn”.

**Chuyển:** “Còn các thao tác dọn mạnh thì phải đọc cụ thể chúng bỏ thứ gì.”

**Bằng chứng:** [E4] dòng 41–42; [E5] dòng 28–36; [E8], [D1].

## Slide 25 — Strip bỏ gì

**Lời nói**

Strip xử lý thông tin trong binary, không phải nén mọi file. Với ELF, `--strip-debug` khác `--strip-all`: phần debug hoặc bảng symbol có thể bị loại tùy chế độ, trong khi thông tin cần cho thực thi và liên kết động vẫn phải đúng.

TOP 2 chạy `strip --strip-all` trên `.so*` và `.a` trong `/install`, có `|| true` để bỏ qua lỗi. Lệnh đi qua không có nghĩa mọi file đều strip thành công hay mọi đường chạy đều còn đúng.

**Hình / thao tác:** hiện `.text`, `.dynsym`, `.symtab`, `.debug_*`; chỉ phần có thể bị bỏ theo chế độ, không gạch toàn bộ symbols. Tách strip khỏi xóa file thông thường.

**Chuyển:** “Recipe này còn dọn nhiều nhóm file khác ngoài binary.”

**Bằng chứng:** [E5] dòng 39–52; [D8].

## Slide 26 — Dọn có giá

**Lời nói**

TOP 2 còn giảm `.dist-info`, xóa license, tài liệu và một số phần standard library. Mất thông tin debug làm chẩn đoán khó hơn; mất metadata hoặc package data có thể ảnh hưởng lúc chạy; license lại có nghĩa vụ phân phối riêng. Tên file nghe có vẻ thừa chưa đủ để xóa.

Bản điều chỉnh qua smoke, nhưng mình chưa tách từng nhóm dọn để đo lợi ích. Con số 65.42 MiB là của cả recipe, không phải số byte riêng strip tiết kiệm được.

**Hình / thao tác:** mở ba nhóm rủi ro strip/metadata-license/stdlib; không hiển thị dung lượng tiết kiệm riêng. Bấm chuyển từ sơ đồ cơ chế sang khung phép đo.

**Chuyển:** “Đến đây mình chốt lại điều kiện trước khi mở kết quả.”

**Bằng chứng:** [E5] dòng 39–52, 94–116; [E1], [E2]; không có ablation hay xác nhận license.

## Slide 27 — Chốt điều kiện

**Lời nói**

Bốn recipe dùng source commit `35be0461710f3f907d1c6e1fd54de68d1f915ea8`, build linux/amd64 trên GitHub Actions ubuntu-24.04. Đây là rebuild ở run `41992840188`, không phải bảng chấm cuộc thi năm 2025.

Runtime được chuẩn hóa 1 CPU, 512 MiB, PORT=5000 và WORKERS=1. Base và dependencies vẫn khác nhau, nên kết quả cho biết từng recipe hoạt động thế nào trong bài thử này. Phụ lục ghi đủ những giới hạn cần đọc cùng bảng số.

**Hình / thao tác:** mở commit/platform/run, rồi khung cấu hình runtime riêng. Không gắn giới hạn 1 CPU/512 MiB lên runner build.

**Chuyển:** “Mỗi recipe được build theo cùng một chuỗi ba lượt.”

**Bằng chứng:** [E1], [E2], [E7], [E9].

## Slide 28 — Ba lượt build

**Lời nói**

Cold dùng builder mới với `--pull --no-cache`. Warm lặp nguyên đầu vào trên builder đó. Source-change chỉ nối một comment vào `app.py`, không sửa chức năng hay thêm dependency.

Đồng hồ bao quanh buildx có `--load`, nên gồm export/load image nhưng không gồm dựng builder. Mỗi chế độ chỉ có một mẫu cho mỗi recipe. Cold cũng không có nghĩa mình đã làm trống mọi cache của registry hay hạ tầng mạng bên ngoài.

**Hình / thao tác:** hiện cold → warm → comment-only; khoanh `--load` trong vùng đồng hồ, setup builder ở ngoài. Runtime theo sau image cuối chuỗi.

**Chuyển:** “Chuỗi này lặp lại trên bốn runner riêng.”

**Bằng chứng:** [E7] dòng 36–49; [E2], [E9].

## Slide 29 — Bốn runner riêng

**Lời nói**

Matrix mở tối đa bốn job song song và tắt fail-fast. Mỗi recipe có builder riêng, chạy cold, warm, source-change rồi kiểm tra runtime. Cùng loại runner không có nghĩa cùng máy hay cùng đường mạng; thời gian vẫn có nhiễu hạ tầng.

Chạy song song ở đây là bốn phép đo độc lập. Mình không dùng nó để nói một image build nhanh gấp bốn lần, cũng không cộng bốn thời gian thành thời gian chờ workflow.

**Hình / thao tác:** nhân chuỗi ba lượt thành bốn làn runner, không có mũi tên cache nối ngang; cho các làn hội tụ về artifact.

**Chuyển:** “Mỗi làn phải để lại dữ liệu, kể cả khi một recipe có lỗi.”

**Bằng chứng:** [E9] dòng 14–20, 26–45; [E2].

## Slide 30 — Gom bằng chứng

**Lời nói**

Workflow yêu cầu upload artifact với `if: always()`, rồi job compare đọc result JSON để tổng hợp. Nhờ vậy, lỗi một nhánh không cần làm mất bằng chứng ở nhánh khác.

Mình kiểm tra `runtime` trong JSON và log thay vì dựa vào mỗi dấu tích xanh của CI. Script có thể ghi runtime failed rồi vẫn kết thúc phần thu thập. Đường đi là run, commit, recipe hash, result và log tương ứng.

**Hình / thao tác:** gom bốn artifact vào compare; mở `result.json` với runtime status cạnh badge CI, không đồng nhất hai trạng thái.

**Chuyển:** “Có đường kiểm tra rồi, mình đọc số đầu tiên: dung lượng local của image.”

**Bằng chứng:** [E7] dòng 69–99, 102–119; [E8], [E9].

## Slide 31 — Kích thước image

**Lời nói**

Default là 200.51 MiB. TOP 1 là 101.82 MiB, giảm 49.22%. TOP 2 điều chỉnh là 65.42 MiB, giảm 67.37%. Mục TOP thứ ba là 207.48 MiB, lớn hơn default 3.48%. Phần trăm tính từ byte thô, không từ MiB đã làm tròn.

Đây là local uncompressed size từ Docker inspect, không phải dung lượng tải registry. Số lớp cũng không quyết định tổng byte: TOP 1 có 21 lớp mà vẫn nhỏ hơn default 9 lớp; TOP 2 có 12, mục TOP thứ ba có 9.

**Hình / thao tác:** hiện bốn thanh chung trục từ 0 theo đúng thứ tự trên; giữ nhãn TOP 2 điều chỉnh. Không đổi MiB thành MB hay suy ra thời gian pull.

**Chuyển:** “Thứ tự này thay đổi khi mình nhìn sang build lạnh.”

**Bằng chứng:** [E1] `image_bytes`, `layer_count`; [E2], [C1].

## Slide 32 — Nhỏ chưa nhanh

**Lời nói**

Cold của default là 14.640 giây; TOP 1 là 11.850; TOP 2 điều chỉnh là 22.579; mục TOP thứ ba là 34.172. So với default, TOP 1 bớt 19.06% thời gian, TOP 2 thêm 54.23%, nhánh cuối thêm 133.42% trong mẫu này.

TOP 2 nhỏ nhất nhưng không build lạnh nhanh nhất. Pull base, cài hoặc build package, dọn và export/load đều có thể góp thời gian. Muốn gán phần chậm cho một lệnh cụ thể, mình phải đọc log và đo tách, không nhìn tổng rồi đổ cho Alpine hay strip.

**Hình / thao tác:** giữ nhãn size nhỏ nhất của TOP 2, chuyển sang bốn thanh cold cùng đơn vị giây. Không trình bày một mẫu như xu hướng thống kê.

**Chuyển:** “Lần build kế tiếp không đổi đầu vào thì cả bốn giảm xuống rất nhiều.”

**Bằng chứng:** [E1] `builds.cold.seconds`; [E7] dòng 36–49; [C1].

## Slide 33 — Build có cache

**Lời nói**

Warm lần lượt là 0.712 giây với default, 0.307 với TOP 1, 0.553 với TOP 2 điều chỉnh và 0.894 với mục TOP thứ ba. Đây là lượt lặp nguyên đầu vào trên builder vừa dùng.

Các kết quả cũ có thể được tái sử dụng, nhưng đồng hồ vẫn có phần xử lý và export/load. Warm nhanh là hữu ích; nó chưa cho mình biết trải nghiệm khi sửa source. Mình cần đổi một đầu vào rồi nhìn lại chuỗi phụ thuộc.

**Hình / thao tác:** thay hàng cold bằng warm, tô các bước được cache; để hàng comment-only trống chờ slide sau. Không lấy cached log lines làm phần trăm tăng tốc.

**Chuyển:** “Bài thử tiếp theo chỉ thêm một comment Python.”

**Bằng chứng:** [E1] `builds.warm`; [E2], [E7].

## Slide 34 — Khi sửa source

**Lời nói**

Sau comment, default mất 9.853 giây; TOP 1 là 0.491; TOP 2 điều chỉnh là 0.928; mục TOP thứ ba là 21.354. So đúng chế độ này với default, TOP 1 bớt 95.02% thời gian và TOP 2 bớt 90.58%; mục TOP thứ ba lại thêm 116.73%.

Kết quả phù hợp với cách đặt source trước dependencies ở default và đường project wheel ở nhánh cuối. Mình mở log để biết từng bước tốn gì. Đây là comment-only, không đại diện cho mọi thay đổi tính năng hoặc lockfile.

**Hình / thao tác:** điền hàng source-change dưới warm; nối màu bước chạy lại với sơ đồ slide 11–13. Giữ cả bốn giá trị và nhãn comment-only.

**Chuyển:** “Image build xong rồi, mình mới chuyển sang kiểm tra ứng dụng bên trong.”

**Bằng chứng:** [E1] `builds.source-change`; [E3]–[E7], [C1].

## Slide 35 — Container đã lên

**Lời nói**

Docker run thành công hay container báo Running mới cho biết tiến trình đã lên ở thời điểm kiểm tra. Nó chưa xác nhận request health và homepage xử lý được.

Bài đo bắt đầu đồng hồ trước docker run, rồi chờ cả hai probe đạt. Mình dùng image cuối sau lượt thêm comment, dưới giới hạn runtime đã chốt. Phần thời gian chờ này cũng chịu nhịp polling, không phải latency một request.

**Hình / thao tác:** hiện container Running nhưng để ô request chưa xác nhận; bắt đầu đồng hồ và thêm hai đường probe. Chưa gắn PASS từ log startup.

**Chuyển:** “Phải đi hết hai đường request này mới biết smoke có đạt không.”

**Bằng chứng:** [E7] dòng 63–85; cấu hình chuẩn hóa [E2].

## Slide 36 — Request mới biết

**Lời nói**

Cả bốn PASS: `/health/` trả JSON có heartbeat bằng HEALTHY, homepage có chuỗi “Dockerfile Contest 2025”. Startup đến khi cả hai đạt lần lượt là 2.370, 1.804, 2.849 và 1.897 giây theo thứ tự default, TOP 1, TOP 2 điều chỉnh, mục TOP thứ ba.

Coffee API trỏ tới stub local, `/hot` trả 200 và `[]`; đây không phải kiểm thử tích hợp live. Script chờ 0.5 giây giữa probe chưa đạt, nên mình không đọc chênh lệch nhỏ như bằng chứng throughput hay tốc độ framework.

**Hình / thao tác:** bật PASS sau health JSON và homepage; nhánh coffee nối “stub local /hot → 200 []”, không nối cloud API thật. Đặt startup bên đồng hồ chờ probe.

**Chuyển:** “Một run trước đã có container startup xong nhưng request vẫn lỗi.”

**Bằng chứng:** [E1] `runtime`, `startup_seconds`; [E7] dòng 15–19, 63–85.

## Slide 37 — FastAPI lệch phiên bản

**Lời nói**

Ở run `41990729849`, TOP 2 nguyên bản resolve FastAPI 0.162.0 cùng prometheus-fastapi-instrumentator 7.1.0. Server ghi application startup complete, nhưng health request trả 500.

Traceback đi qua instrumentator, đọc `route.path` rồi gặp `'_IncludedRouter' object has no attribute 'path'`. Đó là một lỗi trên đường xử lý request của tổ hợp dependency cụ thể, không phải bằng chứng rằng mọi FastAPI mới đều lỗi.

**Hình / thao tác:** mở nhánh bản gốc, giữ startup xanh rồi hiện request 500 và đoạn lỗi đúng; không sửa log cũ thành PASS.

**Chuyển:** “Bản đo hiện tại thay đúng đầu vào FastAPI để tiếp tục khảo sát recipe.”

**Bằng chứng:** [F1] `packages.json`, `container.log`; đối chiếu run cũ với [E2].

## Slide 38 — Pin rồi thử

**Lời nói**

Lần hiện tại pin `fastapi==0.120.4`. Package sau build ghi Starlette 0.49.3 và instrumentator 7.1.0; health JSON cùng homepage đã PASS. Vì có thay đổi đó, mọi số TOP 2 trong bài đều mang nhãn điều chỉnh.

Pin bản biết chạy giúp khoanh vấn đề, chưa thay được lockfile đầy đủ và test khi nâng cấp. Mình cũng không dùng smoke PASS để nói bản pin không có CVE; workflow này không chạy scan mới.

**Hình / thao tác:** mở nhánh điều chỉnh cạnh bản gốc, hiện phiên bản và hai probe PASS; giữ cả hai run ID, nối bảng số chỉ về run mới.

**Chuyển:** “Những chi tiết nhỏ trong dữ liệu cũng phải được đọc đúng như vậy.”

**Bằng chứng:** [E5] dòng 30; [F2], [E1], [E2].

## Slide 39 — Đọc đúng số

**Lời nói**

Mình đi từ comparison JSON về result, build log, inspect, history, packages và container log. Dive có thể giúp soi layer nhưng lần này chưa chạy, nên hình minh họa không phải báo cáo wasted space.

Có hai field dễ hiểu sai: `last_probe_error` có thể còn lỗi của probe đầu dù cuối cùng runtime passed; `base_images` rỗng ở đây lấy từ RepoDigests của image local, không chứng minh FROM không pin. Label `trivy-passed` cũng chỉ là chuỗi trong Dockerfile, không phải kết quả scanner của lần này.

**Hình / thao tác:** mở chuỗi run → commit → hash → artifact; đặt ba chú thích đúng cạnh field/label, tách vùng đã đo khỏi CVE/Dive/full equivalence chưa đo.

**Chuyển:** “Từ bộ bằng chứng này, mình chọn theo nhu cầu nào thì nói rõ nhu cầu đó.”

**Bằng chứng:** [E7] dòng 55–62, 78–89; [E1], [E5] dòng 64; [D6].

## Slide 40 — Đo rồi chọn

**Lời nói**

Trong mẫu này, TOP 1 giảm khoảng nửa dung lượng và có cả bốn thời gian thấp nhất. TOP 2 điều chỉnh nhỏ nhất, nhưng cold và startup không thấp nhất. Mục TOP thứ ba có multi-stage mà vẫn lớn hơn default, đồng thời chậm hơn khi đổi comment.

Mình sẽ bắt đầu bằng việc đặt cache theo nhịp thay đổi, tách đồ nghề build khỏi runtime, chọn base tương thích và lưu đầu vào. Sau đó thử request rồi đo lại. Nếu dùng để quyết định triển khai, còn cần lặp phép đo, kiểm tra chức năng rộng hơn, dependency, license và scan mới. Phụ lục có nguồn để mở lại khi hỏi đáp.

**Hình / thao tác:** khép vòng Inspect → Change → Test → Measure, đặt evidence bên cạnh; không trao huy hiệu thắng mọi tiêu chí hoặc enterprise-ready.

**Chuyển:** “Mình dừng ở đây. Nếu cần xem một chênh lệch cụ thể, mình mở lại đúng log của nó.”

**Bằng chứng:** [E1], [E2], [C1]; các bước kiểm tra thêm là phần chưa làm.

# Phụ lục — giới hạn phép đo

Phần này dùng lúc chuẩn bị và hỏi đáp, không đọc lặp lại trên từng slide.

- Đây là rebuild run `41992840188`, commit `35be0461710f3f907d1c6e1fd54de68d1f915ea8`, không phải kết quả chấm năm 2025. Bốn whole recipe khác base và dependency; cùng source chưa chứng minh cùng môi trường hoặc tương đương chức năng đầy đủ.
- Mỗi chế độ/recipe chỉ một mẫu; bốn runner ubuntu-24.04 độc lập, linux/amd64. Chưa có median, độ lệch chuẩn hay kết luận thống kê. Không suy từ amd64 sang arm64.
- Cold: builder mới, `--pull --no-cache`; warm: nguyên đầu vào, cùng builder; source-change: chỉ thêm comment. Có export/load, không tính dựng builder. Không bảo đảm mọi cache registry/mạng đều trống. Cache mount chỉ có thể dùng lại trong job; không chia sẻ giữa recipe hay restore từ GHA.
- Size: Docker inspect local uncompressed bytes đổi sang MiB, không phải registry compressed size hoặc dung lượng tăng thêm trên máy đã dùng chung layer. Chưa có phép đo tách riêng tác động của wheels, strip hay từng nhóm cleanup.
- Runtime: image sau source-change, 1 CPU/512 MiB, PORT=5000, WORKERS=1; health JSON heartbeat HEALTHY và homepage chứa chuỗi đã nêu. Coffee stub local `/hot` trả 200 và `[]`. Không phải tích hợp API live, dữ liệu đại diện, load test, latency/throughput, toàn bộ endpoints hay xác nhận Docker HEALTHCHECK. Startup gồm docker run và polling 0.5 giây.
- TOP 2 đo là bản điều chỉnh FastAPI 0.120.4, không gán PASS hoặc size cho nguyên bản từng lỗi. `top-entry3` chỉ là ID mục TOP hiển thị thứ ba, chưa xác nhận hạng 3.
- Chưa scan CVE mới, chạy Dive thực đo, kiểm chứng tuân thủ license hoặc chứng minh mọi chức năng còn nguyên. Label/comment “secure”, “trivy-passed” hay số MB/0 CVE lịch sử không thay được bằng chứng mới. `stats.json` nếu có chỉ là snapshot, không phải benchmark tải.
- Muốn kết luận vững hơn: lặp phép đo có kiểm soát; lưu phân bố, đầu vào và image identity; đối chiếu dependencies; test rộng hơn với dữ liệu/API phù hợp; kiểm tra license; scan kèm thời điểm, phiên bản scanner và database. Muốn biết một kỹ thuật giúp bao nhiêu thì thay riêng kỹ thuật đó, giữ phần còn lại.

# Nguồn và bằng chứng đầy đủ

## Tài liệu gốc và phạm vi sử dụng

- **[O1]** `Thuyet_trinh_Dockerfile_Optimize.docx`, trong thư mục gốc repository. Đã đọc toàn bộ nội dung: câu chuyện CTF; layers, xóa file, gộp/tách RUN, thứ tự COPY, hai loại cache, Dive; CVE, multi-stage, base, digest, strip; kiểm tra lại V1 và đo trước khi kết luận. Bản 2 phân bố lại cùng nội dung theo 40 trạng thái sơ đồ đã thống nhất; không dùng các ô “tự bổ sung” hoặc bảng V1/V2 chưa đo.
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

**[C1] Công thức và kiểm tra số bằng Python:** `MiB = image_bytes / 1048576`; `giảm_size_% = (1 - bytes_recipe / bytes_default) * 100`; `tăng_thời_gian_% = (seconds_recipe / seconds_default - 1) * 100`; `giảm_thời_gian_% = (1 - seconds_recipe / seconds_default) * 100`. Tính từ JSON thô, chỉ làm tròn ở bước hiển thị. Kết quả tính lại của bản 2 nằm trong `python-speaker-notes-v2-validation.json`; metadata bản đầu ở `python-sources.json`.

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

