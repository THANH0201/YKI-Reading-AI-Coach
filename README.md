# Phát triển và đánh giá nền tảng luyện đọc hiểu YKI tích hợp mô hình ngôn ngữ lớn

> **Bản thảo học thuật dựa trên hiện trạng mã nguồn.** Tài liệu này được viết
> theo bố cục thesis mẫu người dùng cung cấp, không phải bản thesis đã được
> định dạng hoặc phê duyệt bởi trường. Các vị trí ghi **[CẦN BỔ SUNG]** yêu
> cầu thông tin, tài liệu tham khảo hoặc kết quả nghiên cứu thực tế. Không
> được xem các nội dung này là kết quả đã xác nhận.

## Trang bìa

**Tác giả:** [CẦN BỔ SUNG: họ tên]  
**Tên đề tài:** Phát triển và đánh giá nền tảng luyện đọc hiểu YKI tích hợp
mô hình ngôn ngữ lớn  
**Trường:** [CẦN BỔ SUNG]  
**Chương trình đào tạo:** [CẦN BỔ SUNG]  
**Bậc đào tạo:** [CẦN BỔ SUNG]  
**Giảng viên hướng dẫn:** [CẦN BỔ SUNG]  
**Ngày nộp:** [CẦN BỔ SUNG]

## Tóm tắt

Đề tài trình bày quá trình thiết kế và xây dựng YKI Reading AI Coach, một
nguyên mẫu ứng dụng hỗ trợ luyện đọc tiếng Phần Lan theo định hướng kỳ thi
YKI. Hệ thống cho phép người học nhập bài báo, sử dụng mô hình ngôn ngữ lớn
để ước lượng trình độ CEFR, phân loại chủ đề, tạo câu hỏi đọc hiểu và trao
đổi với AI Tutor. Bài mẫu đã duyệt quyền sử dụng, câu hỏi, kết quả đề mẫu và
dữ liệu từ vựng được lưu trong SQLite; bài người dùng nhập chỉ được xử lý
trong phiên và không được ghi vào kho đề mẫu.

Ứng dụng được triển khai bằng Python và Streamlit. Các yêu cầu AI được gửi
đến model `qwen/qwen3.8-27b` thông qua Groq; Tutor sử dụng LangChain để điều
phối model và các công cụ tìm kiếm nội dung bài đọc, tra từ vựng. Đề luyện
được quy định gồm năm câu hỏi: hai câu trắc nghiệm, hai câu đúng/sai và một
câu trả lời mở. Hệ thống kiểm tra cấu trúc dữ liệu do model trả về trước khi
lưu đề.

Đóng góp nghiên cứu dự kiến của thesis là đánh giá có hệ thống ba khía cạnh
của sản phẩm: mức độ câu hỏi gần với định dạng YKI thực tế, tỷ lệ đề có toàn
bộ đáp án chính xác 100%, và tỷ lệ giải thích từ vựng của Tutor chính xác
trong ngữ cảnh bài đọc. Các tỷ lệ này chưa được đo; cần tập bài đọc, tiêu chí
đối chiếu và đánh giá chuyên môn trước khi có thể báo cáo kết quả.

Đóng góp kỹ thuật hiện có là nguyên mẫu tích hợp các API với luồng luyện đọc,
kiểm tra cấu trúc đầu ra và lưu dữ liệu. Dự án không huấn luyện mô hình học
máy riêng. Vì vậy, luận điểm học thuật cần dựa trên thiết kế đánh giá và
bằng chứng thu được, không dựa riêng vào việc sử dụng AI hoặc xây dựng giao
diện.

**Từ khóa:** YKI, đọc hiểu tiếng Phần Lan, CEFR, mô hình ngôn ngữ lớn, tạo câu
hỏi tự động, AI Tutor.

## Abstract

YKI Reading AI Coach is a prototype application designed to support Finnish
reading practice in the context of the YKI examination. It allows learners
to submit an article, request CEFR-level estimation and topic classification,
generate reading-comprehension questions, complete a timed exercise, and ask
an AI tutor questions about the article or vocabulary. Approved example
articles, their questions, exam results, and vocabulary data are stored in
SQLite. User-submitted text and its practice results remain in the active app
session and are not added to the example-exam library.

The application is implemented in Python using Streamlit. AI functionality
uses the `qwen/qwen3.8-27b` model through Groq. The tutor uses LangChain to
coordinate the model with tools for searching the current article and
translating Finnish vocabulary. Generated exams follow a fixed structure of
two multiple-choice questions, two true/false questions, and one open-ended
question. The application validates the generated question schema before
persisting it.

The proposed research contribution is a systematic evaluation of three
quality dimensions: how closely generated questions follow the authentic YKI
reading format, the percentage of generated exams whose answer keys are
entirely correct (a strict 100% criterion), and the percentage of vocabulary
explanations that correctly reflect meaning in the article context. These
rates have not yet been measured and require a defined dataset, reference
criteria, and expert review.

The existing technical contribution is a prototype integrating APIs into a
reading-practice workflow, validating structured output, and persisting data.
The project does not train a separate machine-learning model. Its academic
argument must therefore be based on a rigorous evaluation design and
evidence, not on API usage or interface development alone.

**Keywords:** YKI, Finnish reading comprehension, CEFR, large language
models, automatic question generation, AI tutor.

## Danh mục từ viết tắt

| Từ viết tắt | Ý nghĩa |
|---|---|
| AI | Trí tuệ nhân tạo (Artificial Intelligence) |
| API | Giao diện lập trình ứng dụng (Application Programming Interface) |
| CEFR | Khung tham chiếu trình độ ngôn ngữ chung châu Âu |
| LLM | Mô hình ngôn ngữ lớn (Large Language Model) |
| NLP | Xử lý ngôn ngữ tự nhiên (Natural Language Processing) |
| YKI | Kỳ thi Chứng chỉ năng lực ngôn ngữ quốc gia của Phần Lan |

## Mục lục

Khi chuyển bản thảo này sang Word theo mẫu của trường, hãy tạo mục lục tự
động từ các kiểu tiêu đề và cập nhật số trang sau khi hoàn thiện nội dung.

1. Giới thiệu  
2. Phương pháp và tài liệu  
3. Phân tích hiện trạng  
4. Cơ sở lý thuyết  
5. Giải pháp đề xuất và triển khai  
6. Kết quả và đánh giá  
7. Kết luận  
Tài liệu tham khảo  
Phụ lục A. Phiếu chấm  
Phụ lục B. Việc cần hoàn thành  
Phụ lục C. Cài đặt và chạy  
Phụ lục D. Kiểm thử  
Phụ lục E. Cấu trúc mã nguồn

# 1. Giới thiệu

## 1.1. Bối cảnh

Đọc hiểu là một kỹ năng quan trọng trong việc sử dụng ngôn ngữ thứ hai. Người
học cần xử lý từ vựng, cấu trúc câu, thông tin tường minh và hàm ý trong các
loại văn bản khác nhau. Trong quá trình chuẩn bị cho một kỳ thi ngôn ngữ, việc
luyện tập thường xuyên với văn bản phù hợp trình độ và nhận phản hồi kịp thời
có thể hỗ trợ người học nhận biết điểm cần cải thiện (Bachman & Palmer, 1996).

Các công cụ tạo sinh dựa trên mô hình ngôn ngữ lớn mở ra khả năng tạo câu hỏi
và giải thích theo nội dung văn bản. Tuy vậy, đầu ra của mô hình có thể sai
hoặc không được văn bản hỗ trợ. Vì thế, một hệ thống học tập cần kiểm tra
định dạng đầu ra, làm rõ giới hạn của việc chấm tự động và đánh giá chất
lượng học liệu trước khi kết luận về tính hữu ích giáo dục.

## 1.2. Phát biểu vấn đề

Người học có thể gặp khó khăn khi tự tìm bài đọc phù hợp, tạo câu hỏi gắn với
nội dung và tự đánh giá câu trả lời. Một quy trình dựa trên AI có thể giảm
công sức chuẩn bị học liệu, nhưng kéo theo các câu hỏi về mức độ gần với
định dạng YKI của đề được tạo, tính chính xác của đáp án, và khả năng Tutor
giải thích đúng nghĩa từ trong ngữ cảnh bài đọc.

Dự án giải quyết trước hết bài toán triển khai một nguyên mẫu có thể kết nối
các bước đó trong một ứng dụng. Việc nguyên mẫu hoạt động không tự chứng minh
rằng đánh giá trình độ chính xác, câu hỏi có chất lượng sư phạm hoặc người
học tiến bộ. Các khía cạnh này cần được kiểm chứng bằng dữ liệu và đánh giá
có phương pháp.

## 1.3. Mục tiêu

Mục tiêu kỹ thuật hiện tại là:

1. Xây dựng ứng dụng web để nhập bài báo tiếng Phần Lan.
2. Tích hợp model để ước lượng trình độ CEFR, phân loại chủ đề và tạo câu
   hỏi đọc hiểu.
3. Xây dựng luồng làm bài có thời hạn, nộp bài, tính điểm và lưu kết quả.
4. Tích hợp AI Tutor có khả năng tìm kiếm trong bài đọc và hỗ trợ từ vựng.
5. Kiểm tra cấu trúc câu hỏi do model tạo trước khi lưu vào cơ sở dữ liệu.

Mục tiêu nghiên cứu là đo lường ba yêu cầu chất lượng do người phát triển đề
ra: (1) mức độ tuân thủ định dạng bài đọc YKI thực tế, (2) độ chính xác của
đáp án, với một đề chỉ đạt nếu mọi đáp án đều chính xác, và (3) độ chính xác
của giải thích nghĩa từ vựng theo ngữ cảnh bài đọc. Tiêu chí cần được đối
chiếu với tài liệu YKI chính thức và duyệt cùng giảng viên hướng dẫn trước
khi thu thập kết quả.

## 1.4. Câu hỏi nghiên cứu

Ba câu hỏi nghiên cứu được xác định theo mục tiêu của dự án. Đây là câu hỏi
đo lường; hiện chưa có kết quả để trả lời:

- **RQ1:** Các câu hỏi do hệ thống tạo tuân thủ định dạng phần đọc YKI thực
  tế ở mức bao nhiêu phần trăm, khi được đối chiếu với tài liệu hoặc mẫu đề
  YKI chính thức theo một rubric xác định trước?
- **RQ2:** Bao nhiêu phần trăm đề được tạo có **tất cả đáp án chính xác
  100%** và được hỗ trợ bởi nội dung bài đọc?
- **RQ3:** Bao nhiêu phần trăm yêu cầu giải thích từ vựng của AI Tutor nhận
  được lời giải thích **đúng hoàn toàn theo ngữ cảnh bài đọc**, theo đánh
  giá của người có chuyên môn?

Trong RQ2, một đề có dù chỉ một đáp án sai được tính là không đạt tiêu chí
“đề hoàn toàn chính xác”; tỷ lệ đúng theo từng đáp án chỉ được dùng làm số
liệu chẩn đoán bổ sung. RQ3 cũng cần định nghĩa trước các lỗi nghiêm trọng,
ví dụ giải thích nghĩa trái với ngữ cảnh hoặc khẳng định sai về cách dùng
từ. Định nghĩa cuối cùng phải được thống nhất với người hướng dẫn và người
chấm.

## 1.5. Phạm vi

Phiên bản hiện tại xử lý một bài đọc trong một lượt học. Model có thể trả về
các mức A2, B1, B2 hoặc C1; dịch vụ tạo bài chỉ tiếp tục với B1, B2 hoặc C1.
Mỗi đề có đúng năm câu: hai câu trắc nghiệm, hai câu đúng/sai và một câu trả
lời mở. Thời lượng làm bài được đặt là 30 phút. Phần nghiên cứu tập trung
đánh giá định dạng đề, độ chính xác đáp án và lời giải thích từ vựng trong
ngữ cảnh; không đánh giá hiệu quả học tập dài hạn hay huấn luyện model riêng.

Hệ thống chưa có tài khoản người dùng, quản lý lớp học, đồng bộ dữ liệu từ
nhiều thiết bị, ngân hàng câu hỏi được giáo viên duyệt hoặc chứng nhận kết
quả theo tiêu chuẩn chính thức. Câu trả lời mở được chấm bằng so khớp từ
khóa, không phải mô hình đánh giá ngữ nghĩa đã được kiểm chứng. Ứng dụng
không thay thế bài thi YKI chính thức hay đánh giá của giáo viên.

## 1.6. Cấu trúc thesis

Chương 1 giới thiệu bối cảnh, vấn đề, mục tiêu, câu hỏi nghiên cứu và phạm
vi. Chương 2 mô tả phương pháp, dữ liệu và quy trình đánh giá. Chương 3 phân
tích kỳ thi YKI, các tài nguyên liên quan và yêu cầu hệ thống. Chương 4 trình
bày cơ sở lý thuyết. Chương 5 mô tả giải pháp và việc triển khai. Chương 6
trình bày kết quả kiểm thử phần mềm và kết quả thực nghiệm nếu nghiên cứu
được thực hiện. Chương 7 tổng kết, trả lời câu hỏi nghiên cứu dựa trên bằng
chứng, nêu hạn chế và hướng phát triển.

# 2. Phương pháp và tài liệu

## 2.1. Phương pháp nghiên cứu

Phần phát triển phần mềm có thể được mô tả theo hướng **Design Science
Research**: xác định vấn đề, thiết kế và xây dựng hiện vật phần mềm, kiểm tra
hiện vật theo yêu cầu, rồi đánh giá trong bối cảnh sử dụng (Hevner et al.,
2004). Bản thân quá trình xây dựng ứng dụng là hoạt động kỹ thuật; để thành
đóng góp nghiên cứu, thesis cần nêu rõ câu hỏi, quy trình thu thập bằng
chứng, tiêu chí đánh giá và giới hạn kết luận.

Nghiên cứu này dùng đánh giá định lượng có giám sát chuyên gia đối với ba
đầu ra AI. Đơn vị thử nghiệm cần được phân biệt: bài đọc là nguồn nội dung,
lượt sinh đề là đơn vị phân tích RQ1/RQ2, và yêu cầu giải thích một mục từ
trong một câu cụ thể là đơn vị phân tích RQ3. Do đầu ra LLM có tính biến
động, một lần sinh trên mỗi bài không đủ để mô tả độ ổn định; số lần lặp
phải được ấn định trước và báo cáo.

Kết quả số được bổ sung bằng phân tích lỗi định tính. Mỗi lỗi cần có ví dụ
đã ẩn thông tin có bản quyền nếu cần, loại lỗi, tiêu chí vi phạm và tác động
đến người học. Phân tích ví dụ không thay thế mẫu số và chỉ số định lượng.

## 2.2. Nguồn dữ liệu

Trong mã nguồn, bài đọc được người dùng nhập vào chỉ dùng trong phiên; đề mẫu
được lấy riêng từ bài đã duyệt quyền sử dụng và lưu trong SQLite. Bộ kiểm thử
dùng dữ liệu giả lập và phản hồi AI mô phỏng; đây không phải tập dữ liệu
nghiên cứu được gán nhãn.

Để trả lời RQ1 và RQ2, cần xây dựng hoặc chọn một tập bài đọc có quyền sử
dụng rõ ràng, cùng tài liệu tham chiếu chính thức cho format YKI. Để kiểm
tra độ chính xác đáp án, mỗi câu cần được đối chiếu với bài và đáp án chuẩn
do người đánh giá xác nhận. Để trả lời RQ3, tập đánh giá cần có các từ/cụm
từ trong câu nguồn và nghĩa tham chiếu theo ngữ cảnh. Cần ghi nguồn, độ dài,
chủ đề và nhãn trình độ nếu có; kiểm tra giấy phép và quyền lưu trữ trước
khi đưa toàn văn bài báo vào phụ lục hoặc dữ liệu nghiên cứu.

**[CẦN BỔ SUNG]** Mô tả tập dữ liệu thực tế: số lượng bài, nguồn, khoảng thời
gian thu thập, tiêu chí đưa vào/loại trừ, cách gán nhãn và sự đồng thuận của
người đánh giá. Không điền số liệu ước đoán.

## 2.3. Quy trình thu thập dữ liệu

Quy trình đánh giá đề xuất:

1. Chọn bài đọc tiếng Phần Lan có quyền sử dụng và tiêu chí chọn mẫu được
   công bố trước.
2. Đối chiếu với tài liệu hoặc đề mẫu YKI chính thức; chuyển các đặc điểm
   định dạng cần thiết thành checklist có tiêu chí quan sát được.
3. Chạy mỗi bài qua cùng phiên bản ứng dụng, model, prompt và cấu hình; lưu
   mọi lần sinh, kể cả phản hồi lỗi hoặc không hợp lệ.
4. Lưu câu hỏi, đáp án, giải thích và danh sách từ vựng cần được Tutor giải
   thích trong đúng ngữ cảnh của bài.
5. Người đánh giá độc lập chấm mức phù hợp định dạng và kiểm tra đáp án bằng
   cách đối chiếu từng câu với bài đọc.
6. Đưa truy vấn từ vựng cùng câu chứa từ cho Tutor; người đánh giá kiểm tra
   xem lời giải thích có truyền đạt chính xác nghĩa trong ngữ cảnh không.
7. Ghi nhận bất đồng, xử lý theo quy trình thống nhất trước, rồi tính các tỷ
   lệ theo mẫu số đã định nghĩa.

Đơn vị lấy mẫu cần là **lượt sinh đề**, không chỉ bài đọc: một bài có thể
được chạy nhiều lần vì đầu ra LLM có thể thay đổi. Số bài, số lần sinh trên
mỗi bài và số truy vấn từ vựng phải được xác định trước cùng giảng viên hướng
dẫn. Báo cáo prompt, model ID, thời điểm truy cập, cài đặt liên quan và lỗi
dịch vụ để kết quả có thể diễn giải và lặp lại.

**[CẦN BỔ SUNG]** Kích thước mẫu, số người đánh giá, nguồn bài, cách giải
quyết bất đồng, thời gian thu thập và yêu cầu đạo đức/quyền sử dụng dữ liệu.

## 2.4. Công cụ phát triển

| Công cụ | Vai trò trong dự án |
|---|---|
| Python | Ngôn ngữ lập trình chính. |
| Streamlit | Giao diện web tương tác. |
| SQLite | Lưu bài mẫu đã duyệt quyền, câu hỏi mẫu, kết quả đề mẫu và dữ liệu từ vựng. |
| Groq API | Cung cấp truy cập model `qwen/qwen3.8-27b`. |
| OpenAI Python SDK | Gửi yêu cầu chat theo giao diện tương thích OpenAI tới Groq. |
| LangChain và `langchain-groq` | Điều phối AI Tutor và các công cụ được phép sử dụng. |
| pytest | Kiểm thử tự động. |

## 2.5. Phương pháp đánh giá

Đánh giá được tổ chức theo ba câu hỏi nghiên cứu. Tất cả các checklist,
rubric, mẫu tham chiếu và cách tính cần được thống nhất trước khi xem kết
quả, để tránh điều chỉnh tiêu chí theo đầu ra đã quan sát.

### 2.5.1. Kiểm thử phần mềm

Kiểm thử đơn vị và kiểm thử giao diện xác nhận một số hành vi như kiểm tra
dữ liệu đầu vào, xác thực cấu trúc câu hỏi, chấm điểm, lưu dữ liệu, xử lý
thời gian và hiển thị kết quả. Các kiểm thử mô phỏng phản hồi AI, do đó
không đo chất lượng thực tế của model.

### 2.5.2. RQ1 – Mức độ tuân thủ định dạng YKI

Không dùng cảm nhận chung về việc đề “trông giống YKI”. Trước tiên, trích
xuất các yêu cầu có thể quan sát từ tài liệu và đề mẫu chính thức đang còn
hiệu lực. Checklist có thể gồm dạng tác vụ, cách trình bày hướng dẫn, loại
phản hồi được yêu cầu, cấu trúc lựa chọn nếu tài liệu tham chiếu quy định,
và các đặc điểm khác thực sự được nguồn chính thức xác nhận. Không đưa các
quy ước nội bộ của ứng dụng vào checklist YKI nếu chúng không có trong
nguồn.

Với mỗi lượt sinh, người đánh giá đánh dấu từng mục áp dụng là đạt hoặc
không đạt. Trước khi chấm, cần lập bảng ánh xạ mỗi yêu cầu trong nguồn YKI
đến một mục checklist; lưu nguồn, trang/mục, ngày truy cập và lý do mục đó
được xem là áp dụng. Nếu một yêu cầu chính thức không thể ánh xạ vào đầu ra
của ứng dụng, đánh dấu không đạt hoặc không tương ứng theo quy tắc đã duyệt,
không tự bỏ mục đó khỏi checklist.

Tỷ lệ tuân thủ theo tiêu chí được tính như sau:

`Tỷ lệ tuân thủ (%) = số mục checklist đạt / tổng số mục checklist áp dụng x 100`

Báo cáo cả (a) điểm tuân thủ theo từng lượt sinh, (b) điểm trung bình trên
các lượt sinh và (c) tỷ lệ đề đạt toàn bộ tiêu chí bắt buộc. Đề chỉ được gọi
là **tuân thủ đầy đủ** khi tất cả mục bắt buộc đều đạt. Đầu ra lỗi hoặc
không sinh được đề phải được giữ trong mẫu số toàn quy trình và tính là
không đạt ở mức đề; đồng thời báo cáo riêng lỗi dịch vụ. Đây là mức độ tuân
thủ checklist đã trích từ tài liệu, không chứng minh đề tương đương về độ
khó, độ tin cậy hoặc giá trị đo lường với bài thi chính thức.

### 2.5.3. RQ2 – Tỷ lệ đề có toàn bộ đáp án đúng

Trước khi xem đáp án do hệ thống tạo, người đánh giá lập đáp án tham chiếu
từ bài đọc cho mỗi câu. Với trắc nghiệm và đúng/sai, xác định đáp án và đoạn
bằng chứng hỗ trợ. Với câu mở, viết các ý bắt buộc và các cách diễn đạt
tương đương có thể chấp nhận; không xem danh sách từ khóa tự sinh là chuẩn
đúng độc lập. Người chấm sau đó so đáp án của hệ thống với đáp án tham chiếu
và kiểm tra xem câu hỏi có một đáp án xác định được hay không.

`Độ chính xác từng đáp án (%) = số đáp án được xác nhận đúng / tổng số đáp án được đánh giá x 100`

Chỉ số chính theo yêu cầu nghiêm ngặt là:

`Tỷ lệ đề đạt 100% (%) = số lượt sinh mà mọi đáp án đều đúng / tổng số lượt sinh được yêu cầu x 100`

Một lượt sinh có một đáp án sai, câu mơ hồ không có đáp án duy nhất, đáp án
không thể xác minh hoặc đầu ra không hợp lệ **không đạt** tiêu chí đề đúng
100%. Tỷ lệ theo từng câu được báo cáo chỉ để chẩn đoán loại câu/lỗi, không
thay thế chỉ số chính. Lỗi API cũng được báo riêng; khi báo cáo chất lượng
đầu-cuối trên mọi yêu cầu, lượt API lỗi được tính là không tạo được đề, không
được lặng lẽ loại khỏi mẫu số. Có thể báo thêm tỷ lệ chính xác có điều kiện
trên các đề đã sinh thành công nhưng phải ghi rõ mẫu số khác nhau.

### 2.5.4. RQ3 – Độ chính xác nghĩa từ vựng theo ngữ cảnh

Chọn từ hoặc cụm từ xuất hiện trong bài, lưu câu chứa từ, và yêu cầu người
đánh giá xác định nghĩa tham chiếu trong ngữ cảnh trước khi xem câu trả lời
của Tutor. Sau đó đưa cùng truy vấn và ngữ cảnh cho Tutor. Mẫu cần bao gồm
các loại từ/cụm từ và trường hợp đa nghĩa, biến tố hoặc thành ngữ nếu các
trường hợp đó thuộc phạm vi. Tỷ lệ phải được báo cáo chung và phân tầng
theo loại mục để dễ nhận biết điểm yếu.

Để so sánh công bằng, dùng một mẫu câu hỏi giống nhau cho từng mục, ví dụ:
“Trong câu sau, từ/cụm từ **[X]** có nghĩa gì trong ngữ cảnh? Giải thích
ngắn gọn bằng tiếng Việt: **[câu nguồn]**”. Không thay đổi mức gợi ý theo
từng từ sau khi xem phản hồi. Nếu muốn đo Tutor trong cách dùng tự nhiên,
thiết kế một đợt đánh giá riêng và không gộp hai chế độ prompt.

`Tỷ lệ giải thích đúng hoàn toàn (%) = số giải thích được người đánh giá xác nhận đúng ngữ cảnh / tổng số yêu cầu giải thích đã gửi x 100`

Một giải thích chỉ đạt nếu nghĩa trọng tâm đúng trong câu nguồn và không
chứa khẳng định sai làm thay đổi cách hiểu. Trả lời không có nội dung, từ
chối nhầm hoặc không phản hồi được tính là lỗi trong chỉ số đầu-cuối; báo
cáo thêm độ chính xác có điều kiện trên các câu trả lời được tạo thành công.
Có thể chấm riêng lemma/ngữ pháp nếu Tutor nêu các thông tin này, nhưng
không gộp vào chỉ số nghĩa theo ngữ cảnh nếu chưa có rubric tương ứng.

### 2.5.5. Độ tin cậy của đánh giá

Ít nhất hai người đánh giá có năng lực tiếng Phần Lan phù hợp nên chấm độc
lập nếu điều kiện cho phép. Cần huấn luyện bằng rubric, ghi kết quả riêng
trước khi hòa giải bất đồng, và báo cáo chỉ số đồng thuận phù hợp với loại
dữ liệu. Lưu cả điểm từng người chấm trước và sau hòa giải; không chỉ lưu
điểm cuối. Có thể báo tỷ lệ thô đồng thuận cùng chỉ số hiệu chỉnh cơ hội
phù hợp do người hướng dẫn thống nhất. Giảng viên hướng dẫn cần duyệt trình
độ người đánh giá và phương pháp thống kê. Các tỷ lệ trên là tiêu chí đo
lường đề xuất; hiện chưa có điểm số thực nghiệm cho bất kỳ tỷ lệ nào.

Để thể hiện độ không chắc chắn, báo cáo tử số/mẫu số và khoảng tin cậy cho
các tỷ lệ. Vì nhiều lượt sinh có thể cùng một bài đọc, chúng không nhất
thiết độc lập; không xem từng câu/lượt sinh là quan sát độc lập nếu chúng
được nhóm theo cùng bài. Chọn phương pháp khoảng tin cậy và đơn vị lấy mẫu
cùng giảng viên hướng dẫn, chẳng hạn bootstrap theo bài đọc khi cỡ mẫu cho
phép. Không tuyên bố một số lượt nhỏ đại diện cho mọi bài YKI.

## 2.6. Hạn chế phương pháp và giá trị nghiên cứu

- **Giá trị cấu trúc (construct validity):** checklist format đo những tiêu
  chí nào? Không được gọi điểm checklist là “độ giống YKI tổng thể” nếu
  chưa chứng minh checklist đại diện đầy đủ cho format.
- **Giá trị tiêu chuẩn (criterion validity):** đáp án tham chiếu có được lập
  độc lập từ bài và xác nhận trước khi xem output model không? Nếu chỉ dùng
  đáp án do chính model sinh làm chuẩn, phép đo sẽ thiên lệch.
- **Độ tin cậy (reliability):** người chấm có hiểu rubric giống nhau không?
  Lưu chấm độc lập trước khi thảo luận và báo cáo bất đồng.
- **Giá trị nội tại:** các lần gọi có dùng cùng model ID, prompt và cài đặt
  hay kết quả thay đổi đồng thời do nhiều yếu tố?
- **Khả năng khái quát (external validity):** mẫu bài, độ dài, chủ đề, độ
  khó và nhóm từ có đủ đa dạng để đại diện cho bài người học sẽ nhập không?
- **Tính lặp lại:** lưu ngày gọi API, model ID hiển thị, prompt, input ID,
  output nguyên bản, lỗi và mã phiên bản ứng dụng. API bên ngoài có thể
  thay đổi mà không có thay đổi trong repository.

**[CẦN HOÀN THÀNH]** Ghi các quyết định cụ thể đã được thống nhất và giải
thích ảnh hưởng còn lại. Không chỉ liệt kê các thuật ngữ trên mà không liên
hệ với thiết kế thực tế.

# 3. Phân tích hiện trạng

## 3.1. Kỳ thi YKI

YKI là hệ thống chứng chỉ năng lực ngôn ngữ quốc gia của Phần Lan. Đề tài
chỉ tập trung vào hoạt động luyện đọc theo định hướng YKI; bài thi do ứng
dụng tạo không phải đề thi chính thức. Mô tả chi tiết cấu trúc, mức độ và
tiêu chí của kỳ thi trong bản nộp cuối cần được trích dẫn từ tài liệu hiện
hành của cơ quan tổ chức và đối chiếu với yêu cầu cụ thể của chương trình
đào tạo.

**[CẦN BỔ SUNG NGUỒN]** Trích dẫn tài liệu chính thức về YKI và mô tả phần
đọc, thang trình độ hoặc tiêu chí liên quan. Không suy luận cấu trúc thi
chính thức từ cơ cấu câu hỏi của ứng dụng.

### Việc cần thực hiện cho phần phân tích YKI

1. Tìm mô tả YKI hiện hành từ cơ quan chịu trách nhiệm, cùng các tài liệu
   hoặc đề mẫu được phép sử dụng.
2. Trích nguyên ý nhưng diễn đạt lại bằng lời của người viết; ghi trang/mục,
   năm/phiên bản và ngày truy cập.
3. Xác định phần nào là yêu cầu chính thức (ví dụ tác vụ đọc, cách hướng dẫn,
   cách phản hồi) và phần nào chỉ là lựa chọn thiết kế của ứng dụng.
4. Xin giảng viên xác nhận checklist RQ1 trước khi chấm bất kỳ đầu ra nào.

**Phân tích quan trọng:** cơ cấu đề của ứng dụng không tự chứng minh là cấu
trúc bài đọc YKI chính thức. Nếu format chính thức dùng tác vụ khác, cần báo
cáo mức không tương ứng trung thực; không thay đổi định nghĩa YKI để khớp
với sản phẩm.

## 3.2. Tài nguyên học tập hiện có

Người học có thể sử dụng bài báo, tài liệu luyện tập, từ điển, giáo viên và
các ứng dụng ngôn ngữ. Những công cụ này có thể giải quyết từng nhu cầu riêng
như đọc văn bản, tra từ hoặc luyện câu hỏi. Đề tài hướng tới một quy trình
tích hợp để người học có thể nhập một bài và tiếp tục luyện tập trong cùng
một giao diện.

Phần này hiện mới nêu bối cảnh chung. Một phân tích học thuật cần khảo sát
các tài nguyên cụ thể, xác định tiêu chí so sánh, ghi ngày truy cập và trích
dẫn nguồn thay vì khẳng định hệ thống mới tốt hơn các sản phẩm khác.

**[CẦN BỔ SUNG]** Bảng so sánh tài nguyên hiện có theo các tiêu chí: hỗ trợ
tiếng Phần Lan, phân loại trình độ, tạo câu hỏi từ bài đọc, chấm tự động,
giải thích theo ngữ cảnh và lưu tiến độ.

| Tài nguyên / sản phẩm | Nguồn tham khảo | Nhập bài đọc cá nhân | Tạo câu hỏi từ bài | Đối chiếu đáp án theo nguồn | Giải nghĩa theo ngữ cảnh |
|---|---|---|---|---|---|
| [CẦN BỔ SUNG: tài nguyên 1] | [URL, ngày truy cập] | [Có/không/chưa rõ] | [Có/không/chưa rõ] | [Có/không/chưa rõ] | [Có/không/chưa rõ] |
| [CẦN BỔ SUNG: tài nguyên 2] | [URL, ngày truy cập] | [Có/không/chưa rõ] | [Có/không/chưa rõ] | [Có/không/chưa rõ] | [Có/không/chưa rõ] |
| YKI Reading AI Coach | Mã nguồn đề tài | Có | Có, qua API LLM | Có phần chấm tự động; độ tin cậy chưa đo | Có AI Tutor; độ chính xác chưa đo |

Không suy ra thiếu tính năng chỉ vì trang web không đề cập. Dùng “chưa xác
minh” khi không có bằng chứng công khai, và lưu ngày khảo sát vì tính năng
sản phẩm có thể thay đổi.

## 3.3. Hạn chế của giải pháp hiện có và khoảng trống

Để xác định khoảng trống nghiên cứu, cần chứng minh qua tổng quan tài liệu
và khảo sát giải pháp, không chỉ dựa trên quan sát của người phát triển. Một
khoảng trống khả thi cần kiểm tra là cách đánh giá có hệ thống chất lượng,
tính bám sát văn bản và mức phù hợp CEFR của câu hỏi tiếng Phần Lan do LLM
tạo.

Đóng góp của dự án hiện tại không phải là phát minh một mô hình phân loại
mới. Mã nguồn sử dụng dịch vụ model có sẵn; do đó, không nên mô tả hệ thống
là “neural network-based classifier” hoặc tuyên bố đã huấn luyện mạng nơ-ron.

## 3.4. Phân tích yêu cầu

### 3.4.1. Yêu cầu chức năng

| Mã | Yêu cầu |
|---|---|
| FR1 | Nhập tiêu đề, nguồn và nội dung bài đọc. |
| FR2 | Ước lượng CEFR và phân loại chủ đề của bài đọc. |
| FR3 | Tạo đề luyện cá nhân theo cơ cấu hiện tại; kho đề mẫu ghép 4 bài và 18 câu theo nhóm nội dung. |
| FR4 | Kiểm tra kiểu dữ liệu, số lượng, lựa chọn và đáp án trước khi dùng câu hỏi trong phiên hoặc lưu cho bài mẫu đã duyệt. |
| FR5 | Làm bài trong 30 phút, nộp thủ công hoặc nộp tự động khi hết giờ. |
| FR6 | Chấm bài, hiển thị đối chiếu, lưu kết quả và câu trả lời. |
| FR7 | Tải bài mẫu ngẫu nhiên chỉ từ thư viện bài đã duyệt quyền sử dụng. |
| FR8 | Hỏi AI Tutor về ngôn ngữ hoặc bài đọc đang học. |
| FR9 | Tra từ vựng Finnish-English và cache bản dịch thành công. |
| FR10 | Thu thập bài RSS/Atom được cấp quyền vào bốn kho, tối đa 10 bài mỗi kho; tạo câu hỏi và đáp án mẫu để dùng lại. |

### 3.4.2. Yêu cầu phi chức năng

- Giao diện tương tác qua trình duyệt.
- Lưu dữ liệu cục bộ bằng SQLite.
- Cấu hình khóa API bên ngoài mã nguồn.
- Kiểm tra đầu ra AI có cấu trúc trước khi lưu.
- Có thể kiểm thử nghiệp vụ bằng model giả lập và cơ sở dữ liệu tạm.
- Thông báo rõ giới hạn của điểm tự động và câu trả lời AI.

# 4. Cơ sở lý thuyết

## 4.1. Đánh giá đọc hiểu

Đánh giá đọc hiểu cần xác định người học có thể xử lý thông tin trong văn
bản ở mức độ nào, từ nhận biết chi tiết đến hiểu ý chính và suy luận. Một bài
kiểm tra có giá trị cần liên kết câu hỏi với mục tiêu đánh giá, văn bản nguồn
và tiêu chí chấm. Bài thi do ứng dụng tạo chỉ là bài luyện tập; chưa có nghiên
cứu xác nhận độ tin cậy hoặc giá trị đo lường như một công cụ thi chuẩn hóa.

Trong nghiên cứu này, “giống format” cần được tách khỏi “đo cùng năng lực”.
Checklist hình thức chỉ có thể đo các thuộc tính quan sát được của tài liệu
tham chiếu; không tự chứng minh độ khó tương đương, độ tin cậy, tính giá trị
hay việc điểm số dự đoán kết quả YKI. Thesis cần nói chính xác phần nào đang
được đánh giá và không mở rộng kết luận vượt quá rubric.

## 4.2. Khung CEFR và trình độ ngôn ngữ

CEFR cung cấp các mức mô tả năng lực ngôn ngữ để hỗ trợ việc dạy, học và đánh
giá (Council of Europe, 2020). Trong hệ thống, model được yêu cầu chọn A2,
B1, B2 hoặc C1 và trả kèm độ tin cậy. Giá trị confidence do model tự trả về
không mặc nhiên là xác suất
đã được hiệu chuẩn; cần so sánh với nhãn chuyên gia trước khi diễn giải như
một thước đo độ chính xác.

Không được đồng nhất các mức CEFR mà ứng dụng yêu cầu với mức YKI nếu không
có tài liệu chính thức xác lập ánh xạ. Trong bản đánh giá hiện tại, CEFR có
thể dùng để mô tả biến thể bài đọc hoặc phân tầng kết quả khi có nhãn tham
chiếu; nó không phải câu hỏi nghiên cứu chính trừ khi bổ sung nghiên cứu
riêng về phân loại trình độ.

## 4.3. Xử lý ngôn ngữ tự nhiên và LLM

LLM tạo văn bản bằng cách dự đoán token dựa trên ngữ cảnh và tham số đã học.
Trong ứng dụng, model nhận prompt có yêu cầu về loại câu hỏi và định dạng
JSON. Vì đầu ra sinh có thể không tuân theo cấu trúc yêu cầu hoặc chứa thông
tin không được bài đọc hỗ trợ, ứng dụng cần xác thực dữ liệu và đánh giá nội
dung độc lập.

Lời nhắc yêu cầu đầu ra JSON và bộ phân tích JSON bảo đảm tính hợp lệ cú
pháp ở một mức độ, không bảo đảm tính đúng ngữ nghĩa. Tương tự, lời nhắc
yêu cầu “chỉ dựa vào bài” không phải bằng chứng rằng mọi câu trả lời thực
sự có căn cứ trong bài. Vì thế, đánh giá thesis lưu và kiểm tra đầu ra thực
tế thay vì suy luận chất lượng từ prompt.

## 4.4. Tạo câu hỏi tự động

Tạo câu hỏi tự động chuyển một văn bản nguồn thành câu hỏi và đáp án
(Heilman & Smith, 2010). Chất lượng không chỉ phụ thuộc tính hợp lệ về cú
pháp mà còn phụ thuộc câu hỏi có
được hỗ trợ bởi văn bản, có đáp án xác định, không mơ hồ và phù hợp với mục
tiêu học tập hay không. Vì vậy, kiểm tra JSON trong phần mềm là điều kiện
cần cho tính nhất quán, nhưng không thay thế đánh giá sư phạm.

Để phân tích sai sót, có thể phân loại lỗi thành: (a) lỗi định dạng/tác vụ,
(b) câu hỏi không có câu trả lời trong bài, (c) đáp án sai hoặc không duy
nhất, (d) lựa chọn nhiễu vô lý hoặc nhiều lựa chọn đúng, (e) câu hỏi mơ hồ,
(f) câu hỏi không đo khả năng đọc hiểu, và (g) mức ngôn ngữ không phù hợp.
Danh mục cuối cùng cần được kiểm tra với tài liệu nghiên cứu và đưa vào
rubric trước khi chấm, không thêm sau khi đã thấy kết quả chỉ để giải thích
điểm thấp.

## 4.5. Phân loại trình độ và đánh giá model

Phân loại mức CEFR trong ứng dụng là yêu cầu gửi đến model bên ngoài, không
phải mô hình được huấn luyện trong dự án. Để đánh giá, cần có tập bài độc lập
với nhãn tham chiếu. Vì các nhãn CEFR có thứ tự, phân tích cần cân nhắc mức
độ sai lệch giữa các mức thay vì chỉ báo cáo một tỷ lệ đúng tổng quát.

## 4.6. Chấm điểm tự động

Các câu hỏi đóng được chấm bằng so sánh chuỗi sau khi chuẩn hóa khoảng trắng
đầu/cuối và chữ hoa/thường. Câu trả lời mở được chấm bằng số từ khóa khớp:
cần đạt ít nhất 60% danh sách từ khóa, tối thiểu một từ khóa. Cách này dễ
giải thích và dễ kiểm thử, nhưng có thể đánh dấu sai câu trả lời đồng nghĩa
hoặc bỏ sót câu trả lời sai có chứa từ khóa. Do đó, kết quả cần được trình
bày như phản hồi luyện tập, không phải đánh giá ngôn ngữ toàn diện.

Trong nghiên cứu RQ2, cần phân biệt việc đánh giá **answer key do AI tạo**
với việc đánh giá **câu trả lời do người học nhập**. RQ2 xem xét liệu đáp án
chuẩn mà hệ thống gắn với câu hỏi có đúng hay không; thuật toán chấm người
học không tự chứng minh answer key đó đúng. Cần lập đáp án tham chiếu độc lập
và lưu đoạn bằng chứng cho từng câu.

## 4.7. Từ vựng theo ngữ cảnh

Một từ có thể có nhiều nghĩa; nghĩa phù hợp phụ thuộc câu, đoạn văn và cấu
trúc ngữ pháp. Đánh giá Tutor vì vậy cần cung cấp ngữ cảnh đầy đủ và kiểm tra
nghĩa được giải thích có đúng với lần xuất hiện trong bài hay không. Bản
dịch từ điển hoặc bản dịch máy có thể là gợi ý đối chiếu nhưng không phải
chuẩn vàng tự động. Nếu nghiên cứu bao gồm lemma, loại từ hay biến tố, mỗi
khía cạnh phải có tiêu chí chấm riêng.

## 4.8. Nguyên tắc đánh giá giáo dục

Tính hữu ích của công cụ học tập không thể được suy ra chỉ từ việc phần mềm
khởi chạy hoặc vượt qua kiểm thử kỹ thuật. Cần xác định đối tượng học, tác vụ,
tiêu chí thành công và dữ liệu quan sát (Black & Wiliam, 1998). Nếu nghiên cứu
có người tham gia, cần tuân thủ hướng dẫn đạo đức nghiên cứu, thông tin đồng
thuận và bảo vệ dữ liệu của cơ sở đào tạo.

# 5. Giải pháp đề xuất và triển khai

## 5.1. Đóng góp và tính mới

### 5.1.1. Đóng góp kỹ thuật đã có trong mã nguồn

1. **Quy trình tích hợp cho luyện đọc:** kết nối nhập bài, phân tích AI, tạo
   đề, làm bài, chấm điểm, lưu kết quả và hỏi Tutor.
2. **Tạo câu hỏi có đầu ra ràng buộc:** yêu cầu cơ cấu đề cố định và từ chối
   đầu ra không đủ số lượng, loại câu hoặc trường dữ liệu bắt buộc.
3. **Kho đề mẫu có kiểm soát:** SQLite lưu bài mẫu riêng chỉ sau khi quyền
   tái sử dụng được ghi nhận và duyệt; bài người dùng nhập và kết quả luyện
   riêng không được lưu.
4. **Tutor có ngữ cảnh bài đọc:** sử dụng công cụ tìm kiếm câu liên quan và
   giới hạn các công cụ được agent gọi trong một lượt.

Các điểm trên là đóng góp về thiết kế và triển khai một nguyên mẫu. Chúng
chưa chứng minh tính mới so với mọi nghiên cứu hoặc sản phẩm đã công bố.

### 5.1.2. Đóng góp nghiên cứu dự kiến

Đóng góp học thuật dự kiến không phải một LLM mới, mà là phép đánh giá thực
nghiệm có thể lặp lại cho một công cụ luyện đọc tiếng Phần Lan dùng LLM.
Nghiên cứu sẽ lượng hóa (1) mức tuân thủ định dạng đối chiếu với tài liệu
YKI chính thức, (2) tỷ lệ lượt sinh có toàn bộ đáp án chính xác 100%, và
(3) tỷ lệ giải thích từ vựng chính xác theo ngữ cảnh bài đọc.

Đóng góp này chỉ được xác lập khi có bộ dữ liệu được mô tả, rubric được
duyệt trước, người đánh giá phù hợp, kết quả định lượng và phân tích trường
hợp sai. Hiện tại đây là **đóng góp dự kiến**, chưa phải phát hiện hoặc kết
quả đã có. Cần xin giảng viên hướng dẫn duyệt thiết kế, cỡ mẫu và yêu cầu
đạo đức trước khi thu thập dữ liệu.

## 5.2. Kiến trúc hệ thống

Hệ thống được chia thành các nhóm thành phần:

1. `views/`: giao diện Streamlit cho bài đọc, bài thi, kết quả và Tutor.
2. `services/`: điều phối nghiệp vụ bài đọc, bài thi, đồng hồ, chấm điểm và
   Tutor.
3. `ai/`: tích hợp model để phân tích trình độ, chủ đề và tạo câu hỏi.
4. `repositories/`: truy vấn và ghi dữ liệu.
5. `models/`: cấu trúc dữ liệu của bài đọc, câu hỏi, đáp án và kết quả.
6. `database/` và `data/`: khởi tạo schema và lưu thư viện đề mẫu đã duyệt cùng dữ liệu liên quan.

`app.py` khởi tạo cấu hình Streamlit, tạo schema khi cần và gọi giao diện
chính.

![Sơ đồ kiến trúc hệ thống](docs/architecture.png)

**Hình 1.** Kiến trúc tổng quan của YKI Reading AI Coach.  
**[CẦN HOÀN THIỆN]** Kiểm tra sơ đồ hiện có và bảo đảm hình thể hiện đúng
các lớp, luồng dữ liệu và dịch vụ bên ngoài nêu trong chương này.

## 5.3. Quy trình xử lý bài đọc

1. Người học nhập tiêu đề, nguồn và nội dung cho một phiên luyện riêng.
2. Hệ thống kiểm tra các trường bắt buộc.
3. Model ước lượng trình độ; bài ngoài B1, B2 hoặc C1 bị loại khỏi luồng tạo
   đề.
4. Model phân loại chủ đề và tạo danh sách câu hỏi theo prompt.
5. Bộ xác thực kiểm tra JSON, số lượng câu, loại câu, lựa chọn, đáp án và từ
   khóa.
6. Bài và câu hỏi của người học chỉ ở trong bộ nhớ phiên; không ghi vào DB
   và không được dùng làm đề mẫu.
7. Người học làm bài trong 30 phút; ScoreService chấm trong bộ nhớ. Chỉ kết
   quả của đề mẫu đã được duyệt mới được ghi vào kho kết quả.
8. AI Tutor nhận câu hỏi của người học và ngữ cảnh bài hiện tại; khi cần,
   agent gọi công cụ tìm kiếm bài hoặc tra từ.

![Sơ đồ luồng xử lý](docs/workflow.png)

**Hình 2.** Luồng xử lý chính từ bài đọc đến kết quả luyện tập.  
**[CẦN HOÀN THIỆN]** Bảo đảm sơ đồ chỉ rõ các lời gọi model bên ngoài, các
bước kiểm tra đầu ra và nơi lưu dữ liệu.

## 5.4. Sinh câu hỏi và kiểm tra đầu ra

Prompt trong `ai/question_generator.py` yêu cầu model trả về đúng năm câu:
hai câu `multiple_choice`, hai câu `true_false` và một câu `open`. Hàm
`generate_questions` giải mã JSON, kiểm tra kiểu dữ liệu và phân phối câu hỏi.
Câu trắc nghiệm phải có bốn lựa chọn và đáp án đúng thuộc các lựa chọn; câu
đúng/sai phải có một trong hai đáp án hợp lệ; câu mở phải có từ ba đến năm
từ khóa.

Việc kiểm tra bảo đảm định dạng và một số điều kiện cấu trúc. Nó không tự
động xác minh sự thật của đáp án hoặc mức độ phù hợp giáo dục. Những tiêu chí
ngữ nghĩa này thuộc phạm vi đánh giá con người được đề xuất trong Chương 2.

## 5.5. Phân tích trình độ và chủ đề

`ai/level_detector.py` gửi bài đọc đến model và kiểm tra nhãn thuộc A2, B1,
B2 hoặc C1 cùng confidence trong khoảng từ 0 đến 1. `ai/subject_classifier.py`
yêu cầu model chọn một chủ đề từ danh sách được quy định và kiểm tra phản hồi
trước khi trả kết quả.

Đây là các lời gọi đến model có sẵn qua Groq. Dự án không có tập huấn luyện,
quy trình fine-tuning hoặc trọng số classifier riêng. Tên gọi và kết luận
trong thesis cần phản ánh chính xác cách triển khai này.

## 5.6. Cơ sở dữ liệu

Cơ sở dữ liệu `data/yki.db` có các bảng:

| Bảng | Dữ liệu |
|---|---|
| `articles` | Chỉ bài đã duyệt quyền tái sử dụng làm đề mẫu; gồm nội dung và thông tin căn cứ/duyệt quyền. |
| `questions` | Nội dung câu, lựa chọn, đáp án, từ khóa và giải thích. |
| `exam_results` | Tổng số câu, số câu đúng, điểm và thời gian tạo kết quả. |
| `user_answers` | Câu trả lời đã chọn và trạng thái đúng/sai. |
| `vocabulary_translations` | Cache bản dịch theo cụm từ và cặp ngôn ngữ. |
| `vocabulary_words` | Mục từ được khóa theo lemma (ví dụ `kotona` được lưu dưới khóa `koti`), loại từ, loại danh từ/động từ, dạng đã hỏi, đặc điểm ngữ pháp và ngữ cảnh bài đọc. |
| `vocabulary_word_forms` | Các dạng biến tố của lemma theo cách (case), số (singular/plural) và dạng từ; ví dụ `koti` có `partitive/singular = kotia`, `partitive/plural = kotoja`. |

Schema được khởi tạo bởi `database/init_db.py`; truy vấn được tách qua các
repository tương ứng.

Bài do người học nhập chỉ được xử lý trong phiên để tạo đề luyện cá nhân;
không lưu bài hoặc kết quả luyện đó vào SQLite, và không đưa vào đề mẫu.
Nội dung được gửi đến AI provider cấu hình để phân tích. Kho đề mẫu được
quản lý riêng qua `ExamService.add_approved_library_article`; thao tác này
bắt buộc có căn cứ quyền, tài liệu tham chiếu và người duyệt. Chỉ bài có
`reuse_approved = 1` mới được chọn ngẫu nhiên. Các trường kiểm soát này
không thay thế việc xác minh pháp lý giấy phép.

### Thu thập tự động bài mẫu từ RSS/Atom

Mở **Build the sample-exam library from licensed feeds** ở cuối trang chủ.
Chỉ đăng ký feed nếu giấy phép hoặc văn bản cho phép lưu toàn văn, tạo câu
hỏi phái sinh, gửi nội dung đến AI provider và hiển thị đề cho người học.
Nhập nhà xuất bản, URL RSS/Atom, căn cứ quyền, liên kết bằng chứng và người
duyệt; đánh dấu xác nhận quyền để thêm feed và chạy nhập ngay.

Luồng chỉ đọc nội dung bài có sẵn trong RSS/Atom, không tải trang bài báo
riêng. Bài thiếu toàn văn trong feed sẽ bị bỏ qua. Có bốn kho, mỗi kho tối
đa 10 bài (40 bài tổng cộng): thông báo/quảng cáo/tin nhắn 20-100 từ (4 câu trắc nghiệm);
email/thư/hướng dẫn 100-250 từ (4 câu đúng-sai); Utiset 300-600 từ, B2 (5
câu mở); và Selkouutiset 300-600 từ, B1 (5 câu mở). Câu hỏi mở phải có đáp
án mẫu cùng từ khóa chấm tự động. Bài trùng URL, sai độ dài/trình độ, hoặc
không tạo được đúng dạng câu hỏi sẽ không được lưu.

Mỗi đề ngẫu nhiên ghép một bài từ từng kho: tổng cộng 4 bài và 18 câu (4
trắc nghiệm, 4 đúng-sai, 10 câu mở). Các câu hỏi, đáp án mẫu và quan hệ kết
quả làm bài với cả bốn bài được lưu trong SQLite. Câu hỏi được tạo tự động
chỉ là đáp án tham khảo, cần được người có chuyên môn kiểm tra trước khi
dùng như tài liệu đánh giá chính thức.
Feed đã đăng ký có thể được chạy lại bằng nút **Fetch and process new
articles** hoặc chạy cùng lúc bằng nút **Fetch all registered feeds**; việc
chạy là theo yêu cầu trong giao diện, không chạy nền theo lịch. URL feed phải
dùng HTTP(S), phân giải tới IP công khai và không được chuyển hướng.

Ứng dụng ghi nhận căn cứ quyền và lời xác nhận của người duyệt nhưng không
xác minh độc lập giấy phép. Hai trang hướng dẫn YKI được trích dẫn ở nơi khác
trong tài liệu không tự động trở thành nguồn nội dung được cấp phép và không
được crawler thêm sẵn.

### Nạp sẵn nội dung luyện tập nguyên bản

Để tạo dữ liệu khởi đầu khi database còn thiếu bài, chạy:

```powershell
.\venv\Scripts\python.exe -m sample_exam_builder
```

Mã tạo đề mẫu tùy chọn nằm riêng trong thư mục `sample_exam_builder/`.
Ứng dụng không import thư mục này; có thể bỏ thư mục nếu không cần tạo thêm
nội dung. Database `data/yki.db` và chức năng làm đề mẫu đã có vẫn hoạt động.
Lệnh trên dùng Groq API đã cấu hình để tạo tối đa 40 văn bản tiếng Phần Lan nguyên
bản cùng 180 câu hỏi/đáp án, rồi lưu trực tiếp vào SQLite: 10 bài mỗi nhóm
và mỗi bài có 4 câu hỏi cho notice/email hoặc 5 câu hỏi mở cho Utiset/
Selkouutiset. Seeder kiểm tra loại bài, số từ, chủ đề, số câu và đáp án mẫu
trước khi lưu; nếu API hoặc dữ liệu trả về sai, lệnh báo lỗi và có thể chạy
lại để hoàn thành quota còn thiếu. Đây là nội dung luyện tập tổng hợp, không
phải bài báo thật. Việc gọi API có thể phát sinh chi phí.

## 5.7. AI Tutor

`TutorService` tra phân tích và nghĩa từ vựng trong SQLite trước. Nếu tìm
được lemma hoặc dạng biến tố đã lưu kèm nghĩa, Tutor trả từ cache mà không
khởi tạo Groq agent. Khi cache miss, Tutor mới gọi AI để phân tích và lưu
nghĩa, lemma, loại từ và các dạng đã nhận diện. Dạng cần tra được so với
lemma, dạng đã hỏi trước đó và các dạng biến tố được lưu; dạng biến tố mới
chưa có trong dữ liệu vẫn cần AI để phân tích. Nếu có bài đang học, câu chứa
từ được tìm cục bộ và thêm vào câu trả lời cache; không có bài thì dùng nghĩa
chung. Bản dịch riêng có thể dùng MyMemory; chỉ cụm từ được yêu cầu được gửi,
không gửi toàn bài đọc. Bản dịch thành công được lưu trong
`vocabulary_translations`. Khi người học hỏi một từ tiếng Phần Lan, Tutor
cũng lưu lemma làm khóa mục từ, dạng được hỏi, loại từ, biến tố/hậu tố,
thay đổi thân từ, chủ đề và mã bài đọc trong `vocabulary_words`. Những dạng
biến cách mà Tutor phân tích được lưu riêng theo case và số trong
`vocabulary_word_forms`.

AI Tutor có thể đưa ra câu trả lời không chính xác. Sự có mặt của công cụ tìm
kiếm không bảo đảm mọi câu trả lời đều được hỗ trợ đầy đủ bởi nguồn; tính
đúng đắn cần được đánh giá riêng nếu là một phần của kết luận thesis.

## 5.8. Luyện viết và điều hướng kỹ năng

Luồng Reading nhận nội dung bài đọc mà không yêu cầu người học nhập tiêu đề
hoặc nguồn; các bước ước lượng trình độ, phân loại chủ đề và tạo câu hỏi vẫn
được giữ nguyên. Mục Example Reading Exam tiếp tục tải đề mẫu đã duyệt từ
thư viện.

Writing gửi bài tiếng Phần Lan đến model để ước lượng mức gần B1/B2, nhận xét
điểm mạnh, chỉ ra lỗi chính tả/ngữ pháp, gợi ý cấu trúc câu và đưa ra một bản
viết đề xuất. Đây là phản hồi luyện tập, không phải điểm YKI hay chứng nhận
CEFR chính thức. Listening và Speaking hiện chỉ là khung giao diện, chưa có
bài nghe, ghi âm hoặc chấm nói.

# 6. Kết quả và đánh giá

## 6.1. Kết quả triển khai

Mã nguồn hiện có các chức năng nhập và xử lý bài đọc trong phiên, quản lý
kho bài mẫu đã duyệt quyền, làm bài theo thời gian, chấm và lưu kết quả đề
mẫu, cũng như giao diện
AI Tutor. Đây là mô tả chức năng từ hiện trạng mã nguồn, không phải kết quả
đánh giá hiệu quả học tập.

## 6.2. Kết quả kiểm thử phần mềm

**Lần chạy kiểm thử ngày 24/10/2026:** `python -m pytest -q` thu được 85
kiểm thử đạt và 3 kiểm thử thất bại (tổng 88). Ba lỗi nằm trong kiểm thử giao
diện: không tìm thấy nút “Start Exam”, không thấy thông báo mức “Level: B1”,
và không thấy tiêu đề “Exam Result”. Vì vậy, không thể kết luận toàn bộ bộ
kiểm thử đạt; các kiểm thử giao diện này cần được điều tra và chạy lại trước
khi nộp thesis.

Các kiểm thử dùng phản hồi AI giả lập. Kết quả này chỉ cung cấp bằng chứng
cho hành vi phần mềm được kiểm thử; nó không xác nhận độ chính xác của Groq,
MyMemory, phân loại CEFR hoặc chất lượng câu hỏi thực tế.

## 6.3. Kết quả nghiên cứu thực nghiệm

**Chưa có dữ liệu thực nghiệm cho ba câu hỏi nghiên cứu trong repository
hiện tại.** Không thể đưa ra tỷ lệ phần trăm đáng tin cậy chỉ bằng cách đọc
mã nguồn hoặc chạy unit test. Sau khi thực hiện nghiên cứu, thay các ô dưới
đây bằng số liệu thật và nêu rõ mẫu số, phạm vi cùng người chấm.

| Câu hỏi | Chỉ số cần báo cáo | Kết quả hiện tại |
|---|---|---|
| RQ1: tuân thủ format YKI | Tỷ lệ mục checklist đạt trung bình và tỷ lệ đề đạt tất cả tiêu chí | Chưa đo |
| RQ2: đáp án chính xác 100% | Tỷ lệ lượt sinh mà mọi đáp án đều đúng; kèm độ chính xác theo đáp án để chẩn đoán | Chưa đo |
| RQ3: Tutor giải thích nghĩa theo ngữ cảnh | Tỷ lệ giải thích được người chấm xác nhận đúng hoàn toàn | Chưa đo |

Mỗi kết quả cần đi kèm: số lượng lượt được đánh giá; số bài và số lần sinh
trên mỗi bài; cấu hình model/prompt; nguồn đối chiếu; số lượng và năng lực
người chấm; cách xử lý bất đồng; khoảng tin cậy hoặc giới hạn thống kê phù
hợp. Không được điền tỷ lệ dựa trên kỳ vọng hoặc confidence do model tự khai.

### Bảng kết quả cần hoàn thiện

| Chỉ số | Tử số | Mẫu số | Tỷ lệ | Khoảng tin cậy | Ghi chú |
|---|---:|---:|---:|---|---|
| RQ1: mục checklist đạt | [ ] | [ ] | [ ]% | [ ] | [ ] |
| RQ1: lượt sinh đạt toàn bộ format | [ ] | [ ] | [ ]% | [ ] | [ ] |
| RQ2: đáp án đúng theo từng câu | [ ] | [ ] | [ ]% | [ ] | [ ] |
| RQ2: lượt sinh có mọi đáp án đúng | [ ] | [ ] | [ ]% | [ ] | [ ] |
| RQ3: giải thích đúng ngữ cảnh | [ ] | [ ] | [ ]% | [ ] | [ ] |
| Tỷ lệ gọi API sinh thành công | [ ] | [ ] | [ ]% | [ ] | Báo riêng, không thay RQ chính |

## 6.4. Thảo luận

Các kiểm thử tự động cho thấy nhiều thành phần phần mềm có thể được kiểm tra
độc lập, nhưng ba lỗi hiện tại trong kiểm thử giao diện làm giảm mức độ bằng
chứng cho toàn luồng người dùng. Ngoài ra, kết quả test giả lập không đại
diện cho đầu ra của model trong môi trường thực tế. Các câu hỏi nghiên cứu
cần được trả lời bằng đánh giá đầu ra API thật theo ba định nghĩa đo lường
đã nêu ở Chương 2, không suy diễn từ unit test.

### 6.4.1. Thảo luận RQ1: định dạng YKI

Khi có số liệu, giải thích tiêu chí nào đạt cao/thấp và vì sao. Đối chiếu
các khác biệt quan sát được với đúng nguồn YKI đã trích; phân biệt lỗi hình
thức (ví dụ hướng dẫn hoặc loại tác vụ không khớp) với khác biệt về chất
lượng/độ khó mà checklist không đo. Nếu tất cả câu hỏi đều theo cùng một
cấu trúc của ứng dụng nhưng không phù hợp tài liệu chính thức, điều đó phải
được nêu là kết quả quan trọng, không nên diễn giải thành “gần format” chỉ
vì đề có câu hỏi đọc hiểu.

**[SAU KHI ĐO]** Nêu tỷ lệ đề tuân thủ toàn bộ tiêu chí, tiêu chí thường bị
trượt, ví dụ đại diện đã được phép trích dẫn, và giới hạn của checklist.

### 6.4.2. Thảo luận RQ2: đáp án đúng tuyệt đối

Phân tích số đề đạt toàn bộ đáp án đúng, không chỉ độ chính xác gộp từng câu.
Phân loại lỗi theo loại câu: đáp án mâu thuẫn với bài, câu hỏi có nhiều đáp
án hợp lý, thông tin ngoài văn bản, đáp án sai ở câu đúng/sai, hoặc tiêu chí
câu mở không bao phủ cách diễn đạt tương đương. Nếu một đề có một lỗi, đề
không đạt tiêu chí 100%; đồng thời chỉ ra nguyên nhân để hướng tới cải thiện
đúng chỗ.

**[SAU KHI ĐO]** So sánh tỷ lệ strict 100% giữa các lần sinh/bài đọc hoặc
loại câu nếu thiết kế mẫu cho phép. Nêu mức độ không chắc chắn và tránh gọi
điểm ước lượng là bảo đảm model sẽ luôn chính xác.

### 6.4.3. Thảo luận RQ3: nghĩa từ vựng trong ngữ cảnh

Phân tích xem Tutor hiểu sai do đa nghĩa, biến tố tiếng Phần Lan, thành ngữ,
thiếu câu ngữ cảnh hay câu trả lời có nội dung đúng nhưng giải thích chưa
đầy đủ. Phân biệt lỗi của MyMemory (bản dịch gợi ý) với lỗi lập luận/giải
thích của Tutor; không coi bản dịch API là đáp án chuẩn. Nếu mẫu chỉ gồm từ
dễ hoặc từ đơn nghĩa, không khái quát kết quả sang toàn bộ từ vựng trong
bài báo.

**[SAU KHI ĐO]** Báo tỷ lệ đúng hoàn toàn, khoảng tin cậy, phân tích theo
nhóm mục từ và một số trường hợp sai tiêu biểu đã ẩn thông tin phù hợp.

### 6.4.4. Độ tin cậy và giới hạn suy luận

Thảo luận ảnh hưởng của số bài, số lần gọi API trên cùng bài, mức biến thiên
do model, nguồn và trình độ bài, lựa chọn từ vựng, năng lực người chấm, cách
xử lý bất đồng và lỗi API. Nhiều lượt sinh trên một bài có tương quan; không
diễn giải số lượng lượt như số lượng bài độc lập. Báo cả độ chính xác theo
từng đơn vị và strict pass rate cấp đề để người đọc hiểu mẫu số.

Không kết luận rằng công cụ cải thiện kết quả học tập vì nghiên cứu này
không đo trước/sau hay có nhóm đối chứng. Không khẳng định khả năng tương
đương bài thi chính thức từ checklist format. Không khẳng định 100% đúng
trong tương lai từ việc quan sát 100% trên một mẫu hữu hạn.

# 7. Kết luận

## 7.1. Tổng kết

YKI Reading AI Coach là nguyên mẫu phần mềm tích hợp chức năng phân tích bài
đọc bằng LLM, tạo câu hỏi có cấu trúc, làm bài theo thời gian, chấm điểm,
lưu dữ liệu và hỗ trợ người học qua AI Tutor. Kiến trúc tách giao diện,
nghiệp vụ, tích hợp AI và truy cập dữ liệu.

## 7.2. Trả lời câu hỏi nghiên cứu

**[ĐIỀN SAU NGHIÊN CỨU; không giữ nguyên hướng dẫn trong bản nộp cuối]**

- **RQ1:** Trong `[N]` lượt sinh, `[n]` lượt đạt đầy đủ checklist tham chiếu
  `[tên/phiên bản nguồn]`, tương đương `[x]%` (khoảng tin cậy `[CI]`). Các
  khác biệt thường gặp là `[ ]`. Do checklist đo `[ ]`, kết quả không chứng
  minh tương đương về độ khó hoặc giá trị đánh giá.
- **RQ2:** `[n]` trong `[N]` lượt sinh có toàn bộ đáp án đúng, tương đương
  `[x]%`. Tỷ lệ đúng cấp câu là `[x]%`. Các lỗi chính gồm `[ ]`; vì vậy kết
  quả `[ủng hộ/không ủng hộ]` việc dùng đề sinh tự động mà không có bước
  duyệt người.
- **RQ3:** `[n]` trong `[N]` yêu cầu được giải thích đúng hoàn toàn theo
  ngữ cảnh, tương đương `[x]%`. Hiệu năng khác nhau theo `[nhóm từ/cấu trúc]`;
  giới hạn quan sát được là `[ ]`.

Chỉ giữ những câu trả lời có dữ liệu tương ứng. Nếu một câu hỏi không được
đo, nêu rõ chưa giải quyết thay vì đưa ra kết luận suy đoán.

## 7.3. Hạn chế

- Chưa có đánh giá thực nghiệm RQ1–RQ3 trong repository hiện tại.
- Kết quả phụ thuộc model/API, prompt và thời điểm gọi; các phiên bản có thể
  thay đổi.
- Câu trả lời mở được chấm bằng từ khóa, chưa đánh giá tương đương ngữ nghĩa.
- Kiểm thử giao diện hiện có 3 trường hợp thất bại trong lần chạy được ghi
  nhận ở Chương 6.
- Chưa tiến hành nghiên cứu người dùng hoặc đo lường kết quả học tập.
- Kết quả phụ thuộc dịch vụ model bên ngoài và khả năng truy cập API.

## 7.4. Hướng phát triển

Ưu tiên nghiên cứu tiếp theo là cố định câu hỏi nghiên cứu và rubric, xây dựng
tập đánh giá có quyền sử dụng rõ ràng, thu thập nhận xét của người có chuyên
môn, sửa các kiểm thử giao diện thất bại và chạy lại toàn bộ kiểm thử. Sau đó
có thể nghiên cứu cải thiện chấm câu trả lời mở, tăng khả năng truy xuất
ngữ cảnh và tiến hành thử nghiệm khả dụng với người học nếu được phê duyệt.

# Tài liệu tham khảo

> Các tài liệu dưới đây là nguồn nền tảng gợi ý cho bản thảo. Cần kiểm tra
> yêu cầu trích dẫn của trường, xác minh thông tin thư mục và bổ sung nguồn
> chính thức YKI, nguồn về LLM và các sản phẩm hiện có trước khi nộp. Mỗi
> nguồn trong danh sách cuối cùng phải được trích dẫn trong nội dung.

- Bachman, L. F. & Palmer, A. S. 1996. *Language Testing in Practice:
  Designing and Developing Useful Language Tests*. Oxford: Oxford University
  Press.
- Black, P. & Wiliam, D. 1998. Assessment and classroom learning. *Assessment
  in Education: Principles, Policy & Practice*, 5(1), 7–74.
- Council of Europe. 2020. *Common European Framework of Reference for
  Languages: Learning, Teaching, Assessment – Companion Volume*. Strasbourg:
  Council of Europe.
- Heilman, M. & Smith, N. A. 2010. Good question! Statistical ranking for
  question generation. In *Proceedings of the Human Language Technologies:
  The 2010 Annual Conference of the North American Chapter of the Association
  for Computational Linguistics*, 609–617.
- Hevner, A. R.; March, S. T.; Park, J. & Ram, S. 2004. Design science in
  information systems research. *MIS Quarterly*, 28(1), 75–105.

**[CẦN BỔ SUNG]** Tài liệu chính thức của Finnish National Agency for
Education về YKI; tài liệu mô tả Groq, Qwen, Streamlit, LangChain và SQLite;
bài nghiên cứu gần đây về LLM question generation, CEFR classification và
đánh giá học liệu; tài liệu về đạo đức và quyền sử dụng dữ liệu bài báo.

# Phụ lục A. Phiếu chấm và cấu trúc dữ liệu nghiên cứu

## A.1. Phiếu RQ1 – Tuân thủ format

Tạo một bản cho mỗi lượt sinh đề. Trước khi sử dụng, thêm nguồn YKI và mô tả
định nghĩa đạt/không đạt cho từng mục.

| Mã tiêu chí | Yêu cầu trích từ nguồn YKI | Nguồn/trang/mục | Áp dụng? | Đạt? | Ghi chú/bằng chứng |
|---|---|---|---|---|---|
| F-01 | [Điền theo nguồn chính thức] | [ ] | [Có/không] | [Có/không] | [ ] |
| F-02 | [Điền theo nguồn chính thức] | [ ] | [Có/không] | [Có/không] | [ ] |
| F-03 | [Điền theo nguồn chính thức] | [ ] | [Có/không] | [Có/không] | [ ] |
| F-04 | [Điền theo nguồn chính thức] | [ ] | [Có/không] | [Có/không] | [ ] |

Không giữ các tiêu chí minh họa nếu chúng không có căn cứ trong tài liệu
chính thức hoặc không áp dụng được cho đầu ra của ứng dụng. Ghi phiên bản
checklist và không sửa định nghĩa sau khi đã xem điểm, trừ khi ghi rõ thay
đổi và chấm lại toàn bộ mẫu.

## A.2. Phiếu RQ2 – Độ chính xác đáp án

| ID lượt sinh | ID bài | Câu | Loại câu | Đáp án tham chiếu | Đoạn bằng chứng trong bài | Đáp án AI | Đúng? | Lý do/lỗi |
|---|---|---:|---|---|---|---|---|---|
| [ ] | [ ] | [ ] | [ ] | [Lập trước khi xem AI] | [ ] | [ ] | [Có/không] | [ ] |

**Quy tắc đề đạt:** tất cả các câu có đáp án xác định và đúng; nếu một câu
sai, không xác minh được, mơ hồ hoặc đề không hợp lệ thì lượt sinh không đạt
chỉ số 100%. Hai người chấm ghi kết quả độc lập. Thêm dòng cho từng câu,
không chỉ nhập kết quả tổng của đề.

## A.3. Phiếu RQ3 – Nghĩa từ vựng trong ngữ cảnh

| ID yêu cầu | ID bài | Từ/cụm từ | Câu nguồn | Nghĩa tham chiếu | Phản hồi Tutor | Đúng hoàn toàn? | Loại lỗi/ghi chú |
|---|---|---|---|---|---|---|---|
| [ ] | [ ] | [ ] | [ ] | [Xác minh trước khi xem phản hồi] | [ ] | [Có/không] | [ ] |

Các loại lỗi có thể dùng làm mã phân tích sau khi được duyệt: chọn sai nghĩa,
bỏ sót nghĩa theo ngữ cảnh, giải thích hình thái sai, thông tin mâu thuẫn,
khẳng định không có căn cứ, diễn đạt không đủ để trả lời, hoặc không phản
hồi. Có thể ghi nhiều mã cho một câu trả lời; định nghĩa mã phải được thống
nhất trước khi chấm.

## A.4. Nhật ký lượt gọi model

| Trường | Giá trị |
|---|---|
| ID yêu cầu | [ ] |
| ID bài đọc / ID từ vựng | [ ] |
| Ngày, giờ và múi giờ | [ ] |
| Phiên bản ứng dụng / mã commit | [ ] |
| Model ID do API trả về hoặc cấu hình | [ ] |
| Phiên bản prompt / checksum prompt | [ ] |
| Tham số sinh khả dụng | [ ] |
| Trạng thái API | [Thành công/lỗi/timeout/không hợp lệ] |
| Nội dung đầu ra nguyên bản | [Lưu tại vị trí bảo mật; không ghi bí mật] |
| Ghi chú | [ ] |

Đảm bảo đầu ra nghiên cứu không chứa API key hoặc thông tin cá nhân. Nếu
điều khoản dịch vụ không cho phép lưu prompt/đầu ra hoặc bài đọc, cần xin
phê duyệt và điều chỉnh quy trình trước khi thu thập.

# Phụ lục B. Danh sách việc cần hoàn thành trước khi nộp

Đánh dấu mỗi mục và lưu bằng chứng phù hợp. Các mục dưới đây không phải kết
quả đã hoàn tất.

## B.1. Phê duyệt phạm vi và phương pháp

- [ ] Xác nhận với giảng viên đây là phạm vi thesis được chấp nhận.
- [ ] Xác nhận ba RQ, hoặc thu hẹp xuống câu hỏi có thể hoàn thành đúng hạn.
- [ ] Xác nhận tiêu chí “tuân thủ format YKI” từ nguồn chính thức.
- [ ] Xác nhận định nghĩa “đáp án 100% chính xác”, gồm xử lý câu mở.
- [ ] Xác nhận nghĩa “đúng hoàn toàn” cho lời giải thích Tutor.
- [ ] Xác nhận kích thước mẫu, số lần sinh trên mỗi bài và số yêu cầu Tutor.
- [ ] Xác nhận người chấm, trình độ cần có, cách chấm độc lập và cách xử lý
  bất đồng.
- [ ] Xác nhận yêu cầu ethics/consent nếu có người tham gia.

## B.2. Dữ liệu và tài liệu tham khảo

- [ ] Thu thập nguồn chính thức về YKI; lưu bản/URL/ngày truy cập.
- [ ] Xây dựng checklist RQ1 và trích nguồn cho từng tiêu chí.
- [ ] Xác định quyền sử dụng, tiêu chí chọn/loại bài và cách ẩn dữ liệu.
- [ ] Chuẩn bị answer key và bằng chứng đoạn văn trước khi xem output AI.
- [ ] Chuẩn bị danh sách từ/cụm từ và nghĩa tham chiếu theo ngữ cảnh trước
  khi xem câu trả lời Tutor.
- [ ] Hoàn thành tổng quan nghiên cứu và bảng so sánh tài nguyên hiện có.
- [ ] Kiểm tra từng tài liệu tham khảo và bảo đảm có trích dẫn trong thân bài.

## B.3. Chạy đánh giá và phân tích

- [ ] Cố định phiên bản code, prompt, model ID và cấu hình chạy.
- [ ] Thực hiện pilot nhỏ để kiểm tra biểu mẫu chấm; sau pilot khóa rubric.
- [ ] Thu thập tất cả lượt sinh và phản hồi lỗi; không chỉ lưu kết quả đẹp.
- [ ] Chấm độc lập; lưu điểm thô của từng người chấm trước hòa giải.
- [ ] Tính tử số, mẫu số, tỷ lệ và khoảng tin cậy đã thống nhất.
- [ ] Phân tích riêng RQ1, RQ2 và RQ3; không trộn chỉ số khác mẫu số.
- [ ] Phân loại lỗi và chọn ví dụ đại diện có quyền sử dụng.
- [ ] Viết thảo luận theo kết quả thật, gồm kết quả không như kỳ vọng.

## B.4. Hoàn thiện sản phẩm và bản nộp

- [ ] Sửa ba kiểm thử giao diện thất bại được ghi nhận ở Chương 6.
- [ ] Chạy lại toàn bộ test sau thay đổi và ghi môi trường, ngày, kết quả.
- [ ] Xác minh ảnh kiến trúc/luồng, số hình, caption và trích dẫn trong nội dung.
- [ ] Điền trang bìa, abstract, số trang, mục lục và danh sách hình/bảng theo
  mẫu trường.
- [ ] Xóa mọi chỉ dẫn `[CẦN BỔ SUNG]`, `[SAU KHI ĐO]` và dữ liệu mẫu khỏi bản
  nộp cuối.
- [ ] Kiểm tra đạo văn, quyền hình ảnh/văn bản, thông tin nhạy cảm và API key.
- [ ] Chuyển sang mẫu Word chính thức; kiểm tra khả năng truy cập và xuất PDF
  theo hướng dẫn trường.

# Phụ lục C. Hướng dẫn cài đặt và chạy

## C.1. Yêu cầu

- Python 3.10 trở lên.
- Khóa API Groq cho các chức năng AI.
- Kết nối Internet khi gọi Groq hoặc tra bản dịch MyMemory chưa có trong
  cache.

## C.2. Cài đặt trên Windows PowerShell

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## C.3. Cài đặt trên macOS hoặc Linux

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## C.4. Cấu hình và khởi chạy

Tạo file `.env` ở thư mục gốc:

```dotenv
GROQ_API_KEY=your_groq_api_key
```

Không chia sẻ khóa API hoặc commit file `.env`. Khởi chạy ứng dụng bằng:

```bash
python -m streamlit run app.py
```

Ứng dụng sử dụng `data/yki.db`; hãy sao lưu file này nếu cần giữ dữ liệu.

# Phụ lục D. Kiểm thử

Chạy toàn bộ kiểm thử:

```bash
python -m pytest -q
```

Chạy kiểm thử và báo cáo coverage:

```bash
python -m pytest -q --cov=ai --cov=services --cov=repositories --cov=models --cov=database --cov=views --cov=app --cov-report=term-missing
```

# Phụ lục E. Cấu trúc mã nguồn

```text
.
├── ai/              # Tích hợp model và chức năng AI
├── data/            # Cơ sở dữ liệu SQLite
├── database/        # Kết nối và khởi tạo cơ sở dữ liệu
├── docs/            # Sơ đồ và tài liệu bổ sung
├── models/          # Mô hình dữ liệu
├── repositories/    # Truy cập dữ liệu
├── services/        # Xử lý nghiệp vụ
├── tests/           # Kiểm thử tự động
├── views/           # Giao diện Streamlit
├── app.py           # Điểm khởi chạy
└── requirements.txt # Dependencies Python
```
