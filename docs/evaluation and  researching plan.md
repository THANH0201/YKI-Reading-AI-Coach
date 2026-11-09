# Kế hoạch hoàn thành thesis

## 1. Mục đích và nguyên tắc

Tài liệu này là kế hoạch công việc để hoàn thiện thesis dựa trên dự án
YKI Reading AI Coach và bản thảo hiện có trong `README.md`. Trọng tâm nghiên
cứu là đo lường ba yêu cầu chất lượng của ứng dụng:

1. Mức độ câu hỏi tuân thủ định dạng phần đọc YKI được xác nhận từ tài liệu
   chính thức.
2. Tỷ lệ đề có toàn bộ đáp án chính xác 100%.
3. Tỷ lệ giải thích từ vựng của AI Tutor đúng nghĩa trong ngữ cảnh bài đọc.

### Nguyên tắc không được bỏ qua

- Không bịa số liệu, trích dẫn, người đánh giá, nguồn bài đọc hoặc kết quả.
- Không gọi cấu trúc câu hỏi hiện tại là format YKI cho tới khi đối chiếu
  được với nguồn chính thức.
- Phân biệt kiểm thử phần mềm bằng câu trả lời giả lập với đánh giá đầu ra
  thật từ API.
- Khóa tiêu chí, rubric, mẫu số và cách xử lý lỗi API trước khi xem kết quả
  đánh giá.
- Lưu cả đầu ra thành công và thất bại; không loại các lần chạy không thuận
  lợi khỏi mẫu số nếu đang báo cáo hiệu quả đầu-cuối.
- Tôn trọng quyền tác giả, điều khoản dịch vụ AI, bảo mật API key và quy
  định đạo đức nghiên cứu của trường.
- Không kết luận công cụ cải thiện khả năng đọc hiểu nếu không có thiết kế
  nghiên cứu đo kết quả học tập.

## 2. Định nghĩa trạng thái

- **Chưa bắt đầu:** chưa có tài liệu hoặc đầu ra kiểm chứng.
- **Đang làm:** có người phụ trách và đầu ra chưa được duyệt.
- **Chờ duyệt:** cần giảng viên, chuyên gia, ethics board hoặc trường xác
  nhận trước khi đi tiếp.
- **Hoàn thành:** đầu ra tồn tại, được kiểm tra và có bằng chứng lưu lại.
- **Không áp dụng:** được giải thích và thống nhất với giảng viên; không tự
  bỏ mục chỉ vì khó thực hiện.

Không đánh dấu mục “Hoàn thành” chỉ vì đã đọc hoặc dự định làm. Mỗi mục cần
có artefact hoặc bằng chứng kiểm tra được.

## 3. Phạm vi nghiên cứu được đề xuất

### 3.1. Câu hỏi nghiên cứu

- **RQ1 – Tuân thủ format:** Trong tập lượt sinh được đánh giá, tỷ lệ tiêu
  chí format YKI đạt là bao nhiêu và tỷ lệ lượt sinh đạt tất cả tiêu chí
  bắt buộc là bao nhiêu?
- **RQ2 – Độ chính xác answer key:** Bao nhiêu phần trăm lượt sinh có mọi
  câu trả lời/đáp án đúng và được hỗ trợ bởi bài đọc? Một lượt sinh chỉ đạt
  nếu **tất cả câu đều đúng 100%**.
- **RQ3 – Tutor và ngữ cảnh:** Bao nhiêu phần trăm yêu cầu giải thích từ
  vựng được Tutor giải thích đúng hoàn toàn theo nghĩa của từ trong câu
  thuộc bài đọc?

### 3.2. Phạm vi kết luận

Thesis đánh giá một ứng dụng cụ thể, với model, prompt, cấu hình, ngôn ngữ,
tập bài và ngày chạy được ghi nhận. Kết quả không tự áp dụng cho mọi model,
mọi phiên bản API, mọi bài đọc tiếng Phần Lan hay mọi đề YKI. Nếu ứng dụng
không mô phỏng đúng định dạng chính thức, RQ1 phải báo cáo mức không tuân
thủ; không được nới tiêu chí sau khi thấy kết quả.

**Cổng quyết định 1:** Trước thu thập dữ liệu, giảng viên hướng dẫn xác nhận
ba RQ, phạm vi YKI, tiêu chí strict 100%, cỡ mẫu khả thi và năng lực người
đánh giá. Nếu không xác nhận, dừng trước khi chạy nghiên cứu chính thức.

## 4. Lộ trình tổng quan

Thứ tự là quan trọng; không chạy đánh giá chính trước khi rubric và nguồn
tham chiếu được khóa.

| Giai đoạn | Công việc chính | Đầu ra bắt buộc | Điều kiện bắt đầu giai đoạn sau |
|---|---|---|---|
| 0 | Chốt đề tài với giảng viên | Phê duyệt RQ, scope, định dạng trường, ethics | Câu hỏi và phương pháp được duyệt |
| 1 | Nghiên cứu nguồn YKI và tài liệu liên quan | Bộ nguồn chính thức, tổng quan tài liệu, checklist dự thảo | Checklist được giảng viên duyệt |
| 2 | Thiết kế nghiên cứu và mẫu đánh giá | Dataset protocol, rubric RQ1–RQ3, kế hoạch người chấm | Pilot hoàn tất, rubric khóa |
| 3 | Chuẩn bị ứng dụng và khả năng lặp lại | Kiểm thử xanh, phiên bản code/model/prompt được ghi nhận | Lượt pilot có thể tái kiểm tra |
| 4 | Pilot và chỉnh quy trình | Báo cáo pilot, bản rubric cuối | Có phê duyệt chạy chính |
| 5 | Thu thập và chấm dữ liệu | Raw outputs, rating độc lập, nhật ký API | Dataset đầy đủ, có audit |
| 6 | Phân tích | Bảng số liệu, CI, phân tích lỗi, biểu đồ | Tất cả RQ có kết quả hoặc nêu rõ chưa trả lời |
| 7 | Viết và phản biện thesis | Bản chương hoàn chỉnh, trích dẫn đúng | Giảng viên góp ý, bản sửa |
| 8 | Hoàn tất nộp | Word/PDF theo mẫu, phụ lục, kiểm tra cuối | Không còn placeholder hoặc kết quả chưa xác minh |

**Thời lượng:** tự điền sau khi biết ngày nộp và lịch giảng viên:

| Mốc | Ngày bắt đầu | Hạn hoàn thành | Người duyệt |
|---|---|---|---|
| Phê duyệt phạm vi | [điền] | [điền] | [điền] |
| Phê duyệt protocol và rubric | [điền] | [điền] | [điền] |
| Pilot | [điền] | [điền] | [điền] |
| Thu thập dữ liệu | [điền] | [điền] | [điền] |
| Phân tích | [điền] | [điền] | [điền] |
| Bản thesis hoàn chỉnh | [điền] | [điền] | [điền] |
| Bản cuối theo template | [điền] | [điền] | [điền] |

## 5. Giai đoạn 0 — Chốt phạm vi với giảng viên

### Công việc

- [ ] Gửi đề tài và ba RQ ở Mục 3 cho giảng viên hướng dẫn.
- [ ] Xác nhận thesis được chấm theo cấu trúc mẫu Metropolia hay template
  khác; lấy đúng file Word/template và rubric chấm điểm.
- [ ] Xác nhận title nên dùng “phát triển và đánh giá” thay vì tuyên bố
  nghiên cứu/huấn luyện mô hình AI.
- [ ] Hỏi giảng viên có chấp nhận RQ1 là “mức tuân thủ checklist format” hay
  muốn đo thêm các khía cạnh độ khó/đáp ứng năng lực.
- [ ] Xác nhận định nghĩa đề đúng 100%: một câu sai, mơ hồ, không xác minh
  được hoặc đề không sinh thành công xử lý như thế nào.
- [ ] Xác nhận đối tượng nào đủ chuyên môn để chấm tiếng Phần Lan và format
  YKI; cần bao nhiêu người chấm.
- [ ] Xác nhận yêu cầu ethics/consent, quyền dùng bài báo, dữ liệu/API và
  việc đưa prompt/đầu ra lên dịch vụ bên ngoài.
- [ ] Xác nhận cỡ mẫu và thời gian khả thi. Không tự xem đề xuất số lượng
  trong kế hoạch này là cỡ mẫu thống kê đã được chứng minh.

### Đầu ra

- Email/biên bản ý kiến giảng viên.
- Phiên bản chốt RQ, scope, title, phương pháp và lịch nộp.
- Danh sách nội dung phải có theo template chính thức.

### Điều kiện hoàn thành

Không còn tranh cãi về việc “format YKI”, “đúng 100%” và “đúng nghĩa theo
ngữ cảnh” được hiểu thế nào. Nếu chưa chốt được, chưa chạy dataset chính.

## 6. Giai đoạn 1 — Nguồn chính thức và tổng quan nghiên cứu

### 6.1. Xác minh format YKI cho RQ1

- [ ] Tìm tài liệu chính thức, phiên bản còn hiệu lực, mô tả phần thi đọc và
  sample items được phép sử dụng.
- [ ] Lưu URL, tên cơ quan, ngày xuất bản/cập nhật, ngày truy cập, trang hoặc
  mục cụ thể.
- [ ] Phân biệt rõ thông tin chính thức với bài viết thứ cấp, blog, diễn đàn
  hoặc tự suy luận.
- [ ] Trích các thuộc tính có thể quan sát trong output của ứng dụng: kiểu
  tác vụ, hướng dẫn, loại phản hồi, cấu trúc câu hỏi/đáp án, cách dựa trên
  văn bản — chỉ giữ mục thực sự được nguồn xác nhận.
- [ ] Xác định thuộc tính nào không đánh giá được chỉ từ bộ 5 câu hiện có.
- [ ] Đối chiếu cấu trúc hiện tại (2 multiple-choice, 2 true/false, 1 open)
  với nguồn. Nếu không tương ứng, ghi nhận là thiếu sót/điểm không tuân thủ;
  thảo luận với giảng viên xem có cần sửa generator trước khi đo hay đo
  nguyên trạng.
- [ ] Không gọi “tuân thủ format” là “tương đương đề thi chính thức”; hai
  kết luận này không giống nhau.

### 6.2. Tổng quan tài liệu

- [ ] Tìm nghiên cứu về đánh giá đọc hiểu/ngôn ngữ thứ hai và giá trị của
  bài kiểm tra (test validity).
- [ ] Tìm nghiên cứu về automatic question generation và rubric đánh giá
  tính đúng, tính liên quan, answerability, ambiguity.
- [ ] Tìm nghiên cứu về LLM trong language learning/assessment, đặc biệt
  giới hạn hallucination và độ ổn định đầu ra.
- [ ] Tìm nghiên cứu về nghĩa từ vựng theo ngữ cảnh, đa nghĩa và biến tố
  tiếng Phần Lan.
- [ ] Tìm giải pháp/tài nguyên học tập cụ thể làm đối tượng so sánh.
- [ ] Mỗi nguồn được đọc từ trang nhà xuất bản, DOI, cơ quan chính thức hoặc
  bản toàn văn có thẩm quyền; xác minh năm, tiêu đề, tác giả và số trang.
- [ ] Ghi lại: câu hỏi nghiên cứu, dữ liệu, phương pháp, kết quả, giới hạn,
  liên quan đến thesis và trích dẫn đầy đủ.
- [ ] Lập bảng tổng quan tài liệu theo chủ đề; không chỉ liệt kê bài báo.
- [ ] Xác định khoảng trống từ bằng chứng trong tài liệu; không khẳng định
  “chưa ai làm” khi chưa có tìm kiếm hệ thống phù hợp.

### Đầu ra

- Bảng trích nguồn YKI và checklist format draft.
- Bảng tổng quan tài liệu, bảng so sánh tài nguyên.
- Danh sách tài liệu tham khảo đã xác minh và trích dẫn trong thân thesis.

### Điều kiện hoàn thành

Mỗi tiêu chí RQ1 có nguồn gốc truy ngược được. Mỗi tuyên bố trong Chương 3–4
được trích dẫn hoặc được đánh dấu là mô tả hệ thống hiện tại.

## 7. Giai đoạn 2 — Protocol nghiên cứu và rubric

### 7.1. Chốt mẫu và đơn vị phân tích

- [ ] Xác định tiêu chí đưa bài vào: ngôn ngữ, độ dài, loại văn bản, quyền
  sử dụng, mức phù hợp chủ đề.
- [ ] Xác định tiêu chí loại bài trước khi chạy AI; ghi lý do loại.
- [ ] Cân bằng hoặc mô tả phân bố độ dài, chủ đề và mức độ bài nếu có nhãn
  CEFR đã được xác nhận.
- [ ] Chọn đơn vị cho RQ1/RQ2 là **lượt yêu cầu sinh đề**, không chỉ là bài
  đọc. Một bài có thể sinh nhiều đề.
- [ ] Chọn đơn vị cho RQ3 là **một yêu cầu giải thích một từ/cụm từ trong
  một câu/ngữ cảnh cụ thể**.
- [ ] Chọn số bài, số lượt sinh đề mỗi bài, số từ mỗi bài và tổng lượt Tutor
  sau khi hỏi ý kiến giảng viên. Ghi rationale; không dùng số nhỏ để suy ra
  đại diện toàn bộ YKI.
- [ ] Nếu mỗi bài có nhiều lượt sinh, gắn `article_id`, `generation_id` và
  `run_id` để giữ cấu trúc lặp.
- [ ] Lập kế hoạch xử lý output lỗi/timeout, lỗi schema, lỗi Tutor, kết quả
  trống, retry và chi phí API. Quy tắc phải được viết trước khi chạy.

### 7.2. Hoàn thiện rubric RQ1

- [ ] Tạo bảng ánh xạ: yêu cầu nguồn YKI → tiêu chí → cách quan sát → điều
  kiện đạt/không đạt → ví dụ.
- [ ] Định nghĩa rõ các mục bắt buộc và mục không áp dụng; không được xóa
  tiêu chí sau khi thấy điểm.
- [ ] Xác định hai chỉ số: tỷ lệ mục checklist đạt; tỷ lệ lượt sinh đạt
  toàn bộ mục bắt buộc.
- [ ] Quy định output API lỗi được tính trong mẫu số nào; báo riêng tỷ lệ
  thành công dịch vụ.
- [ ] Xin giảng viên/chuyên gia xác nhận nội dung checklist trước pilot.

### 7.3. Hoàn thiện rubric RQ2

- [ ] Người đánh giá lập answer key trước khi xem đáp án AI.
- [ ] Với mỗi câu, lưu đoạn/các đoạn bằng chứng trong bài.
- [ ] Với câu mở, xác định ý bắt buộc, diễn đạt tương đương có thể chấp nhận
  và trường hợp không đủ thông tin.
- [ ] Định nghĩa câu hỏi mơ hồ, có nhiều đáp án, không answerable, sai sự
  thật hoặc cần kiến thức ngoài bài là lỗi gì.
- [ ] Tính độ chính xác theo từng câu để chẩn đoán.
- [ ] Tính chỉ số chính strict: lượt sinh chỉ đạt khi **mọi đáp án đúng,
  xác định và được hỗ trợ bởi bài**.
- [ ] Đầu ra invalid/không tạo được đề tính thất bại trong tỷ lệ end-to-end;
  có thể tính thêm accuracy có điều kiện trên đề thành công nhưng phải nêu
  rõ mẫu số.

### 7.4. Hoàn thiện rubric RQ3

- [ ] Chọn từ/cụm từ thực sự xuất hiện trong bài; giữ câu nguồn và vị trí.
- [ ] Tạo nghĩa tham chiếu theo ngữ cảnh độc lập trước khi xem Tutor.
- [ ] Phân tầng mẫu từ: danh từ/động từ/tính từ/cụm từ; đa nghĩa; biến tố;
  idiom — chỉ áp dụng nhóm có trong phạm vi nghiên cứu.
- [ ] Dùng cùng một template prompt, ngôn ngữ đầu ra và lượng ngữ cảnh cho
  mọi mục thử nghiệm.
- [ ] Định nghĩa “đúng hoàn toàn”: nghĩa trọng tâm phù hợp câu và không có
  khẳng định sai làm thay đổi cách hiểu.
- [ ] Quy định trả lời trống, lỗi API, refusal và lỗi dịch tính vào chỉ số
  end-to-end hay chỉ báo riêng.
- [ ] Nếu đánh giá lemma/part of speech/inflection, tạo tiêu chí con riêng;
  không tự gộp vào accuracy nghĩa.

### 7.5. Người chấm và độ tin cậy

- [ ] Xác nhận số lượng và tiêu chuẩn người chấm với giảng viên.
- [ ] Chuẩn bị hướng dẫn chấm, ví dụ chuẩn và cách ghi lý do.
- [ ] Làm vòng calibration trên một nhóm nhỏ chưa dùng cho phân tích chính
  hoặc ghi rõ nếu pilot được đưa vào phân tích.
- [ ] Chấm độc lập trước khi thảo luận; lưu raw ratings riêng.
- [ ] Chọn cách đo độ đồng thuận phù hợp với thang điểm/nhãn và số người
  chấm cùng giảng viên; không chọn chỉ số sau khi nhìn số liệu.
- [ ] Định nghĩa cách hòa giải và ai quyết định khi bất đồng.

### Đầu ra và cổng duyệt

- Protocol v1 có ngày/version.
- Rubric RQ1, RQ2, RQ3 hoàn chỉnh.
- Dataset schema và kế hoạch phân tích.
- Phê duyệt ethics/consent nếu cần.

**Cổng quyết định 2:** Không bắt đầu thu thập chính thức nếu chưa có protocol
và rubric được duyệt.

## 8. Giai đoạn 3 — Chuẩn bị phần mềm và tính lặp lại

### 8.1. Khắc phục và xác nhận phần mềm

- [ ] Điều tra ba kiểm thử giao diện thất bại đã được ghi nhận trong
  `README.md`: tìm nút “Start Exam”, thông báo “Level: B1”, tiêu đề
  “Exam Result”. Xác định nguyên nhân thực tế; không chỉ sửa assertion để
  làm test xanh nếu hành vi UI vẫn hỏng.
- [ ] Xác định các test đó còn phù hợp với UI hiện tại không; cập nhật test
  theo behavior mong muốn, có lý do rõ ràng.
- [ ] Chạy test tập trung sau sửa, rồi chạy toàn suite.
- [ ] Ghi phiên bản Python, dependency, hệ điều hành, lệnh, ngày và kết quả.
- [ ] Lưu log test nhưng không lưu secret hoặc dữ liệu người dùng.

### 8.2. Bảo đảm khả năng tái lập thí nghiệm

- [ ] Gắn mã phiên bản/commit cho code chạy đánh giá.
- [ ] Lưu prompt hoàn chỉnh cho level detector, subject classifier, question
  generator và Tutor; đánh version hoặc checksum.
- [ ] Ghi model ID cấu hình và model ID do response API trả về nếu có; không
  giả định alias model luôn trỏ đến cùng weights.
- [ ] Ghi ngày giờ, tham số sinh, timeout/retry và trạng thái API.
- [ ] Lưu nguyên bản đầu vào/đầu ra hoặc ID tham chiếu bảo mật theo quyền sử
  dụng; không để API key trong CSV, log, README hay git.
- [ ] Nếu ứng dụng hiện không lưu raw output hoặc metadata, quyết định trước
  cách ghi nhận nghiên cứu: export thủ công có kiểm soát hoặc bổ sung logging
  tối thiểu. Không ghi toàn bộ văn bản có bản quyền nếu điều khoản không cho
  phép.
- [ ] Tạo data dictionary: mỗi cột, kiểu dữ liệu, ví dụ, giá trị hợp lệ,
  missing/error semantics.
- [ ] Tách raw data bất biến khỏi bản đã làm sạch/đánh giá; ghi lại mọi phép
  biến đổi.

### Đầu ra

- Toàn bộ test đã chạy, lỗi còn lại được giải thích.
- Protocol lưu metadata, prompt version, raw output và API failures.
- Dataset schema/data dictionary.

## 9. Giai đoạn 4 — Pilot

### Công việc

- [ ] Chạy thử pipeline trên một số ít bài khác nhau; số lượng pilot do
  giảng viên duyệt.
- [ ] Kiểm tra có lấy được output và metadata cần thiết không.
- [ ] Cho người chấm thử rubric; ghi câu nào khó hiểu hoặc có thể diễn giải
  theo nhiều cách.
- [ ] Kiểm tra định nghĩa “đề đạt 100%” trên câu mở và câu mơ hồ.
- [ ] Kiểm tra template RQ3 không vô tình gợi sẵn nghĩa hoặc dùng ngữ cảnh
  khác nhau giữa các mục.
- [ ] Đo thời gian, lỗi dịch vụ và chi phí/API limit.
- [ ] Ghi mọi thay đổi rubric/protocol sau pilot; phát hành phiên bản cuối
  trước nghiên cứu chính.
- [ ] Quyết định có đưa pilot vào mẫu chính hay loại; quyết định trước khi
  xem kết quả chính và nêu rõ trong thesis.

### Cổng quyết định 3

Chỉ chạy nghiên cứu chính nếu: pipeline ghi đủ dữ liệu, người chấm hiểu
rubric, nguồn và quyền sử dụng hợp lệ, chi phí khả thi, và giảng viên duyệt
protocol cuối.

## 10. Giai đoạn 5 — Thu thập dữ liệu chính thức

### 10.1. Đánh giá RQ1 và RQ2

- [ ] Chạy từng bài theo protocol đã khóa.
- [ ] Giữ tất cả output: hợp lệ, invalid JSON, câu thiếu, lỗi API, timeout
  và response không đáp ứng schema.
- [ ] Không retry âm thầm. Mỗi lần retry là generation mới, ghi liên kết với
  lần trước và lý do retry.
- [ ] Gán ID không chứa thông tin cá nhân cho từng bài/lượt sinh/câu.
- [ ] Chấm checklist RQ1 độc lập.
- [ ] Lập/kiểm tra answer key và bằng chứng câu văn theo quy trình RQ2.
- [ ] Hai người chấm ghi kết quả trước khi trao đổi.
- [ ] Theo dõi mẫu số theo ba cấp: yêu cầu gửi, lần API thành công, đề hợp
  lệ được đánh giá.
- [ ] Kiểm tra đầy đủ dữ liệu hằng ngày; không đợi đến cuối để phát hiện
  output hoặc metadata bị mất.

### 10.2. Đánh giá RQ3

- [ ] Chọn mẫu từ/cụm từ theo quy tắc đã khóa; tránh chỉ chọn ví dụ dễ.
- [ ] Chuẩn bị nghĩa tham chiếu/ngữ cảnh trước khi xem phản hồi Tutor.
- [ ] Gửi cùng template prompt và context nhất quán cho Tutor.
- [ ] Ghi riêng lỗi MyMemory, lỗi gọi Groq, trả lời rỗng và từ chối.
- [ ] Chấm đúng/sai hoàn toàn và mã lỗi từng câu.
- [ ] Giữ phản hồi nguyên bản để audit, theo giới hạn quyền lưu trữ/API.

### Kiểm soát chất lượng

- [ ] Kiểm tra ID trùng, thiếu cột, output mất, timestamp sai và số lượt
  không khớp.
- [ ] Kiểm tra ngẫu nhiên một phần phiếu so với raw output.
- [ ] Tính tỷ lệ missing, lỗi API và invalid output trước khi phân tích chất
  lượng.
- [ ] Khóa raw dataset; chỉ sửa lỗi qua bản clean có nhật ký biến đổi.

## 11. Giai đoạn 6 — Phân tích số liệu và thảo luận

### 11.1. Phân tích RQ1

- [ ] Tính số mục đạt/tổng mục áp dụng; công bố cách xử lý không áp dụng.
- [ ] Tính điểm mỗi generation, trung bình/tỷ lệ theo đề và strict pass rate
  đạt mọi tiêu chí bắt buộc.
- [ ] Báo cáo tử số, mẫu số, phần trăm và khoảng tin cậy.
- [ ] Phân tích từng tiêu chí, không chỉ gộp một con số.
- [ ] Xem riêng trường hợp ứng dụng không thể biểu diễn một yêu cầu format.
- [ ] Giải thích tiêu chí nào không thể đánh giá từ output hiện có.
- [ ] Không khẳng định độ khó hoặc giá trị đo lường tương đương YKI nếu
  không thực sự kiểm tra hai thuộc tính đó.

### 11.2. Phân tích RQ2

- [ ] Báo độ chính xác cấp câu để chẩn đoán, tách theo loại câu nếu mẫu đủ.
- [ ] Báo strict rate: số generation mà mọi câu đều đúng/tổng generation
  theo định nghĩa đã khóa.
- [ ] Báo riêng rate trên mọi yêu cầu end-to-end và rate có điều kiện trên
  output thành công; không nhầm hai mẫu số.
- [ ] Phân loại lỗi: đáp án mâu thuẫn, không có bằng chứng, câu mơ hồ, nhiều
  đáp án đúng, open-answer rubric không đủ, schema/API error.
- [ ] Đưa ví dụ lỗi và giải thích vì sao vi phạm rubric.
- [ ] Nếu quan sát 100% trên mẫu, báo khoảng tin cậy và nhấn mạnh điều đó
  không chứng minh lỗi không thể xảy ra ở ngoài mẫu.
- [ ] Không dùng “accuracy 100%” nếu chỉ là điểm trung bình cấp câu; nhãn
  strict pass phải tính ở cấp đề.

### 11.3. Phân tích RQ3

- [ ] Tính đúng hoàn toàn/tổng yêu cầu theo chỉ số end-to-end.
- [ ] Báo thêm tỷ lệ trên response thành công nếu hữu ích, kèm mẫu số.
- [ ] Phân tầng theo loại mục từ/ngữ cảnh nếu sample size cho phép.
- [ ] Phân loại lỗi: sai nghĩa ngữ cảnh, bỏ sót nghĩa, lemma/POS/inflection
  sai, hallucination, câu trả lời thiếu, không phản hồi.
- [ ] Phân biệt nguồn lỗi MyMemory với lỗi Tutor; bản dịch máy không mặc
  nhiên là gold standard.
- [ ] Chọn ví dụ thành công và thất bại có tính đại diện; che dữ liệu/quyền
  tác giả nếu cần.

### 11.4. Phân tích độ tin cậy và độ không chắc chắn

- [ ] Báo số người chấm, tỷ lệ bất đồng ban đầu và thống kê đồng thuận đã
  được duyệt.
- [ ] Báo cách hòa giải; lưu số liệu trước và sau hòa giải.
- [ ] Tính khoảng tin cậy bằng phương pháp phù hợp với cấu trúc lặp. Nếu
  nhiều lượt đến từ cùng bài, xem xét bootstrap/cluster theo bài với người
  hướng dẫn thay vì giả định mọi lượt độc lập.
- [ ] Thảo luận độ biến thiên model theo lần gọi.
- [ ] Nêu ảnh hưởng của số bài, chủ đề, độ dài, độ khó và lựa chọn từ vựng.
- [ ] Không tuyên bố tác động học tập hoặc thay thế kỳ thi YKI.

### 11.5. Các câu hỏi bắt buộc trong phần thảo luận

- Mục format nào hệ thống tuân thủ/không tuân thủ nhiều nhất, và có bằng
  chứng YKI nào hỗ trợ nhận định đó?
- Một đề có đáp án sai thường sai ở loại câu nào? Sai do prompt, nguồn bài,
  mơ hồ, answer key hay chấm câu mở?
- Strict 100% thấp hơn accuracy cấp câu bao nhiêu, và điều đó thay đổi cách
  diễn giải mức “đáng tin” ra sao?
- Tutor giải thích sai ở dạng từ/cấu trúc/ngữ cảnh nào? Có dấu hiệu mẫu thiên
  về từ dễ không?
- Lỗi API ảnh hưởng đến hiệu quả đầu-cuối như thế nào?
- Người đánh giá có bất đồng ở mục nào? Rubric có cần làm rõ không?
- Kết quả khác hoặc giống nghiên cứu trước ra sao; so sánh có thực sự cùng
  tác vụ, ngôn ngữ và tiêu chí không?
- Các giới hạn nào khiến không thể khái quát? Kết luận nào vẫn đứng vững
  trong phạm vi mẫu?
- Thay đổi nhỏ nhất nào của hệ thống có thể giảm lỗi? Chỉ đề xuất nếu có
  lỗi dữ liệu hỗ trợ; không kết luận nhân quả khi chưa kiểm nghiệm giải pháp.

## 12. Giai đoạn 7 — Hoàn thiện nội dung thesis

### Chương 1 — Giới thiệu

- [ ] Viết bối cảnh dựa trên tài liệu có trích dẫn, không dùng khẳng định
  chung không nguồn.
- [ ] Nêu vấn đề đúng trọng tâm: cần biết mức tuân thủ format, đáp án strict
  100%, và Tutor giải thích từ trong ngữ cảnh chính xác tới đâu.
- [ ] Nêu mục tiêu, RQ, phạm vi, thuật ngữ, giới hạn và đóng góp dự kiến.
- [ ] Không hứa đo learning outcome nếu không có nghiên cứu người học.

### Chương 2 — Phương pháp và tài liệu

- [ ] Mô tả research design, mẫu, nguồn bài, quy trình sinh, cấu hình và
  người đánh giá đủ để người khác lặp lại.
- [ ] Đưa rubric và công thức chỉ số vào nội dung/phụ lục.
- [ ] Mô tả ethics, bản quyền, dữ liệu gửi API, bảo vệ dữ liệu và xử lý lỗi.
- [ ] Giải thích chọn thống kê và đơn vị phân tích.

### Chương 3 — Phân tích hiện trạng

- [ ] Mô tả YKI từ nguồn chính thức, phân biệt format với CEFR.
- [ ] So sánh sản phẩm/tài nguyên cụ thể, trích nguồn và ngày truy cập.
- [ ] Chỉ ra gap từ literature review; tránh tuyên bố tính mới chưa chứng minh.
- [ ] Gắn từng yêu cầu hệ thống với RQ hoặc use case.

### Chương 4 — Cơ sở lý thuyết

- [ ] Giải thích đọc hiểu, assessment validity/reliability, CEFR, LLM, AIG,
  contextual vocabulary và automatic scoring.
- [ ] Trích dẫn các khẳng định khoa học; không chỉ chép định nghĩa.
- [ ] Liên kết lý thuyết với tiêu chí rubric và giới hạn hệ thống.

### Chương 5 — Giải pháp và triển khai

- [ ] Mô tả kiến trúc và sequence/data flow chính xác với code hiện tại.
- [ ] Trình bày prompt/version, model/API, validation và xử lý thất bại.
- [ ] Giải thích phần nào tự xây, phần nào là API/dịch vụ bên thứ ba.
- [ ] Không gọi ứng dụng là mô hình neural network do thesis phát triển.
- [ ] Thêm hình, caption, nguồn và dẫn chiếu trong văn bản.

### Chương 6 — Kết quả và thảo luận

- [ ] Trình bày kết quả kiểm thử software riêng với kết quả thực nghiệm.
- [ ] Điền bảng RQ1–RQ3 bằng số thật; mọi tỷ lệ có numerator/denominator.
- [ ] Phân tích lỗi, ví dụ, khoảng tin cậy và độ đồng thuận.
- [ ] Trả lời mỗi RQ một cách tường minh.
- [ ] Thảo luận cả kết quả âm/không mong đợi; tránh chọn lọc kết quả đẹp.
- [ ] Nêu điều không thể kết luận.

### Chương 7 — Kết luận

- [ ] Tóm tắt đóng góp triển khai và đóng góp đánh giá riêng.
- [ ] Trả lời RQ1–RQ3 bằng kết quả đã báo cáo ở Chương 6.
- [ ] Nêu hạn chế thực tế, hướng cải tiến dựa trên lỗi được quan sát.
- [ ] Không thêm kết quả mới ở phần kết luận.

## 13. Giai đoạn 8 — Kiểm tra chất lượng và nộp

### Khoa học và nội dung

- [ ] Mọi RQ có phương pháp và kết quả tương ứng.
- [ ] Mọi kết quả có mẫu số, nguồn, thời điểm và cách tính.
- [ ] Tất cả trích dẫn trong thân bài có trong danh mục tham khảo và ngược
  lại.
- [ ] Tài liệu tham khảo kiểm tra được; dùng chuẩn trích dẫn theo trường.
- [ ] Không còn câu “sẽ đo”, “dự kiến” hoặc placeholder trong bản cuối.
- [ ] Không còn `[CẦN BỔ SUNG]`, `[SAU KHI ĐO]`, `[ ]`, `[N]`, `[x]`.
- [ ] Đọc lại để bảo đảm không viết kết luận nhân quả hoặc khái quát quá mẫu.

### Kỹ thuật và tái lập

- [ ] Chạy toàn bộ test trên phiên bản cuối; điều tra mọi lỗi.
- [ ] Lưu lệnh chạy, môi trường, ngày, phiên bản code/dependencies.
- [ ] Xác minh sơ đồ kiến trúc và workflow trùng với implementation.
- [ ] Kiểm tra không có `.env`, API key, dữ liệu riêng tư hoặc dữ liệu không
  được phép đính kèm.
- [ ] Lưu dataset đánh giá và rating theo chính sách dữ liệu đã duyệt.

### Định dạng trường

- [ ] Chuyển nội dung sang Word template chính thức; README Markdown không
  thay thế thesis theo định dạng trường.
- [ ] Điền trang bìa, degree programme, supervisors, ngày nộp, số trang và
  phụ lục.
- [ ] Tạo/cập nhật mục lục, danh sách hình/bảng/từ viết tắt.
- [ ] Caption và đánh số hình/bảng; trong văn bản có dẫn chiếu từng hình.
- [ ] Kiểm tra line spacing, font, lề, tiêu đề, page breaks và citation style.
- [ ] Chạy kiểm tra accessibility và xuất PDF đúng hướng dẫn trường.
- [ ] Đọc PDF cuối cùng từng trang để kiểm tra lỗi ngắt dòng, hình, bảng,
  bookmark, hyperlink và trang trắng.

## 14. Rủi ro và phương án giảm thiểu

| Rủi ro | Tác động | Biện pháp |
|---|---|---|
| Không tìm được tiêu chí format YKI đủ cụ thể | RQ1 không có thước đo hợp lệ | Hỏi cơ quan/giảng viên; thu hẹp RQ1 thành compliance với tập tiêu chí công khai, nêu giới hạn |
| Cơ cấu câu hỏi hiện tại khác format thật | Điểm RQ1 thấp | Không che giấu; cân nhắc sửa generator trước khi khóa protocol hoặc đánh giá nguyên trạng |
| Không có người chấm tiếng Phần Lan | RQ2/RQ3 thiếu gold standard | Xin giảng viên giới thiệu người đủ năng lực; nếu không có, giảm phạm vi và công bố giới hạn |
| Dữ liệu bài báo có bản quyền | Không thể lưu/chia sẻ mẫu | Dùng nội dung có giấy phép phù hợp, quyền cho phép hoặc bài tự tạo/được phép; hỏi trường |
| API đổi model hoặc ngừng truy cập | Kết quả không lặp lại/thiếu mẫu | Chạy trong khung thời gian ngắn, ghi metadata, giữ output được phép, báo version và failure |
| Chi phí/rate limit | Không đủ lượt chạy | Pilot, dự trù chi phí và chốt cỡ mẫu trước; không giảm mẫu âm thầm |
| Đánh giá người chấm bất đồng | Tỷ lệ phụ thuộc người chấm | Calibration, rubric cụ thể, lưu độc lập và báo cáo agreement |
| LLM sinh không ổn định | Kết quả phụ thuộc lần gọi | Nhiều lượt trên mỗi bài theo protocol; phân tích theo bài và generation |
| Cỡ mẫu nhỏ | CI rộng, khái quát yếu | Nêu exploratory/pilot, tránh khẳng định tổng quát; xin duyệt cỡ mẫu |
| Nội dung gửi API chứa dữ liệu hạn chế | Vi phạm quyền riêng tư/điều khoản | Chỉ dùng dữ liệu được phép, ẩn danh và được ethics duyệt |

## 15. Hồ sơ/artefact cần có khi kết thúc

- [ ] Bản thesis Word/PDF theo template trường.
- [ ] Protocol nghiên cứu và phiên bản rubric đã khóa.
- [ ] Danh mục nguồn YKI và literature review đã xác minh.
- [ ] Dataset manifest, data dictionary và nhật ký chạy API (theo quyền lưu).
- [ ] Raw ratings độc lập, resolved ratings và hướng dẫn chấm.
- [ ] Script/notebook hoặc bảng tính có thể tái tạo các chỉ số và hình.
- [ ] Báo cáo test phiên bản cuối.
- [ ] Phụ lục câu hỏi, tiêu chí, ví dụ và tài liệu ethics cần thiết.
- [ ] Bản sao lưu dữ liệu nghiên cứu theo chính sách trường.

## 16. Mẫu ghi tiến độ hàng tuần

| Tuần/ngày | Việc đã làm | Artefact tạo ra | Bằng chứng/đường dẫn | Vấn đề | Việc kế tiếp | Cần ai duyệt |
|---|---|---|---|---|---|---|
| [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |

### Nhật ký quyết định

| Ngày | Quyết định | Lý do/bằng chứng | Người duyệt | Ảnh hưởng đến protocol/thesis |
|---|---|---|---|---|
| [ ] | [ ] | [ ] | [ ] | [ ] |
