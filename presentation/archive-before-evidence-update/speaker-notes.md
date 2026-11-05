# Ghi chú thuyết trình — tối ưu Dockerfile có kiểm chứng

**Nhịp trình bày:** khoảng 23 phút, chưa tính hỏi đáp. Tổng thời lượng dự kiến của 16 slide là 23 phút; cần tập nói để điều chỉnh tốc độ và khoảng dừng chỉ sơ đồ. Chỉ đọc “Lời nói” và “Chuyển ý”; phần chỉ sơ đồ là động tác, không phải chữ thêm lên slide.

**Trục nội dung:** CTF → layers → cleanup → COPY/cache → multi-stage → nền/runtime → đầu vào → inspect → kiểm chứng → pipeline → đo và lặp. Công cụ phục vụ phương pháp; không biến bài tối ưu thành danh sách công cụ.

**Ranh giới bằng chứng:** `DockerFile-Contest/main` vẫn là lab Python độc lập. Case thực tế nằm ở repo packaging-only `newnol/9router-wolfi`: checkout upstream commit `1fe586bb1cf35e1ed0cb2150a8ef7d1db040b21d`, manifest phiên bản **0.5.112**, nền Wolfi đã pin, Node 22, multi-stage và runtime non-root. Main đã build, smoke và publish thành công ở run **41964645341**. Run **41966436702** là build thành công của nhánh **0.4.41**, không phải cùng source hoặc image. Renovate run **41964645996** thành công, tạo PR #1/#2; tại mốc kiểm tra hai PR còn mở và CI cần phê duyệt, chưa được coi là pass. Chưa có Grype/Strix, benchmark trước–sau hay chứng minh tương đương toàn bộ chức năng. Bằng chứng dưới đây là snapshot trong `sources.json`, không phải tuyên bố vừa build hoặc quét lại ở máy trình bày.[16]–[29]

## Slide 1 — Từ CTF

**Thời lượng dự kiến:** 1 phút 25 giây.

**Lời nói:**

“Điểm bắt đầu là câu chuyện CTF trong bài chia sẻ cũ. Khi nhận một container image, mình dễ nghĩ đây chỉ là cách đóng gói để chạy ứng dụng. Nhưng nhìn dưới góc độ artifact, câu hỏi thú vị hơn là: ngoài ứng dụng, image còn mang theo những gì? Cây thư mục trên hình là mô hình minh họa, không phải bằng chứng một challenge cụ thể hay repo hiện tại đã lộ khóa.

Một lần COPY quá rộng có thể mang theo lịch sử source, cấu hình local hoặc artifact build. Container chạy đúng không đồng nghĩa mọi file trong image đều cần thiết. Ngược lại, chỉ thấy shell hay công cụ mạng cũng chưa đủ kết luận image có thể bị xâm nhập; còn phụ thuộc lỗi, quyền và cấu hình thực tế. Vì vậy mình không dùng một dấu hiệu riêng lẻ để thay cho kiểm tra.

Em giữ lại câu hỏi gốc: image này cần chứa gì, và mình biết điều đó bằng cách nào? Bài hôm nay không đi vào khai thác. Mình đi từ hiểu artifact đến build ít dư thừa hơn, giữ chức năng đúng, rồi kiểm tra bằng chứng. Nhỏ hơn là một mục tiêu, nhưng không phải mục tiêu duy nhất. Phần sau sẽ dùng một bản đóng gói thật để phân biệt điều đã làm với điều vẫn cần đo.”

**Chỉ sơ đồ:** image → source, dependency và dữ liệu thừa. Nhấn đây là minh họa artifact, không tái hiện khai thác hoặc đọc secret.

**Chuyển ý:** “Case thực tế đã tồn tại ở một repo riêng; trước tiên em tách rõ nó với lab Python.”

## Slide 2 — Ứng dụng thật

**Thời lượng dự kiến:** 1 phút 30 giây.

**Lời nói:**

“Ở đây có hai repo độc lập. DockerFile-Contest vẫn là lab Python cho phương pháp tối ưu. Repo newnol/9router-wolfi chứa Dockerfile, cấu hình chạy và workflow đóng gói; nó không chứa toàn bộ source ứng dụng. Workflow checkout upstream ở commit được pin, rồi build ứng dụng từ đó. Manifest tại commit này ghi phiên bản 0.5.112.[16][20][23][27]

Vì vậy case 9router không còn chỉ là ý tưởng migration. Main đã có build, smoke test và publish thành công ở run 41964645341. Tuy nhiên, kết quả đó chỉ chứng minh các bước và assertion thực sự đã chạy. Nó chưa phải benchmark, chưa chứng minh toàn bộ chức năng hoặc mức độ sẵn sàng triển khai doanh nghiệp.[19][24] Bản build nhánh 0.4.41 là bằng chứng riêng, không lấy kết quả nhánh đó gắn vào main.[25]

Advisory lịch sử ghi phạm vi đến 0.4.41 là bối cảnh để nhắc rằng tối ưu đóng gói khác với sửa logic ứng dụng.[1][2] Không suy từ đó rằng 0.5.112 vẫn chịu mọi lỗi cũ, cũng không nói phiên bản mới đã sửa hết mọi lỗi. Chưa định danh đầy đủ thì không dùng lời nhắc ‘ba CVE’ làm finding hiện tại. Case thật giúp mình có đầu vào và kết quả cụ thể, đồng thời phải nói rõ giới hạn của chúng.”

**Chỉ sơ đồ:** chỉ hai nhánh Python lab và repo packaging; dừng ở nhãn v0.5.112, rồi chỉ các nhóm chức năng như phạm vi cần kiểm tra, không như tất cả đã pass.

**Chuyển ý:** “Dù Python hay Node, muốn tối ưu đúng vẫn phải hiểu filesystem của image.”

## Slide 3 — Filesystem layers

**Thời lượng dự kiến:** 1 phút 25 giây.

**Lời nói:**

“Image là các lớp thay đổi filesystem chồng lên nhau. Một lớp có thể thêm, sửa hoặc đánh dấu xóa file; khi đã tạo, lớp đó không bị viết lại chỉ vì lớp phía trên thay đổi.[15] Khi container chạy, mình thấy một cây thư mục hợp nhất, nên rất dễ quên bên dưới còn dữ liệu của từng lớp.

Nhìn từ dưới lên: nền cung cấp môi trường chạy, tiếp theo là dependency, cuối cùng là artifact ứng dụng. Đây là mô hình để suy luận, không phải bản chụp chính xác các layer của image hiện tại. RUN hoặc COPY có thể tạo thay đổi filesystem; không nên suy thành mọi dòng Dockerfile đều tạo một lớp chứa file. CMD và các chỉ thị cấu hình còn có vai trò metadata. Đếm dòng hoặc đếm layer không tự trả lời image có nhỏ hay build có nhanh không.

Câu hỏi hữu ích là: lớp nào chứa dữ liệu gì, dữ liệu đó có cần ở runtime không, và đầu vào nào làm bước tạo nó phải chạy lại? Mô hình này nối hai việc thường bị trộn: dung lượng artifact phân phối và công sức build. Với case Node, mình vẫn phân biệt runtime, dependency và output build thay vì xem image là một khối đen. Phần kế tiếp dùng chính tính bất biến này để giải thích chuyện xóa file.”

**Chỉ sơ đồ:** base → dependency → application → image hợp nhất. Nhấn lớp lưu trữ khác với cây thư mục container nhìn thấy.

**Chuyển ý:** “Xóa khỏi cây thư mục cuối chưa chắc xóa khỏi artifact được phân phối.”

## Slide 4 — Xóa chưa mất

**Thời lượng dự kiến:** 1 phút 25 giây.

**Lời nói:**

“Bên trái là cách làm dễ gặp: bước đầu tải archive, bước sau giải nén, bước tiếp theo xóa archive. Trong filesystem cuối mình không còn thấy file nén. Nhưng dữ liệu đã được ghi ở lớp trước; lớp sau chỉ ghi nhận việc xóa trong góc nhìn hợp nhất, không quay lại cắt bytes khỏi lớp cũ.[15] Vì thế nhìn thư mục cuối chưa đủ để giải thích dung lượng image.

Bên phải là hướng xử lý cho file tạm: tạo, dùng và dọn trong cùng bước tạo layer, để file tạm không còn trong thay đổi lưu ở cuối bước. Một hướng khác là giữ dữ liệu trung gian ở builder và không copy sang runner. Điều này không có nghĩa mọi RUN phải gộp thành một dòng khổng lồ. Gộp các công việc không liên quan có thể làm cache kém hữu ích và khó tìm lỗi.[13][14]

Em cũng không dùng xóa ở lớp sau như cách xử lý secret. Nếu dữ liệu nhạy cảm đã vào artifact hoặc cache chia sẻ thì phải xử lý theo phạm vi thực tế, không chỉ giấu khỏi cây thư mục cuối. Trong bài tối ưu, nguyên tắc là không đưa file không cần vào ngay từ đầu và kiểm tra artifact đầu ra. Đây là giải thích cơ chế; chưa có phép đo đối chứng để hứa giảm một lượng MB cụ thể trên case này.”

**Chỉ sơ đồ:** thêm archive ở lớp dưới → xóa ở lớp trên → bytes còn lại; đối chiếu nhánh tải–dùng–xóa cùng bước.

**Chuyển ý:** “Sau thứ gì được lưu, mình xét thứ tự nào giúp tránh phải làm lại.”

## Slide 5 — Thứ tự COPY

**Thời lượng dự kiến:** 1 phút 25 giây.

**Lời nói:**

“Nguyên tắc là đưa đầu vào dependency ít đổi lên trước, source hay đổi xuống sau. Khi chỉ sửa source, mình muốn giữ kết quả cài dependency nếu điều kiện cache còn hợp lệ. Docker dùng chính kiểu ví dụ này để giải thích vì sao COPY cả source trước bước install dễ làm cache bị vô hiệu hóa không cần thiết.[13]

Dockerfile packaging hiện đã COPY package.json trước source và chạy npm install --include=dev.[17] Mình ghi nhận thứ tự tốt đang có, không dựng chuyện upstream hoặc bản packaging chưa biết tối ưu cache. Nhưng ở bước cài này không có lockfile được copy vào; do đó không được gọi nó là cài dependency đã khóa. Pin commit source và digest nền không khóa được mọi phiên bản npm được phân giải tại thời điểm build.

Khi bổ sung kiểm chứng, cần tách ba tình huống: không đổi đầu vào, chỉ đổi source, rồi đổi dependency. Đọc log xem bước nào dùng lại, thay vì suy từ vị trí COPY rằng đã nhanh hơn bao nhiêu. Build context cũng cần gọn để lịch sử Git, dữ liệu thử và artifact local không bị mang theo. Hình đang minh họa nguyên tắc cùng một khoảng trống thực tế là lockfile; chưa phải biểu đồ cache hit hay kết quả so trước–sau.”

**Chỉ sơ đồ:** package.json → install → source; dừng ở “Lockfile còn thiếu”. “Cache giữ lại” là hành vi mong đợi khi đủ điều kiện, không phải số đo đã thu.

**Chuyển ý:** “Nếu bước install vẫn cần chạy lại, một kiểu cache khác có thể giảm tải lại.”

## Slide 6 — Hai lớp cache

**Thời lượng dự kiến:** 1 phút 25 giây.

**Lời nói:**

“Layer cache trả lời: có thể dùng lại kết quả bước build này không? Nếu hit, RUN tương ứng được bỏ qua. Cache mount trả lời câu khác: khi RUN vẫn phải chạy, nó có thể dùng lại dữ liệu tải về của package manager không?[13] Hai khái niệm này hỗ trợ nhau nhưng không thay thế nhau.

Dockerfile packaging đã có cache mount cho npm; workflow cũng có cấu hình layer cache qua GitHub Actions.[17][20] Đây là kỹ thuật đang dùng, không phải một mục em mới đề xuất thêm. Nhưng khai báo cache mount không chứng minh dữ liệu trong mount được khôi phục giữa mọi runner CI. Layer cache từ xa và trạng thái mount trên builder không mặc nhiên là cùng một kho. Muốn nói lợi ích thực tế vẫn cần kiểm tra log và điều kiện runner.

Phép đo sau này phải phân biệt build lạnh, build ấm không thay đổi, đổi source và đổi dependency. Cần ghi rõ builder, cache nào được giữ và cache nào bị xóa. Chỉ tắt layer cache chưa đủ gọi phép thử là lạnh nếu kho package manager vẫn còn dữ liệu. Ngược lại, một build chậm do mạng không chứng minh thứ tự COPY sai. Tới thời điểm này mình có cấu hình cache thật nhưng chưa có số đo đối chứng về mức tăng tốc.”

**Chỉ sơ đồ:** nhánh layer đi qua RUN được bỏ qua; nhánh mount vẫn qua RUN và nối tới downloads. Không vẽ mount như dependency tự đi vào runtime.

**Chuyển ý:** “Cache giảm công sức build; multi-stage giới hạn thứ được chuyển sang runtime.”

## Slide 7 — Tách giai đoạn

**Thời lượng dự kiến:** 1 phút 30 giây.

**Lời nói:**

“Builder cần công cụ đóng gói và biên dịch; runner chỉ cần những gì phục vụ chạy ứng dụng. Multi-stage cho phép chọn artifact từ stage trước thay vì mang cả xưởng build vào image cuối.[14] Nó tạo ranh giới rõ, nhưng không tự bảo đảm nhỏ hoặc an toàn: copy nguyên thư mục làm việc vẫn có thể đưa phần dư trở lại.

Bản packaging đã có base, builder và runner với Node 22. Builder cài npm, build-base và Python 3, đồng thời rebuild better-sqlite3. Runner nhận output standalone, static, public cùng custom-server, open-sse, src/mitm và các module cần thiết.[17] Những file bổ sung nhắc mình không nên coi mọi thứ ngoài output chính là rác. File tracing không thay thế hiểu biết về cách ứng dụng và tiến trình con tìm file lúc chạy.

Runtime còn có các dependency lazy wreq-js và playwright-core được cài riêng; phiên bản ở bước này chưa pin.[17] Đây vừa là nhu cầu chức năng vừa là khoảng trống về kiểm soát đầu vào. Native module cũng phải phù hợp thư viện nền và kiến trúc, không thể build ở đâu rồi copy sang đâu cũng được. Smoke main đã kiểm tra một số đường nạp module, nhưng chưa kiểm tra mọi tính năng của chúng.[19][24] Bài học là tách stage rồi xác minh từng nhóm artifact, không cắt bỏ theo cảm giác.”

**Chỉ sơ đồ:** builder giữ compiler/cache; COPY chọn lọc qua runner. Nhắc các artifact ngoài standalone và dependency lazy là thành phần có chủ đích, cần kiểm chứng.

**Chuyển ý:** “Artifact đã chọn vẫn cần một nền tương thích; ở case này Wolfi đã được dùng thật.”

## Slide 8 — Chọn nền tảng

**Thời lượng dự kiến:** 1 phút 30 giây.

**Lời nói:**

“Em vẫn giữ bảng các hướng Alpine, Debian slim, distroless và Wolfi để hỏi workload cần gì, không để xếp hạng nền nào luôn tốt nhất. Nền nhỏ nhưng thiếu thư viện hoặc làm native dependency đổi hành vi có thể tăng chi phí nhiều hơn phần dung lượng tiết kiệm.

Với case hiện tại, Wolfi không còn là ứng viên chưa chọn. Dockerfile đã pin wolfi-base theo digest sha256:771146c2dfc880902a185f060c3db5571473c46b267edd98c3119c83068dfb61 và cài nodejs-22. Main đã build và smoke thành công trên amd64.[17][24] Kết quả này có giá trị thực, nhưng không mở rộng thành đã benchmark các nền khác hoặc đã kiểm chứng mọi kiến trúc.

Wolfi là userspace hướng container, không có kernel riêng. Cùng dùng apk không có nghĩa trộn package Wolfi với Alpine là tương thích.[5][8] Phải xem Node, native module, thư viện, user và quyền dữ liệu cùng nhau. Tương thích cũng khác độ tin cậy nguồn: tên Wolfi hay một digest không tự xác minh chữ ký hoặc provenance của image cuối do mình build. Tài liệu image Node của Chainguard là tham khảo riêng, không phải chứng cứ bản custom hiện tại chính là image Node đó.[11][12] Chọn nền đúng là quyết định theo workload với bằng chứng giới hạn rõ, không phải lời hứa zero CVE.”

**Chỉ sơ đồ:** đi qua workload trước; dừng ở “Wolfi đã dùng”. Phân biệt kết quả amd64 với các lựa chọn chưa đối chứng.

**Chuyển ý:** “Nền chạy được rồi, tối thiểu runtime vẫn phải đủ để vận hành.”

## Slide 9 — Runtime tối thiểu

**Thời lượng dự kiến:** 1 phút 25 giây.

**Lời nói:**

“Tối thiểu không có nghĩa xóa càng nhiều càng tốt. Cần giữ artifact thực sự dùng, giấy phép theo nghĩa vụ phân phối và metadata phục vụ truy vết. Strip binary hoặc xóa hàng loạt node_modules để đẹp dung lượng mà chưa hiểu cách chạy có thể làm mất chức năng hoặc khả năng điều tra.

Runner hiện dùng USER nonroot, có ffmpeg và libstdc++, đồng thời bố trí owner cho DATA_DIR và HOME.[17] ffmpeg và dependency lazy không tự là phần dư: cần xem tính năng sử dụng chúng. Compose bind dịch vụ vào localhost, bật init, bỏ capability và no-new-privileges, dùng named volumes.[18] Đó là cấu hình giảm quyền cụ thể, không phải bằng chứng ứng dụng không còn lỗi.

Smoke đã assert UID 65532, thử ghi thư mục và restart đọc lại marker.[19][24] Nhưng smoke không gắn named volume của Compose và không kiểm tra media bằng ffmpeg. Restart cùng container cũng chưa chứng minh xóa rồi tạo lại container với volume sẽ giữ đúng dữ liệu và quyền. Vì vậy em nói non-root đã có và một số quyền ghi đã được kiểm tra, không nói toàn bộ vòng đời lưu trữ đã đạt. Runtime đủ dùng phải đi cùng quyền và dữ liệu đúng, không chỉ có dòng USER trong Dockerfile.”

**Chỉ sơ đồ:** non-root, least privilege, needed files rồi ffmpeg/lazy deps và licenses; nhấn giữ thành phần có lý do thay vì blind strip.

**Chuyển ý:** “Một runtime rõ ràng vẫn cần đầu vào truy vết được và cách cập nhật có kiểm soát.”

## Slide 10 — Khóa nguồn vào

**Thời lượng dự kiến:** 1 phút 25 giây.

**Lời nói:**

“Tag là tên có thể được cập nhật; digest nhận diện nội dung artifact được chọn. Pin giúp kiểm soát thay đổi, nhưng không tự chứng minh nguồn đáng tin hoặc toàn bộ build tái lập. Ở đây source upstream và base đã pin, còn bước npm install và dependency lazy vẫn là giới hạn đã nêu.[17][20]

Renovate đang quản lý Dockerfile và GitHub Actions, pinDigests bật và automerge tắt.[21][22] Run 41964645996 đã thành công, tạo PR #1 pin digest frontend docker/dockerfile và PR #2 cập nhật frontend. Tại snapshot kiểm tra hai PR còn mở, CI ở trạng thái cần phê duyệt; không gọi chúng là đã pass hay đã merge.[26][28][29] Cấu hình này không đồng nghĩa Renovate tự nâng upstream commit hoặc quản lý toàn bộ npm.

Quy trình có ích là PR nêu thay đổi, CI kiểm tra đúng revision rồi người review quyết định. Ngoài ra, lịch rebuild hằng tuần có thể tạo image mới cho cùng packaging commit vì đầu vào khác còn thay đổi. Do đó tag theo SHA source không đủ để chọn đúng artifact của một lần chạy. Khi đối chiếu smoke, publish hoặc báo cáo, ưu tiên run tag và digest. Khóa nguồn vào là khả năng truy vết và chủ động cập nhật, không phải đóng băng mọi thứ rồi mặc định an toàn.”

**Chỉ sơ đồ:** tag → digest → review; vòng Renovate → PR. Nhấn “Digest ≠ Trust” và phân biệt PR được tạo với CI được chấp nhận.

**Chuyển ý:** “Đầu vào có hồ sơ rồi, mình cần nhìn vào đầu ra thay vì chỉ đọc Dockerfile.”

## Slide 11 — Nhìn vào image

**Thời lượng dự kiến:** 1 phút 25 giây.

**Lời nói:**

“Inspect layer giúp trả lời file nào được thêm ở đâu, file tạm có còn ở lớp thấp và thành phần nào chiếm chỗ. Sơ đồ này là phương pháp đọc artifact; chưa phải kết quả phân tích layer hay báo cáo lỗ hổng đã tạo cho image 9router hiện tại.

Sau góc nhìn file là góc nhìn thành phần. Syft tạo SBOM theo phạm vi thu thập; Grype đối chiếu package hệ điều hành và thư viện ngôn ngữ với dữ liệu lỗ hổng đã biết.[3][4] Layer, SBOM và scanner bổ sung nhau, không thay thế nhau. Repo hiện chưa có bước vulnerability scan; Grype và việc lưu báo cáo gắn artifact là phần cần bổ sung, không được kể như một gate đã chạy.[16][20]

Báo cáo sau này phải ghi digest image, phiên bản công cụ và trạng thái cơ sở dữ liệu. Khi đọc cần tách OS với npm rồi xem phiên bản, bản vá và khả năng áp dụng. Không lấy advisory lịch sử làm finding hiện tại nếu chưa xác minh, cũng không coi không có cảnh báo là logic xác thực và phân quyền an toàn.[2][3] Xóa metadata để scanner nhìn thấy ít hơn không phải sửa rủi ro. Mình muốn kiểm kê được rồi giải thích kết quả, không chỉ tìm một con số thấp để đưa lên slide.”

**Chỉ sơ đồ:** image → layers; image → SBOM → Grype. Dừng ở “Dự kiến scan” và ranh giới “Logic ≠ packages”.

**Chuyển ý:** “Khác với scan còn thiếu, runtime đã có một bộ smoke thật; em nói rõ nó kiểm tra gì.”

## Slide 12 — Kiểm chứng runtime

**Thời lượng dự kiến:** 1 phút 35 giây.

**Lời nói:**

“Correctness là cổng đầu tiên. Run main 41964645341 đã chạy smoke thành công trên image local vừa build trước khi publish.[19][20][24] Assertion gồm HTTP health và dashboard, UID 65532, better-sqlite3 thực hiện select 1, nạp wreq-js, playwright-core và sharp, thử ghi marker rồi restart đọc lại. Đây là kết quả thực tế, không còn là danh sách kiểm tra dự kiến.

Tuy nhiên mỗi assertion có phạm vi riêng. Nạp được một module không chứng minh mọi hành vi của module hoạt động. SQLite select 1 không thay thế kiểm tra toàn bộ lưu trữ ứng dụng. Dashboard trả HTTP thành công không phải UI automation. Restart cùng container đọc lại marker không phải bài thử named volume sau khi recreate. Smoke chưa kiểm tra live provider, media ffmpeg, shutdown timing hoặc tương đương đầy đủ các chức năng.[19]

Trên hình có shutdown với dấu hỏi vì đó vẫn là phần cần đo, không phải một assertion đã pass. Khi bổ sung đối chứng, hai image phải chạy cùng bộ hành vi và dữ liệu tổng hợp; không được bỏ tính năng để nhỏ hơn rồi gọi là tương đương. Nếu thay đổi làm startup hoặc dữ liệu sai thì quay lại thay đổi đó, không dùng điểm scanner để bù. Kết luận chính xác hôm nay là bộ smoke đã định nghĩa đã qua trên main, và phạm vi rộng hơn vẫn cần kiểm chứng.”

**Chỉ sơ đồ:** startup → health → restart đã có bằng chứng; dừng ở shutdown dấu hỏi và “Đối chứng còn thiếu”. Không gắn pass cho toàn bộ sơ đồ.

**Chuyển ý:** “Ngoài correctness, em tách một nhánh đánh giá bảo mật ứng dụng, nhưng nhánh này chưa được chạy.”

## Slide 13 — Kiểm thử động

**Thời lượng dự kiến:** 1 phút 15 giây.

**Lời nói:**

“Đây là phần bonus, không phải điều kiện để kể lại thành công build hiện tại. Strix là công cụ có repo chính thức, nhưng trong case này chưa cài và chưa chạy.[7] Không có báo cáo động nào để nói đã tìm ra hoặc đã loại trừ lỗ hổng của 0.5.112.

Nếu bổ sung một bài đánh giá ứng dụng, phạm vi phải được người phụ trách duyệt trước: lab local cách ly, dữ liệu giả, provider mock, giới hạn tài nguyên và điều kiện dừng. Không dùng tài khoản thật hoặc chạm dịch vụ bên thứ ba. Mục tiêu ở bài trình bày là thiết kế cách ghi nhận và review kết quả, không trình diễn khai thác hay tự động đưa thay đổi lên môi trường thật.

Vai trò của nhánh này cũng khác Grype. Scanner package đối chiếu thành phần với dữ liệu lỗ hổng; đánh giá hành vi ứng dụng cần ngữ cảnh và người đọc lại bằng chứng. Một kết quả của công cụ không tự trở thành finding đã xác nhận. Nó càng không phải giấy chứng nhận production-ready. Em giữ nhánh bonus riêng để tránh biến bài tối ưu Dockerfile thành một workflow tấn công tự động hoặc kéo dài phạm vi ngoài mục tiêu.”

**Chỉ sơ đồ:** optional lab → human review; chỉ “Synthetic only” và “Isolated local”. Không trình bày lệnh hay thao tác khai thác.

**Chuyển ý:** “Gộp lại trên pipeline sẽ thấy rõ đoạn nào có thật, đoạn nào còn thiếu.”

## Slide 14 — Pipeline tổng thể

**Thời lượng dự kiến:** 1 phút 35 giây.

**Lời nói:**

“Đường chính đã có là checkout source, buildx với load vào local, smoke đúng image vừa build, rồi tag và push chính image đã kiểm tra lên GHCR. Không rebuild một image khác sau smoke.[20] PR không publish. Những gate scan, review bảo mật ứng dụng và phê duyệt rủi ro chưa được cấu hình như một phần của đường này; Strix vẫn là nhánh lab riêng.

Để truy vết, main run 41964645341 dùng source 0.5.112. Run tag là ghcr.io/newnol/9router-wolfi:run-41964645341-1; log push ghi digest sha256:fb14153d9e76506f3fc2616f35f98ed3e6ae1f6851e2f626ecb8b16f5c4a098a.[24] Digest này được ghi từ log, không phải kết quả vừa pull lại registry tại máy trình bày. Chi tiết đó giúp phân biệt bằng chứng CI với một phép kiểm tra độc lập sau publish.

Run thành công mới hơn xét toàn repo là 41966436702, nhưng nó thuộc nhánh 0.4.41 với upstream commit khác và digest khác.[25] Không lấy nhãn ‘latest successful’ rồi suy đó là main hoặc cùng artifact. Renovate là đường tạo PR đầu vào, không phải một lần cập nhật nào cũng đã qua gate. Pipeline tốt ở chỗ nối được revision, image và assertion cụ thể; biểu tượng màu xanh không được che những phần chưa có bằng chứng.”

**Chỉ sơ đồ:** Git → build → smoke → tag → push GHCR; phân biệt đường Renovate PR, ô scan/review dấu hỏi và nhánh lab chưa chạy.

**Chuyển ý:** “Build và smoke xanh cho mình một mốc hợp lệ để bắt đầu đo, không tự là kết quả tối ưu.”

## Slide 15 — Đo trước sau

**Thời lượng dự kiến:** 1 phút 25 giây.

**Lời nói:**

“Bảng này cố ý ghi chưa đo ở cả baseline lẫn optimized. Chưa có số đối chứng về image size, build lạnh–ấm, startup, RAM hoặc CVE/noise của case 9router. Không lấy số từ lab Python cũ, không lấy thời gian một job CI hoặc dòng Next Ready làm kết quả so trước–sau.

Muốn phép đo có nghĩa, hai phía cần cùng revision ứng dụng, kiến trúc, workload và điều kiện máy. Chỉ thay yếu tố đang đánh giá và ghi mọi khác biệt không tránh được. Với build, phải nêu cache nào còn và mạng ảnh hưởng ra sao. Với runtime, phải thống nhất thời điểm bắt đầu, điều kiện sẵn sàng và khoảng quan sát. Chạy lặp lại rồi báo cách tổng hợp cùng độ dao động, thay vì chọn lần đẹp nhất.

Dung lượng cũng cần cùng định nghĩa: bytes nén phân phối và kích thước local không phải một con số. Với scanner, giữ tool và snapshot cơ sở dữ liệu tương đương, tách package và khả năng áp dụng; số cảnh báo không tự là thước đo hiệu năng hay bảo mật tổng thể. Chưa có baseline thì chưa thể kết luận Wolfi nhỏ hơn hoặc nhanh hơn nền khác. Kết quả hiện tại là đóng gói chạy qua smoke, còn lợi ích định lượng phải đến từ phép đo riêng.”

**Chỉ sơ đồ:** đọc từng hàng size, cold/warm, startup/RAM và CVE/noise; chỉ cả hai cột “Chưa đo”, không điền số minh họa dễ bị hiểu là kết quả.

**Chuyển ý:** “Vì vậy vòng tiếp theo không phải thêm công cụ cho đủ tên, mà là chọn một giả thuyết và kiểm tra.”

## Slide 16 — Vòng cải tiến

**Thời lượng dự kiến:** 1 phút 20 giây.

**Lời nói:**

“Vòng em muốn giữ là measure, optimize, validate. Đầu tiên xác định baseline cùng một câu hỏi cụ thể. Tiếp theo thay đổi nhỏ có lý do, rồi kiểm tra cả hành vi lẫn số đo. Nếu cải thiện một chỉ số nhưng làm mất chức năng hoặc khó bảo trì hơn, mình không tự coi đó là tối ưu thành công.

Đến đây có thể khẳng định repo packaging Wolfi tồn tại, main dùng source 0.5.112 và đã build, smoke, publish. Python main ở DockerFile-Contest vẫn độc lập. Cũng phải giữ nguyên phần chưa biết: chưa có scan lỗ hổng, chưa đánh giá động, chưa benchmark trước–sau và chưa kiểm tra tương đương đầy đủ. Main thành công không xóa những khoảng trống này; build nhánh 0.4.41 cũng không thay thế kết quả main.

Điểm cần mentor quyết định là tiêu chí chấp nhận và thứ tự làm tiếp: ưu tiên bộ kiểm tra rộng hơn, kiểm soát đầu vào dependency, phép đo đối chứng và review kết quả theo phạm vi. Không gọi sản phẩm production-ready trước khi có bằng chứng phù hợp. Kết luận của bài là tối ưu Dockerfile không chỉ làm image nhỏ: phải hiểu thứ đã đóng gói, kiểm soát thay đổi, giữ workload chạy đúng và nói được mỗi kết luận dựa trên bằng chứng nào.”

**Chỉ sơ đồ:** measure → optimize → validate → quay lại; dừng ở mentor decision như quyết định phạm vi và tiêu chí, không như dấu đã nghiệm thu.

**Chuyển ý:** “Em xin chốt ở phương pháp và ranh giới bằng chứng đó; phần còn lại là thống nhất phép kiểm chứng tiếp theo.”

## Nguồn và bằng chứng

Các số [n] trỏ tới ID trong `sources.json`; ngày truy cập và snapshot kiểm tra được giữ ở đó. Các URL theo commit là ảnh chụp nguồn, còn run/PR là bằng chứng lịch sử tương ứng, không bảo đảm trạng thái mới nhất tại mọi lần trình bày.

- [1] [Release 0.4.41 — bối cảnh lịch sử](https://github.com/decolua/9router/releases/tag/v0.4.41); [2] [advisory chính thức](https://github.com/decolua/9router/security/advisories/GHSA-vjc7-jrh9-9j86). Không chuyển phạm vi advisory thành finding của 0.5.112.
- [3] [Grype](https://github.com/anchore/grype); [4] [Syft](https://github.com/anchore/syft): khả năng công cụ, không phải báo cáo đã chạy cho case này.
- [5] [Wolfi OS](https://github.com/wolfi-dev/os); [8] [Wolfi overview](https://edu.chainguard.dev/open-source/wolfi/overview): mô hình userspace và tương thích.
- [6] [Renovate Docker](https://docs.renovatebot.com/docker): pin/cập nhật digest; [7] [Strix](https://github.com/usestrix/strix): tham khảo cho nhánh bonus chưa chạy.
- [9] [Dockerfile upstream 0.4.41](https://raw.githubusercontent.com/decolua/9router/v0.4.41/Dockerfile); [10] [manifest 0.4.41](https://raw.githubusercontent.com/decolua/9router/v0.4.41/package.json): chỉ là tham khảo lịch sử, không mô tả source main hiện tại.
- [11] [Chainguard Node provenance](https://images.chainguard.dev/directory/image/node/provenance); [12] [Node overview](https://images.chainguard.dev/directory/image/node/overview): tài liệu image riêng, không tự xác minh provenance của custom image.
- [13] [Docker cache](https://docs.docker.com/build/cache/optimize); [14] [multi-stage](https://docs.docker.com/build/building/multi-stage); [15] [image layers](https://docs.docker.com/get-started/docker-concepts/building-images/understanding-image-layers): nền tảng phương pháp.
- [16] [README packaging tại snapshot](https://github.com/newnol/9router-wolfi/blob/c65f395e53869315170005a676d768954f1d8a84/README.md); [17] [Dockerfile](https://github.com/newnol/9router-wolfi/blob/c65f395e53869315170005a676d768954f1d8a84/Dockerfile); [18] [Compose](https://github.com/newnol/9router-wolfi/blob/c65f395e53869315170005a676d768954f1d8a84/compose.yaml); [19] [smoke assertions](https://github.com/newnol/9router-wolfi/blob/c65f395e53869315170005a676d768954f1d8a84/smoke-test.sh).
- [20] [Build workflow](https://github.com/newnol/9router-wolfi/blob/c65f395e53869315170005a676d768954f1d8a84/.github/workflows/build.yml); [21] [Renovate workflow](https://github.com/newnol/9router-wolfi/blob/c65f395e53869315170005a676d768954f1d8a84/.github/workflows/renovate.yml); [22] [Renovate config](https://github.com/newnol/9router-wolfi/blob/c65f395e53869315170005a676d768954f1d8a84/renovate.json).
- [23] [Manifest upstream pin — 0.5.112](https://github.com/decolua/9router/blob/1fe586bb1cf35e1ed0cb2150a8ef7d1db040b21d/package.json).
- [24] [Main build/smoke/publish run 41964645341](https://github.com/newnol/9router-wolfi/actions/runs/41964645341); [25] [build nhánh 0.4.41 run 41966436702](https://github.com/newnol/9router-wolfi/actions/runs/41966436702): source và image khác nhau, không tráo bằng chứng.
- [26] [Renovate run 41964645996](https://github.com/newnol/9router-wolfi/actions/runs/41964645996); [27] [repo packaging-only](https://github.com/newnol/9router-wolfi); [28] [PR #1](https://github.com/newnol/9router-wolfi/pull/1); [29] [PR #2](https://github.com/newnol/9router-wolfi/pull/2).

**Artifact main đã ghi nhận trong snapshot:** packaging commit `c65f395e53869315170005a676d768954f1d8a84`; upstream commit `1fe586bb1cf35e1ed0cb2150a8ef7d1db040b21d`; run tag `ghcr.io/newnol/9router-wolfi:run-41964645341-1`; digest từ log push `sha256:fb14153d9e76506f3fc2616f35f98ed3e6ae1f6851e2f626ecb8b16f5c4a098a`. Nhánh 0.4.41 dùng upstream `cebc72e3438dca5aad69b2828cb0d0f2e54b168d` và digest từ log `sha256:aac7738fc50f62dc461bc911270481391022bd00a3c54588af8de9a01d875caf`. Không dùng tag SHA có thể được cập nhật qua rebuild để thay cho nhận diện artifact theo run/digest.
