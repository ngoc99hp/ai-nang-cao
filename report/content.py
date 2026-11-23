"""Nội dung báo cáo BTL (dùng bởi report/build.py). Số liệu lấy từ results/tables/ (2026-11-23)."""
from build import Doc

COVER = {
    8: 'HỌC PHẦN “TRÍ TUỆ NHÂN TẠO NÂNG CAO”',
    11: 'Tự động phân loại và cụm hóa các quan niệm sai lầm (Misconceptions Clustering) của sinh viên '
        'thông qua khai phá cấu trúc bài làm sai',
    21: 'Hải Phòng, tháng 11 năm 2026',
}

ABBREV = [
    ['AST', 'Abstract Syntax Tree', 'Cây cú pháp trừu tượng'],
    ['OAV', 'Object – Attribute – Value', 'Bộ ba Đối tượng – Thuộc tính – Giá trị'],
    ['ILA', 'Inductive Learning Algorithm', 'Thuật toán học quy nạp sinh luật'],
    ['ID3', 'Iterative Dichotomiser 3', 'Thuật toán cây quyết định dựa trên entropy'],
    ['ARI', 'Adjusted Rand Index', 'Chỉ số Rand hiệu chỉnh'],
    ['NMI', 'Normalized Mutual Information', 'Thông tin tương hỗ chuẩn hóa'],
    ['DB', 'Davies–Bouldin index', 'Chỉ số Davies–Bouldin'],
    ['MDS', 'Multidimensional Scaling', 'Phép chiếu đa chiều'],
    ['APR', 'Automated Program Repair', 'Sửa lỗi chương trình tự động'],
    ['UB', 'Undefined Behavior', 'Hành vi không xác định (ngôn ngữ C)'],
    ['LOPO', 'Leave-One-Problem-Out', 'Đánh giá chéo bỏ ra một bài tập'],
    ['GV', '—', 'Giảng viên'],
    ['SV', '—', 'Sinh viên'],
    ['T / O / A / D', 'Test / Output / AST / Diff', 'Bốn nhóm thuộc tính OAV của đề tài'],
    ['M1–M8', '—', 'Mã 8 loại quan niệm sai lầm trong taxonomy của đề tài'],
]

PN = {'digits': 'digits', 'grade': 'grade', 'median': 'median', 'smallest': 'smallest', 'average': 'average'}


def make():
    D = Doc()

    # =================================================================================== MỞ ĐẦU
    D.h1('PHẦN MỞ ĐẦU', chap='0')
    D.h2('1. Giới thiệu đề tài')
    D.p('Trong các lớp lập trình nhập môn quy mô lớn, mỗi bài tập có thể nhận hàng trăm bài nộp, phần lớn trong số đó '
        'chưa đúng. Các hệ thống chấm tự động hiện nay trả lời rất tốt câu hỏi “bài này đúng hay sai, trượt test nào”, '
        'nhưng giảng viên thường cần một câu trả lời ở mức cao hơn: **sinh viên đang hiểu sai điều gì, và bao nhiêu '
        'người cùng hiểu sai như vậy**. Thông tin này cho phép giảng viên điều chỉnh bài giảng cho cả lớp – còn gọi là '
        'phản hồi vĩ mô (*macro-feedback*) – thay vì sửa từng bài một.')
    D.p('Một quan niệm sai lầm (*misconception*) là một cách hiểu không đúng nhưng nhất quán về một khái niệm lập trình, '
        'ví dụ cho rằng phép so sánh `<` đã đủ để tìm số nhỏ nhất mà không cần quan tâm trường hợp các số bằng nhau, '
        'hay cho rằng vòng lặp `while (n)` xử lý được cả trường hợp n = 0. Nhiều bài làm trông rất khác nhau về mặt '
        'mã nguồn lại cùng xuất phát từ một quan niệm sai lầm; ngược lại, cùng một test bị trượt có thể do nhiều nguyên '
        'nhân khác nhau. Vì vậy, việc gom nhóm theo kết quả test thuần túy là chưa đủ.')
    D.p('Đề tài này xây dựng một quy trình tự động: hình thức hóa mỗi bài làm sai bằng các bộ ba **Đối tượng – Thuộc '
        'tính – Giá trị (OAV)** bám theo các test bị trượt và cấu trúc mã nguồn, **gom cụm phi giám sát** các bài làm '
        'có biểu hiện tương tự, rồi **quy nạp hệ luật NẾU – THÌ** bằng thuật toán ILA để giải thích từng cụm, làm cơ '
        'sở đặt tên quan niệm sai lầm và sinh bảng phản hồi vĩ mô cho giảng viên.')
    D.p('Do dữ liệu bài làm do giảng viên cung cấp không truy cập được (máy chủ gặp sự cố), nhóm tự thu thập dữ liệu từ '
        'hai bộ dữ liệu công khai là IntroClass [1] và ITSP [2], đồng thời tự sinh một bộ dữ liệu có nhãn bằng kỹ thuật '
        'đột biến chương trình để có “đáp án” phục vụ đánh giá định lượng.')
    D.h2('2. Mục tiêu nghiên cứu')
    D.p('Mục tiêu chính là xây dựng và đánh giá một quy trình đầu–cuối phát hiện và cụm hóa quan niệm sai lầm từ bài làm '
        'C sai của sinh viên. Cụ thể:')
    D.bullets([
        'Xây dựng môi trường chấm bài an toàn, tái lập được, đối chiếu kết quả chấm với dữ liệu gốc của các bộ dữ liệu.',
        'Đề xuất bộ thuộc tính OAV mô tả bài làm sai theo bốn nhóm: kết quả test, kiểu sai của output, cấu trúc cây cú '
        'pháp và khác biệt so với lời giải đúng gần nhất.',
        'Áp dụng và so sánh các thuật toán gom cụm phù hợp với dữ liệu định danh (K-modes, gom cụm phân cấp với khoảng '
        'cách Hamming có trọng số) và một mô hình đối chứng (K-means trên mã hóa one-hot).',
        'Tự cài đặt thuật toán ILA để sinh luật giải thích cụm, so sánh với cây quyết định ID3.',
        'Đánh giá định lượng trên dữ liệu cấy lỗi có nhãn, đánh giá trên dữ liệu thật, và xây dựng chương trình demo.',
    ])
    D.h2('3. Đóng góp của đề tài')
    D.bullets([
        'Một quy trình hoàn chỉnh, tái lập được: chấm bài trong container cách ly → trích xuất OAV → gom cụm → sinh '
        'luật → bảng macro-feedback, kèm 94 kiểm thử tự động.',
        'Bộ dữ liệu cấy lỗi gồm 480 bài có nhãn theo taxonomy 8 quan niệm sai lầm (M1–M8), sinh bằng phép đột biến trên '
        'cây cú pháp, đã loại các đột biến tương đương.',
        'Nhóm thuộc tính **D** (khác biệt so với lời giải đúng gần nhất) và thực nghiệm ablation cho thấy đây là nhóm '
        'quyết định chất lượng gom cụm, trong khi chỉ dùng kết quả test gần như không phân biệt được quan niệm sai lầm.',
        'Phân tích trung thực các giới hạn: thiên lệch khi chọn trọng số, độ nhạy theo bài tập, đánh giá trên ITSP với '
        'nhãn gán tay.',
        'Chương trình demo có giao diện web cho giảng viên và cho phép nộp bài mới để chẩn đoán, chạy trong sandbox đã '
        'được kiểm thử với các bài nộp độc hại.',
    ])
    D.h2('4. Cấu trúc báo cáo')
    D.p('Báo cáo gồm 6 chương. Chương 1 trình bày tổng quan bài toán và các nghiên cứu liên quan. Chương 2 trình bày cơ sở '
        'lý thuyết về biểu diễn OAV, các thuật toán gom cụm, quy nạp luật và độ đo đánh giá. Chương 3 mô tả dữ liệu, môi '
        'trường chấm bài và thiết kế thực nghiệm. Chương 4 trình bày cách hình thức hóa OAV, lựa chọn trọng số, số cụm và '
        'sinh luật. Chương 5 trình bày kết quả các thực nghiệm E1–E5 và chương trình demo. Chương 6 kết luận, nêu hạn chế '
        'và hướng phát triển.')

    # =================================================================================== CHƯƠNG 1
    D.h1('CHƯƠNG 1: TỔNG QUAN BÀI TOÁN', chap=1)
    D.h2('1.1. Quan niệm sai lầm trong lập trình nhập môn')
    D.p('Các nghiên cứu về giáo dục lập trình ghi nhận rằng người mới học thường xây dựng một “mô hình tinh thần” chưa '
        'chính xác về cách máy tính thực thi chương trình [3], [4]. Những sai lệch này mang tính hệ thống: chúng lặp lại '
        'giữa các sinh viên và giữa các bài tập. Ví dụ điển hình gồm: nhầm phép gán với phép so sánh, xác định sai điều '
        'kiện biên của vòng lặp, quên khởi tạo biến tích lũy, hiểu sai cơ chế truyền tham trị và truyền tham chiếu, hoặc '
        'không xử lý các trường hợp đặc biệt (số âm, số 0, các giá trị bằng nhau).')
    D.p('Điểm quan trọng là quan niệm sai lầm khác với lỗi ngẫu nhiên (gõ nhầm, sai chính tả trong câu thông báo). Lỗi '
        'ngẫu nhiên chỉ cần sửa cho từng bài; quan niệm sai lầm cần được giảng lại. Vì vậy hệ thống phân tích phải tách '
        'được hai loại này – ví dụ, đề tài coi lỗi định dạng output là “được ghi nhận nhưng không phải misconception”.')
    D.h2('1.2. Bài toán cụm hóa quan niệm sai lầm')
    D.p('Cho một bài tập lập trình với bộ test và tập N bài làm sai của sinh viên. Mục tiêu là phân hoạch tập bài làm '
        'thành k nhóm sao cho các bài trong cùng một nhóm có chung một quan niệm sai lầm, đồng thời sinh cho mỗi nhóm '
        'một mô tả dễ hiểu (luật) để giảng viên đặt tên và quyết định nội dung cần giảng lại. Bài toán có ba đặc điểm:')
    D.bullets([
        '**Phi giám sát**: không có nhãn quan niệm sai lầm cho dữ liệu thật; số nhóm k không biết trước.',
        '**Dữ liệu định danh**: mỗi bài được mô tả bằng các thuộc tính rời rạc (test đạt/trượt, kiểu sai, loại phép '
        'so sánh…), không phải véc-tơ số thực.',
        '**Cần giải thích được**: đầu ra phải đọc được bởi giảng viên, nên kết quả gom cụm cần đi kèm luật hoặc dấu '
        'hiệu đặc trưng.',
    ])
    D.h2('1.3. Thách thức')
    D.bullets([
        '**Đa dạng mã nguồn**: cùng một quan niệm sai lầm có thể xuất hiện trong các lời giải có cấu trúc rất khác nhau '
        '(dùng chuỗi if, dùng vòng lặp, dùng hàm…).',
        '**Triệu chứng không đặc trưng**: cùng một test bị trượt có thể do nhiều nguyên nhân; trong dữ liệu IntroClass, '
        'mỗi bài tập chỉ có 9–24 mẫu kết quả test khác nhau cho hàng chục, hàng trăm bài sai.',
        '**Nhiễu định dạng**: nhiều bài “sai” chỉ do khác chữ trong câu thông báo (ví dụ ở bài grade, 123/228 bài sai '
        'theo bộ chấm gốc thực ra chỉ sai định dạng).',
        '**Hành vi không xác định của C**: biến chưa khởi tạo làm kết quả phụ thuộc môi trường chạy.',
        '**Một bài nhiều lỗi**: một bài làm có thể mang nhiều quan niệm sai lầm cùng lúc, làm ranh giới cụm không rõ.',
        '**An toàn**: hệ thống phải biên dịch và chạy mã nguồn của người khác.',
    ])
    D.h2('1.4. Các hướng tiếp cận và nghiên cứu liên quan')
    D.p('Có thể chia các nghiên cứu liên quan thành bốn hướng:')
    D.bullets([
        '**Gom cụm theo mã nguồn**: OverCode [5] chuẩn hóa và gom các lời giải có cùng hành vi để giảng viên duyệt hàng '
        'nghìn bài; Gulwani và cộng sự [7] gom cụm các lời giải đúng theo cấu trúc điều khiển và dùng cụm để sửa bài sai '
        'tự động.',
        '**Biểu diễn học được**: Piech và cộng sự [6] học véc-tơ biểu diễn chương trình để lan truyền phản hồi của giảng '
        'viên từ một bài sang các bài tương tự.',
        '**Sửa lỗi tự động (APR)**: bộ dữ liệu IntroClass [1] và ITSP [2] được xây dựng để đánh giá các công cụ sửa lỗi '
        'tự động trên bài làm của sinh viên; Head và cộng sự [8] học các phép biến đổi sửa lỗi từ bản sửa của sinh viên '
        'để tái sử dụng phản hồi.',
        '**Phân loại theo taxonomy**: các tổng quan về quan niệm sai lầm [3] đưa ra danh mục lỗi phổ biến, thường được '
        'dùng làm nhãn cho hướng có giám sát nhưng đòi hỏi gán nhãn thủ công tốn kém.',
    ])
    D.p('Đề tài chọn hướng **biểu diễn tri thức tường minh (OAV) kết hợp gom cụm định danh và quy nạp luật**, phù hợp với '
        'nội dung học phần và ưu tiên khả năng giải thích. Khác với các hướng chỉ dùng kết quả test, đề tài bổ sung đặc '
        'trưng về khác biệt so với lời giải đúng, lấy cảm hứng từ hướng APR: “bài sai khác bài đúng ở đâu” là tín hiệu '
        'trực tiếp về điều sinh viên hiểu sai.')
    D.h2('1.5. Hướng tiếp cận của đề tài và phạm vi')
    D.p('Từ yêu cầu của đề bài, nhóm điều chỉnh hai điểm về phương pháp:')
    D.bullets([
        '**ILA là thuật toán học có giám sát** sinh luật [11], không phải thuật toán gom cụm. Do đó đề tài gom cụm trước, '
        'sau đó dùng mã cụm làm nhãn lớp để ILA sinh luật mô tả cụm.',
        '**K-means tối ưu theo khoảng cách Euclid** nên ghép với khoảng cách Hamming là không nhất quán về mặt toán học. '
        'Với dữ liệu định danh, đề tài dùng K-modes [9] và gom cụm phân cấp trên ma trận khoảng cách Hamming có trọng '
        'số; K-means trên mã hóa one-hot chỉ đóng vai trò mô hình đối chứng.',
    ])
    D.p('Phạm vi: bài làm bằng ngôn ngữ C ở mức nhập môn (rẽ nhánh, vòng lặp, số học, con trỏ cơ bản); dữ liệu thật '
        'gồm 4 bài tập của IntroClass (digits, grade, median, smallest) và 602 cặp bài sai/bản sửa của ITSP; dữ liệu cấy '
        'lỗi bổ sung các quan niệm sai lầm hiếm gặp trong dữ liệu công khai (con trỏ, chia nguyên). Báo cáo tách riêng '
        'kết quả trên dữ liệu sinh (sạch, có nhãn) và dữ liệu thật (nhiễu, không nhãn).')

    # =================================================================================== CHƯƠNG 2
    D.h1('CHƯƠNG 2: CƠ SỞ LÝ THUYẾT', chap=2)
    D.h2('2.1. Biểu diễn tri thức Đối tượng – Thuộc tính – Giá trị')
    D.p('Bộ ba OAV là một hình thức biểu diễn tri thức cổ điển: mỗi sự kiện được mô tả bằng một **đối tượng**, một '
        '**thuộc tính** của đối tượng đó và **giá trị** của thuộc tính. Ví dụ `(test wb3, trạng thái, FAIL)` hay '
        '`(điều kiện if, kiểu so sánh, chặt)`. Một bài làm sai được biểu diễn bằng tập các bộ ba như vậy.')
    D.p('Để áp dụng thuật toán, tập bộ ba được chuyển sang dạng bảng “rộng”: mỗi cặp (đối tượng, thuộc tính) là một '
        'cột, mỗi bài làm là một dòng, ô chứa giá trị định danh. Đề tài lưu song song hai dạng: dạng dài (đúng hình thức '
        'OAV, dùng cho báo cáo và giải thích) và dạng rộng (dùng cho thuật toán). Tên cột có dạng '
        '`<nhóm>:<đối tượng>.<thuộc tính>`, ví dụ `D:diff.cmp_if`.')
    D.h2('2.2. Cây cú pháp trừu tượng')
    D.p('Cây cú pháp trừu tượng (AST) biểu diễn cấu trúc ngữ pháp của chương trình dưới dạng cây: các nút là cấu trúc '
        'ngôn ngữ (câu lệnh `for`, biểu thức nhị phân, lời gọi hàm…), các cạnh thể hiện quan hệ chứa. Đề tài dùng '
        'tree-sitter [20] với văn phạm C để phân tích mã nguồn, kể cả mã có lỗi cú pháp nhẹ. Từ AST, đề tài trích xuất '
        'các thuộc tính cấu trúc (phép so sánh trong điều kiện vòng lặp, giá trị khởi tạo của biến tích lũy…), thực hiện '
        'phép đột biến theo vị trí byte của nút (Phần 2.6) và tính khác biệt giữa hai chương trình theo chuỗi token.')
    D.h2('2.3. Khoảng cách cho dữ liệu định danh')
    D.p('Với hai bài làm x và y được mô tả bởi d thuộc tính định danh, khoảng cách Hamming có trọng số là tổng trọng số '
        'của các thuộc tính mà hai bài có giá trị khác nhau, chuẩn hóa về đoạn [0, 1]:')
    D.eq('d(x, y) = Σ_{j} w_{j} · [x_{j} ≠ y_{j}] / Σ_{j} w_{j}', 'hamming')
    D.p('Do số cột ở các nhóm thuộc tính rất khác nhau (nhóm D có 24 cột, nhóm A có 13 cột), nếu dùng trọng số bằng '
        'nhau thì nhóm nhiều cột sẽ chi phối khoảng cách. Đề tài **chuẩn hóa theo nhóm**: mỗi cột j thuộc nhóm g nhận '
        'trọng số bằng trọng số của nhóm chia cho số cột của nhóm, nhờ đó mỗi nhóm đóng góp đúng bằng trọng số W_{g} '
        'được chọn, không phụ thuộc số cột:')
    D.eq('w_{j} = W_{g(j)} / |G_{g(j)}|', 'wnorm')
    D.h2('2.4. Các thuật toán gom cụm')
    D.h3('2.4.1. K-modes')
    D.p('K-modes [9] mở rộng K-means cho dữ liệu định danh: thay trung bình bằng **mode** (giá trị xuất hiện nhiều nhất '
        'theo từng thuộc tính) và thay khoảng cách Euclid bằng khoảng cách sai khác. Thuật toán cực tiểu hóa:')
    D.eq('J = Σ_{c=1..k} Σ_{x ∈ Cc} d(x, m_{c})', 'kmodes')
    D.p('trong đó Cc là tập bài thuộc cụm c và m_{c} là mode của cụm c. Mỗi vòng lặp gồm hai bước: gán mỗi bài về cụm có mode gần nhất, rồi cập nhật '
        'mode của từng cụm. Đề tài dùng khoảng cách Hamming có trọng số (công thức ({E:hamming})) làm hàm sai khác, khởi '
        'tạo theo phương pháp của Cao và cộng sự [10] (chọn tâm theo mật độ và độ khác biệt), chạy 5 lần khởi tạo và '
        'giữ nghiệm có J nhỏ nhất.')
    D.h3('2.4.2. Gom cụm phân cấp')
    D.p('Gom cụm phân cấp gộp (agglomerative) bắt đầu với mỗi bài là một cụm, lần lượt gộp hai cụm gần nhau nhất cho '
        'tới khi còn k cụm. Với liên kết trung bình (average linkage) [21], khoảng cách giữa hai cụm A, B là trung bình '
        'khoảng cách giữa mọi cặp phần tử:')
    D.eq('d(A, B) = (1 / |A||B|) · Σ_{x∈A} Σ_{y∈B} d(x, y)')
    D.p('Thuật toán nhận trực tiếp ma trận khoảng cách tính sẵn nên dùng được với khoảng cách Hamming có trọng số, và '
        'cho cây phân cấp (dendrogram) thể hiện quan hệ cha–con giữa các nhóm lỗi.')
    D.h3('2.4.3. K-means trên mã hóa one-hot')
    D.p('K-means [22] cực tiểu tổng bình phương khoảng cách Euclid tới tâm cụm. Để áp dụng cho dữ liệu định danh, mỗi '
        'thuộc tính được mã hóa one-hot và nhân với căn bậc hai trọng số cột, khi đó bình phương khoảng cách Euclid tỷ '
        'lệ với khoảng cách Hamming có trọng số giữa hai điểm dữ liệu. Tuy nhiên tâm cụm là véc-tơ số thực không ứng với '
        'bài làm nào, nên phương pháp này chỉ được dùng làm đối chứng.')
    D.h2('2.5. Quy nạp luật')
    D.h3('2.5.1. Thuật toán ILA')
    D.p('ILA (Inductive Learning Algorithm) [11] sinh tập luật NẾU–THÌ từ bảng ví dụ có thuộc tính rời rạc và nhãn lớp. '
        'Với mỗi lớp, thuật toán tìm các tổ hợp giá trị thuộc tính **chỉ xuất hiện trong lớp đó**, ưu tiên tổ hợp ngắn '
        'và phủ nhiều ví dụ nhất. Các bước:')
    D.bullets([
        'Chia bảng ví dụ thành các bảng con theo lớp.',
        'Với mỗi lớp, xét số thuộc tính j = 1, 2, …: duyệt mọi tổ hợp j thuộc tính; tìm tổ hợp giá trị xuất hiện ở '
        'các dòng **chưa được đánh dấu** của lớp đang xét nhưng **không xuất hiện** ở bất kỳ dòng nào của lớp khác; '
        'chọn tổ hợp xuất hiện nhiều nhất.',
        'Sinh luật “NẾU tổ hợp đó THÌ lớp đang xét”, đánh dấu các dòng được luật phủ; lặp lại với cùng j cho tới khi '
        'không còn tổ hợp thỏa mãn, sau đó tăng j.',
        'Dừng khi mọi dòng của lớp đã được đánh dấu (hoặc j vượt ngưỡng tối đa, đề tài đặt 3).',
    ])
    D.p('Theo cấu tạo, mọi luật của ILA nhất quán 100% trên tập huấn luyện. Đề tài tự cài đặt ILA và kiểm chứng trên '
        'bộ ví dụ “phân loại vật thể” trong bài báo gốc: thuật toán sinh đúng 5 luật như bài báo công bố. Mỗi luật được '
        'báo cáo kèm **độ phủ** (số dòng của lớp khớp luật / số dòng của lớp) và **độ chính xác**.')
    D.h3('2.5.2. Cây quyết định ID3')
    D.p('ID3 [12] xây dựng cây quyết định bằng cách chọn tại mỗi nút thuộc tính có độ lợi thông tin lớn nhất. Với tập S '
        'có tỷ lệ lớp p_{c}:')
    D.eq('H(S) = − Σ_{c} p_{c} · log_{2} p_{c}')
    D.eq('IG(S, A) = H(S) − Σ_{v ∈ A} (|S_{v}| / |S|) · H(S_{v})')
    D.p('Mỗi đường đi từ gốc tới lá tương ứng với một luật. ID3 được dùng làm mốc so sánh độ dài và độ chính xác của '
        'luật với ILA.')
    D.h2('2.6. Đột biến chương trình và dữ liệu có nhãn')
    D.p('Kiểm thử đột biến (mutation testing) [17] tạo ra các phiên bản lỗi của chương trình bằng những thay đổi nhỏ có '
        'chủ đích (đổi toán tử, xóa câu lệnh…). Đề tài dùng ý tưởng này theo hướng ngược lại: mỗi **toán tử đột biến** '
        'được thiết kế để mô phỏng **một quan niệm sai lầm** cụ thể (ví dụ đổi `<=` thành `<` trong điều kiện vòng lặp '
        'mô phỏng sai biên vòng lặp). Cấy đột biến vào lời giải đúng cho ra bài làm sai có nhãn quan niệm sai lầm biết '
        'trước, dùng làm “đáp án” để đo chất lượng gom cụm. Một đột biến là **tương đương** nếu không làm thay đổi hành '
        'vi chương trình; các đột biến này phải được loại bỏ.')
    D.h2('2.7. Các độ đo đánh giá')
    D.p('**Chỉ số Rand hiệu chỉnh (ARI)** [13] đo mức trùng khớp giữa phân hoạch tìm được và phân hoạch đúng. Chỉ số '
        'Rand (RI) là tỷ lệ cặp phần tử được hai phân hoạch xử lý nhất quán (cùng cụm ở cả hai, hoặc khác cụm ở cả '
        'hai); ARI hiệu chỉnh RI theo giá trị kỳ vọng khi phân hoạch ngẫu nhiên, nên ARI = 1 khi trùng hoàn toàn và '
        'xấp xỉ 0 khi không hơn ngẫu nhiên:')
    D.eq('ARI = (RI − E[RI]) / (max RI − E[RI])', 'ari')
    D.p('**Thông tin tương hỗ chuẩn hóa (NMI)** [14] đo lượng thông tin chung giữa hai phân hoạch U và V:')
    D.eq('NMI(U, V) = I(U; V) / √(H(U) · H(V))')
    D.p('**Độ thuần (Purity)**: với mỗi cụm, đếm số phần tử thuộc nhãn chiếm đa số, cộng lại và chia cho N. Độ đo này '
        'dễ hiểu nhưng tăng theo số cụm, nên chỉ dùng bổ sung.')
    D.eq('Purity = (1/N) · Σ_{c} max_{l} |C_{c} ∩ L_{l}|')
    D.p('Với dữ liệu thật không có nhãn, đề tài dùng các độ đo nội tại. **Silhouette** [15] của một điểm i so sánh '
        'khoảng cách trung bình a(i) tới các điểm cùng cụm với khoảng cách trung bình nhỏ nhất b(i) tới một cụm khác; '
        'giá trị thuộc [−1, 1], càng cao càng tách bạch:')
    D.eq('s(i) = (b(i) − a(i)) / max(a(i), b(i))')
    D.p('**Chỉ số Davies–Bouldin** [16] là trung bình, trên các cụm, của tỷ số giữa tổng độ phân tán trong hai cụm và '
        'khoảng cách giữa chúng (lấy cặp xấu nhất); giá trị càng nhỏ càng tốt.')

    # =================================================================================== CHƯƠNG 3
    D.h1('CHƯƠNG 3: DỮ LIỆU VÀ THIẾT KẾ THỰC NGHIỆM', chap=3)
    D.h2('3.1. Quy trình tổng thể')
    D.p('Hình {F:pipeline} tóm tắt quy trình. Ba nguồn dữ liệu (IntroClass, bài cấy lỗi, ITSP) được chấm trong môi '
        'trường cách ly; bài sai được hình thức hóa thành bộ ba OAV, gom cụm theo khoảng cách Hamming có trọng số, sinh '
        'luật bằng ILA và tổng hợp thành bảng phản hồi vĩ mô. Mỗi bước là một script độc lập, ghi kết quả trung gian '
        'dạng Parquet có kiểm tra lược đồ, cho phép chạy lại từng bước.')
    D.figure('results/figures/pipeline.png', 'Quy trình tổng thể của đề tài', 16, label='pipeline')
    D.h2('3.2. Môi trường chấm bài an toàn')
    D.p('Hệ thống phải biên dịch và chạy mã nguồn C của người khác (bài sinh viên, bài đột biến), trên một máy chủ dùng '
        'chung với dịch vụ thật. Vì vậy mọi thao tác biên dịch/chạy được thực hiện trong container Docker có nhiều lớp '
        'bảo vệ (Bảng {T:sandbox}), và mỗi lần chạy đều đi qua một mô-đun chấm duy nhất có giới hạn tài nguyên theo '
        'tiến trình.')
    D.table(['Biện pháp', 'Mục đích'], [
        ['Không có mạng (network_mode: none)', 'Mã lạ không truy cập được mạng hay các dịch vụ khác trên máy chủ'],
        ['User không đặc quyền, bỏ mọi capability, no-new-privileges', 'Không leo thang quyền trong container'],
        ['Giới hạn 1,5 CPU, 3 GB RAM, 512 tiến trình', 'Không ảnh hưởng dịch vụ dùng chung; chặn fork bomb'],
        ['Dữ liệu gốc gắn chỉ đọc', 'Không thể sửa bộ dữ liệu gốc'],
        ['ulimit theo tiến trình: 2 s CPU, 256 MB, 1 MB output', 'Phân loại TIMEOUT / CRASH / OUTPUT_LIMIT'],
        ['Timeout theo thời gian CPU, wall-clock = 3× làm lưới an toàn',
         'Tránh TIMEOUT oan cho bài đúng khi chạy song song cùng bài lặp vô hạn'],
        ['Diệt cả nhóm tiến trình sau mỗi lần chạy', 'Không sót tiến trình con / fork bomb'],
    ], [4, 5], 'Các lớp bảo vệ của môi trường chấm bài', label='sandbox')
    D.p('Bộ chấm trả về một trong sáu trạng thái: PASS, FAIL, TIMEOUT, CRASH, OUTPUT_LIMIT, COMPILE_ERROR. Mã thoát '
        'khác 0 không bị coi là lỗi (các bài C cũ thường thiếu `return 0;`), chỉ tín hiệu kết thúc bất thường mới là '
        'CRASH. Việc song song hóa được thực hiện ở mức (bài × test) để cân bằng tải.')
    D.h2('3.3. Bộ dữ liệu IntroClass')
    D.h3('3.3.1. Nguồn dữ liệu')
    D.p('IntroClass [1] gồm 1.143 phiên bản bài làm C của 259 lượt sinh viên (mỗi “repo” là một sinh viên, mỗi phiên bản '
        'là một lần nộp) cho 6 bài tập nhập môn của Đại học California, Davis, kèm bộ test hộp đen và hộp trắng '
        '(Bảng {T:introclass}). Mỗi phiên bản có siêu dữ liệu ghi kết quả đạt/trượt từng test do nhóm tác giả đo.')
    D.table(['Bài tập', 'Nội dung', 'Test hộp đen', 'Test hộp trắng', 'Số SV', 'Phiên bản'], [
        ['checksum', 'Tính ký tự kiểm tra của chuỗi', '6', '10', '21', '69'],
        ['digits', 'In các chữ số từ hàng đơn vị', '6', '10', '55', '236'],
        ['grade', 'Xếp loại điểm theo 4 ngưỡng', '9', '9', '50', '268'],
        ['median', 'Số trung vị của 3 số', '7', '6', '44', '232'],
        ['smallest', 'Số nhỏ nhất của 4 số', '8', '8', '45', '177'],
        ['syllables', 'Đếm nguyên âm trong chuỗi', '6', '10', '44', '161'],
        ['Tổng', '', '', '', '259', '1.143'],
    ], [1.6, 3.6, 1.3, 1.3, 1, 1.2], 'Thống kê bộ dữ liệu IntroClass', label='introclass',
        align=[None, None, 'c', 'c', 'r', 'r'], bold_last=True)
    D.h3('3.3.2. Cách chấm và kiểm định bộ chấm')
    D.p('Bộ chấm gốc của IntroClass trích đáp án bằng biểu thức chính quy riêng cho từng bài và bỏ qua câu nhắc nhập, '
        'nhưng vẫn đánh trượt các bài sai chính tả trong câu kết quả (ví dụ “Studetn has an C grade”) và có một số lỗi '
        '(ở bài smallest, phép kiểm tra phủ định tìm nhầm trong input thay vì output). Đề tài chấm theo **hai chế độ**: '
        '**strict** – mô phỏng nguyên văn bộ chấm gốc, dùng để kiểm định; và **semantic** – trích đáp án linh hoạt, sửa '
        'các lỗi của bộ chấm gốc, dùng cho gom cụm. Bài chỉ sai ở chế độ strict được gắn cờ “chỉ sai định dạng”, được ghi '
        'nhận như một thuộc tính nhưng không được coi là quan niệm sai lầm.')
    D.p('Kiểm định lần đầu cho thấy bài smallest chỉ khớp 90,4% với siêu dữ liệu. Phân tích chỉ ra hai nguyên nhân: (1) '
        'giả định “mã thoát khác 0 thì trượt” là sai – siêu dữ liệu ghi đạt cho cả 90/90 test có mã thoát khác 0 và '
        'output đúng; (2) **biến chưa khởi tạo**: biên dịch mỗi bài hai lần, lần lượt khởi tạo mọi biến cục bộ bằng 0 và '
        'bằng mẫu khác 0, cho thấy 79/1.143 phiên bản có kết quả phụ thuộc giá trị rác. Bản biên dịch khởi tạo bằng 0 '
        'khớp siêu dữ liệu gần tuyệt đối, chứng tỏ môi trường gốc năm 2014 cũng cho giá trị 0. Đề tài giữ các phiên bản '
        'này, gắn cờ `uninit_dependent` (bản thân việc dùng biến chưa khởi tạo cũng là một quan niệm sai lầm) và biên '
        'dịch với `-ftrivial-auto-var-init=zero` để tái lập. Kết quả kiểm định sau cùng ở Bảng {T:validation}.')
    D.table(['Bài tập', 'Số test (deterministic)', 'Tỷ lệ khớp', 'Số test lệch', 'Phiên bản phụ thuộc UB'], [
        ['checksum', '624', '100%', '0', '4'],
        ['digits', '3.392', '100%', '0', '5'],
        ['grade', '3.582', '100%', '0', '2'],
        ['median', '2.652', '99,81%', '5', '26'],
        ['smallest', '2.640', '99,81%', '5', '33'],
        ['syllables', '1.168', '98,20%', '21', '11'],
    ], [1.5, 2, 1.4, 1.4, 2], 'Kiểm định bộ chấm với siêu dữ liệu IntroClass (chế độ strict)', label='validation',
        align=[None, 'r', 'r', 'r', 'r'])
    D.p('31 test lệch còn lại đều có dạng siêu dữ liệu ghi trượt nhưng bộ chấm ghi đạt, trong khi output của bài trùng '
        'với output mà chính siêu dữ liệu đã ghi nhận – tức là nhiễu nhãn của bộ dữ liệu. Tiêu chí ≥ 95% được đáp ứng '
        'ở cả 6 bài.')
    D.h3('3.3.3. Lọc, khử trùng và chọn bài tập')
    D.p('Bài sai được giữ lại nếu biên dịch được và trượt ít nhất một test ở chế độ semantic. Các phiên bản trùng lặp '
        '(một sinh viên nộp lại cùng một mã chỉ khác định dạng/chú thích) được khử bằng băm chuỗi token của tree-sitter '
        '(bỏ chú thích và khoảng trắng); số bài còn lại xấp xỉ số lỗi duy nhất mà bộ dữ liệu công bố. Bảng {T:stats} cho '
        'thấy kết quả từng bước lọc.')
    D.table(['Bài tập', 'Phiên bản', 'Sai (strict)', 'Sai (semantic)', 'Chỉ sai định dạng', 'Giữ lại', 'SV',
             'Phụ thuộc UB'], [
        ['checksum', '69', '52', '52', '0', '29', '21', '2'],
        ['digits', '236', '204', '196', '8', '108', '54', '3'],
        ['grade', '268', '228', '105', '123', '38', '22', '1'],
        ['median', '232', '203', '203', '1', '69', '44', '9'],
        ['smallest', '177', '163', '155', '8', '64', '42', '12'],
        ['syllables', '161', '123', '123', '0', '38', '28', '6'],
    ], [1.5, 1.2, 1.2, 1.3, 1.4, 1.1, 0.8, 1.2], 'Số bài sai sau từng bước lọc', label='stats',
        align=[None] + ['r'] * 7)
    D.p('Nhận xét: ở bài grade, 123/228 bài sai theo bộ chấm gốc thực ra chỉ sai định dạng (ví dụ in “F grade” thay vì '
        '“failed the course” vẫn bị coi là sai nội dung, nhưng “Stdent has…” thì chỉ là lỗi chính tả); chế độ semantic '
        'loại được lượng nhiễu lớn này. Nhóm chọn **4 bài trọng tâm: digits, grade, median, smallest** (tổng 279 bài sai '
        'duy nhất của 162 lượt sinh viên); bỏ checksum (quá ít bài) và syllables (phần lớn phụ thuộc giá trị không xác '
        'định). Khi gom cụm, mọi phiên bản duy nhất đều được giữ; khi lập bảng phản hồi vĩ mô, đề tài đếm **số sinh viên '
        'khác nhau** trong mỗi cụm.')
    D.h2('3.4. Dữ liệu cấy lỗi có nhãn')
    D.p('Dữ liệu công khai chủ yếu là bài tập rẽ nhánh và số học, gần như không có quan niệm sai lầm về con trỏ hay chia '
        'nguyên. Để có dữ liệu có nhãn và bao phủ các quan niệm này, nhóm xây dựng taxonomy 8 quan niệm sai lầm '
        '(Bảng {T:taxonomy}) cùng các toán tử đột biến tương ứng.')
    D.table(['Mã', 'Quan niệm sai lầm', 'Toán tử đột biến'], [
        ['M1', 'Điều kiện biên vòng lặp', '`<` ↔ `<=` ở điều kiện vòng lặp; `i = 0` → `i = 1`'],
        ['M2', 'Truyền tham trị và tham chiếu', 'Bỏ `*` ở tham số và `&` ở lời gọi hàm'],
        ['M3', 'Nhầm phép gán và phép so sánh', '`==` → `=` trong điều kiện'],
        ['M4', 'Chia nguyên', 'Bỏ ép kiểu `(float)` trong phép chia'],
        ['M5', 'Khởi tạo biến tích lũy', 'Bỏ `sum = 0`; `max = a[0]` → `max = 0`'],
        ['M6', 'Phạm vi return/break', 'Đưa `return`/`break` vào trong vòng lặp'],
        ['M7', 'Biên so sánh trong chuỗi if', '`>` ↔ `>=`, `<` ↔ `<=` trong điều kiện if'],
        ['M8', 'Số âm với `%` và `/`', 'Bỏ `abs()`, bỏ lệnh đổi dấu, bỏ dấu `−` khi in'],
    ], [0.8, 3, 4.6], 'Taxonomy quan niệm sai lầm và toán tử đột biến', label='taxonomy')
    D.p('Phép đột biến được thực hiện bằng cách sửa mã nguồn theo vị trí byte của nút trên cây cú pháp (không dùng biểu '
        'thức chính quy), đảm bảo chỉ thay đổi đúng cấu trúc mong muốn. Lời giải gốc gồm các phiên bản IntroClass đạt '
        'toàn bộ test và **19 lời giải do nhóm tự viết** (dùng vòng lặp, mảng, hàm và con trỏ, cùng một bài phụ '
        '“average” có bộ test riêng cho M4). Một đột biến được giữ nếu: (1) biên dịch được, (2) trượt ít nhất một test, '
        '(3) có hành vi khác bản gốc (loại đột biến tương đương). Khoảng 15% bài kết hợp hai lỗi (nhãn dạng `M1+M6`). '
        'Kết quả ở Bảng {T:mutants}.')
    D.table(['Bài tập', 'M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7', 'M8', 'Kép', 'Tổng'], [
        ['digits', '24', '5', '50', '0', '4', '50', '29', '48', '37', '247'],
        ['grade', '4', '2', '8', '0', '0', '3', '50', '0', '12', '79'],
        ['median', '16', '12', '13', '0', '4', '17', '5', '3', '12', '82'],
        ['smallest', '9', '9', '1', '0', '6', '18', '0', '0', '8', '51'],
        ['average', '5', '2', '0', '3', '3', '5', '0', '0', '3', '21'],
        ['Tổng', '58', '30', '72', '3', '17', '93', '84', '51', '72', '480'],
    ], [1.6] + [0.75] * 9 + [0.9], 'Số bài cấy lỗi được chọn theo bài tập và quan niệm sai lầm', label='mutants',
        align=[None] + ['r'] * 10, bold_last=True)
    D.p('Tỷ lệ đột biến hợp lệ thấp nhất ở M7 (27%): ở median và smallest, **mọi** đột biến `>` ↔ `>=` đều tương đương, '
        'vì khi hai giá trị bằng nhau, chọn bên nào cũng cho cùng kết quả. Phát hiện này cho thấy bước loại đột biến '
        'tương đương là cần thiết; nó cũng giải thích vì sao quan niệm sai lầm “so sánh chặt” ở dữ liệu thật biểu hiện '
        'qua cấu trúc điều kiện khác (Chương 5) chứ không đơn giản là một phép đổi toán tử.')
    D.h2('3.5. Bộ dữ liệu ITSP')
    D.p('ITSP [2] gồm 661 bài làm sai của sinh viên Học viện Công nghệ Ấn Độ Kanpur cho 74 bài tập thuộc 10 buổi thực '
        'hành, mỗi bài sai kèm **bản sửa đúng của chính sinh viên đó**. Phần đầu mỗi tệp còn ghi kết quả chấm của hệ '
        'thống gốc cho từng test, cho phép kiểm định bộ chấm: tỷ lệ khớp đạt 95,7% trên 8.721 test. Phần lớn sai lệch '
        'tập trung ở vài bài có hành vi không xác định phụ thuộc nền tảng (chuỗi thiếu ký tự kết thúc, tràn kiểu `char`, '
        'truy cập ngoài mảng). Sau khi giữ các cặp mà bản đúng đạt toàn bộ test và bản sai trượt ít nhất một test, còn '
        '**602 cặp thuộc 72 bài tập**. Vì mỗi bài tập chỉ có khoảng 9 cặp, ITSP được dùng để đánh giá gộp nhiều bài tập '
        '(Phần 5.5).')
    D.h2('3.6. Thiết kế thực nghiệm')
    D.table(['Mã', 'Mục tiêu', 'Dữ liệu', 'Độ đo'], [
        ['E1', 'Khôi phục quan niệm sai lầm đã cấy', 'Cấy lỗi', 'ARI, NMI, Purity'],
        ['E2', 'So sánh phương pháp gom cụm', 'Cấy lỗi', 'K-modes, Agglomerative, K-means one-hot'],
        ['E3', 'Ablation nhóm thuộc tính', 'Cấy lỗi', 'ARI theo tổ hợp T, O, A, D'],
        ['E1b', 'Độ nhạy của trọng số (LOPO)', 'Cấy lỗi', 'ARI khi chọn trọng số trên các bài còn lại'],
        ['E4', 'Áp dụng lên dữ liệu thật', 'IntroClass', 'Silhouette, Davies–Bouldin, phân tích định tính'],
        ['E4b', 'Đối chiếu nhãn gán tay', 'ITSP', 'ARI, NMI, Purity trên mẫu có nhãn'],
        ['E5', 'Chất lượng luật', 'Cả hai', 'Số luật, số điều kiện/luật, độ chính xác kiểm định chéo; ILA vs ID3'],
    ], [0.7, 3.2, 1.4, 3.8], 'Thiết kế các thực nghiệm', label='experiments')
    D.p('Gom cụm được thực hiện **riêng cho từng bài tập** và **tách riêng** dữ liệu sinh và dữ liệu thật. Trên dữ liệu '
        'sinh, số cụm k bằng số nhãn đơn của bài tập đó. Hạt giống ngẫu nhiên cố định (42) để tái lập kết quả.')
    D.h2('3.7. Môi trường và công nghệ')
    D.table(['Thành phần', 'Công nghệ / Cấu hình'], [
        ['Máy chủ', 'Ubuntu 24.04, 2 nhân CPU, 7,8 GB RAM, không GPU; dùng chung với dịch vụ khác'],
        ['Cách ly', 'Docker: container nghiên cứu, container sandbox chấm bài demo, container giao diện'],
        ['Biên dịch', 'gcc 13, cờ `-O0 -w -std=gnu99 -ftrivial-auto-var-init=zero -lm`'],
        ['Ngôn ngữ', 'Python 3.12'],
        ['Phân tích mã', 'tree-sitter 0.26.1 + tree-sitter-c 0.24.2 (duyệt cây đệ quy)'],
        ['Gom cụm, độ đo', 'kmodes 0.12.2, scikit-learn 1.6.1, SciPy 1.16.3'],
        ['Dữ liệu', 'pandas 2.2.3, pyarrow 23.0.1 (Parquet có kiểm tra lược đồ)'],
        ['Trực quan, demo', 'matplotlib 3.10.1, Streamlit 1.41.1'],
        ['Kiểm thử', 'pytest – 94 kiểm thử tự động'],
    ], [2, 6], 'Môi trường và công nghệ', label='env')

    # =================================================================================== CHƯƠNG 4
    D.h1('CHƯƠNG 4: HÌNH THỨC HÓA OAV VÀ GOM CỤM', chap=4)
    D.h2('4.1. Các nhóm thuộc tính')
    D.p('Mỗi bài làm sai được mô tả bằng bốn nhóm thuộc tính (Bảng {T:groups}). Mọi giá trị đều là định danh; thuộc tính '
        'đúng/sai ghi T/F. Các thuộc tính chỉ phản ánh phong cách lập trình (số vòng lặp, số câu if, số hàm tự định '
        'nghĩa) được loại bỏ sau khi phân tích ở Phần 4.3.')
    D.table(['Nhóm', 'Đối tượng.Thuộc tính (ví dụ)', 'Giá trị', 'Số cột'], [
        ['T – Test', '`wb3.status`, `bb5.status`', 'PASS, FAIL, TIMEOUT, CRASH, OUTPUT_LIMIT', '13–18'],
        ['O – Kiểu sai output', '`output.off_by_one`, `output.sign_error`, `output.missing_answer`, '
         '`tests_tie.fail`, `tests.fail_frac`', 'T/F; none/some/all; low/mid/high/all', '13–16'],
        ['A – Cấu trúc AST', '`condition.if_cmp`, `loop.cmp_op`, `loop.return_in_loop`, `extremum.init`, '
         '`function.has_ptr_param`, `division.int_div_float_ctx`', 'strict/nonstrict/mixed; T/F; zero/literal/expr',
         '13'],
        ['D – Khác bản đúng', '`diff.cmp_if`, `diff.cmp_loop`, `diff.cmp_kind`, `diff.var_changed`, '
         '`diff.missing_output`, `diff.stmt_missing`, `diff.size`', 'T/F; strictness/reversed/mixed; 1/2-5/6-20/21+',
         '24'],
    ], [1.6, 4, 2.6, 0.8], 'Bốn nhóm thuộc tính OAV', label='groups', align=[None, None, None, 'c'])
    D.p('Nhóm **O** so đáp án trích từ output với đáp án đúng trên các test bị trượt để xác định kiểu sai (lệch 1 đơn '
        'vị, sai dấu, in một số có trong input nhưng không phải đáp án, thiếu chữ số cuối, xếp loại lệch một bậc…), '
        'đồng thời gom các test theo tính chất của input (có các số bằng nhau, có số âm, có số 0, input đã sắp xếp, điểm '
        'đúng bằng ngưỡng…) và ghi nhận bài trượt không / một số / tất cả các test thuộc từng loại. Ngoài ra nhóm O trên '
        'dữ liệu thật có các cờ: chỉ sai định dạng, phụ thuộc biến chưa khởi tạo, kết quả không ổn định.')
    D.h2('4.2. Ví dụ bộ ba OAV của một bài làm thật')
    D.p('Bài `ic_smallest_90a14c1ac8f5_001` (bài đại diện của cụm lớn nhất ở bài smallest) dùng chuỗi if với phép so '
        'sánh chặt, ví dụ:')
    D.code('if (a < b && a < c && a < d)\n    printf("%d is the smallest\\n", a);\nelse if (b < a && b < c && b < d)\n'
           '    ...')
    D.p('Bài trượt 9/16 test, đều là các test có hai số nhỏ nhất bằng nhau (khi đó không nhánh nào thỏa mãn và chương '
        'trình không in gì). Bảng {T:oavex} liệt kê các bộ ba khác giá trị mặc định của bài này.')
    D.table(['Nhóm', 'Đối tượng', 'Thuộc tính', 'Giá trị'], [
        ['T', 'bb5, bb6, wb1–wb5, wb7', 'status', 'FAIL (các test còn lại: PASS)'],
        ['O', 'output', 'missing_answer', 'T'],
        ['O', 'tests_tie', 'fail', 'some'],
        ['O', 'tests_sorted', 'fail', 'some'],
        ['O', 'tests_zero', 'fail', 'some'],
        ['O', 'tests', 'fail_frac', 'mid'],
        ['A', 'condition', 'if_cmp', 'strict'],
        ['D', 'diff', 'cmp_if', 'T'],
        ['D', 'diff', 'cmp_kind', 'strictness'],
        ['D', 'diff', 'var_changed', 'T'],
        ['D', 'diff', 'size', '21+'],
    ], [1, 3, 2.4, 3], 'Các bộ ba OAV của bài ic_smallest_90a14c1ac8f5_001', label='oavex')
    D.p('Đọc theo dạng OAV, bài này “không in ra đáp án” ở “một số test có các số bằng nhau”, “các điều kiện if chỉ dùng '
        'so sánh chặt”, và so với bản đúng gần nhất thì “đổi phép so sánh trong if theo kiểu chặt ↔ không chặt” – đúng '
        'là biểu hiện của quan niệm sai lầm M7.')
    D.h2('4.3. Chẩn đoán ban đầu và nhóm thuộc tính D')
    D.p('Lần gom cụm đầu tiên chỉ dùng ba nhóm T, O, A cho kết quả kém trên dữ liệu cấy lỗi: ARI chỉ 0,11–0,15 ở digits, '
        'median, smallest và average. Phân tích chẩn đoán chỉ ra hai nguyên nhân:')
    D.bullets([
        'Nhóm **A gom theo chương trình gốc** chứ không theo quan niệm sai lầm: ARI giữa cụm và chương trình gốc (bài '
        'đúng được đem đột biến) đạt 0,47–0,64, cao hơn nhiều so với ARI theo nhãn. Hai đột biến khác loại trên cùng một '
        'chương trình gốc có cấu trúc AST gần như giống hệt nhau.',
        '**Cùng một quan niệm sai lầm biểu hiện khác nhau** tùy chương trình gốc, nên T và O riêng lẻ chỉ đạt ARI '
        '0,06–0,25.',
    ])
    D.p('Từ đó, đề tài bổ sung nhóm **D**: so sánh bài sai với **bản đúng gần nhất** và mô tả vị trí, loại khác biệt. '
        'Với dữ liệu thật, bản đúng ưu tiên là **bản sửa đúng sớm nhất về sau của chính sinh viên đó** (có ở 64/108 bài '
        'digits, 35/38 grade, 44/69 median, 18/64 smallest); nếu không có, chọn bản đúng gần nhất theo độ tương đồng '
        'chuỗi token trong kho lời giải đúng (IntroClass + lời giải tự viết). Hai chương trình được so khớp theo chuỗi '
        'token; mỗi đoạn khác biệt được phân loại dựa vào ngữ cảnh trên AST (nằm trong điều kiện if hay vòng lặp, là '
        'phép so sánh, phép gán, hằng số, lời gọi in…), tạo ra 24 thuộc tính `D:diff.*`. Đồng thời 4 thuộc tính A chỉ '
        'phản ánh phong cách lập trình bị loại.')
    D.p('**Lưu ý về đánh giá**: dữ liệu cấy lỗi dùng cùng quy trình tìm bản đúng gần nhất (không được biết chương trình '
        'gốc), nhưng quy trình này tìm đúng chương trình gốc ở 100% trường hợp, vì bài đột biến chỉ khác gốc vài token. '
        'Do đó trên dữ liệu sinh, nhóm D gần như mô tả trực tiếp phép đột biến – một dạng “thông tin rò rỉ”. Phép thử '
        'thật sự của nhóm D là dữ liệu thật (Phần 5.4 và 5.5).')
    D.h2('4.4. Trọng số các nhóm thuộc tính')
    D.p('Với trọng số khởi điểm (T 1, O 1,5, A 0,5, D 1,5), nhóm D bị các nhóm khác “pha loãng” và ARI trung bình chỉ '
        '0,31. Nhóm quét lưới trọng số T ∈ {0; 0,5; 1}, O ∈ {0; 0,5; 1,5}, A ∈ {0; 0,5}, D ∈ {1,5; 3} và đánh giá ARI '
        'trên dữ liệu sinh cùng silhouette trên dữ liệu thật (Bảng {T:grid}).')
    D.table(['T', 'O', 'A', 'D', 'ARI TB', 'ARI thấp nhất', 'Silhouette thật (k=6)'], [
        ['0,5', '0', '0', '3', '0,594', '0,335', '0,384'],
        ['**0**', '**0,5**', '**0,5**', '**3**', '**0,583**', '**0,513**', '**0,335**'],
        ['0,5', '0,5', '0,5', '3', '0,559', '0,169', '0,320'],
        ['0', '0', '0,5', '3', '0,551', '0,345', '0,421'],
        ['1', '1,5', '0,5', '1,5', '0,313', '0,124', '0,326'],
    ], [0.7, 0.7, 0.7, 0.7, 1.3, 1.5, 2.2], 'Trích kết quả quét lưới trọng số (gom cụm phân cấp, k = số nhãn)',
        label='grid', align=['c'] * 7)
    D.p('Nhóm chọn **T 0, O 0,5, A 0,5, D 3**: ARI trung bình gần cao nhất và **ARI thấp nhất cao nhất** (0,51), tức ổn '
        'định nhất giữa các bài tập. Nhóm T bị tắt vì kết quả test đã được phản ánh gián tiếp, ở dạng có ý nghĩa hơn, '
        'trong nhóm O. Silhouette trên dữ liệu thật gần như không đổi giữa các cấu hình (0,32–0,42). Cần lưu ý rằng '
        'việc chọn trọng số dựa trên ARI của dữ liệu sinh rồi báo cáo ARI trên chính dữ liệu đó là lạc quan; Phần 5.3 '
        'đánh giá lại bằng LOPO.')
    D.h2('4.5. Chọn số cụm')
    D.p('Với dữ liệu thật, nhóm quét k từ 2 đến 12 và xem xét silhouette, hàm chi phí K-modes và kích thước cụm nhỏ nhất '
        '(Hình {F:ksweep}). Silhouette không có cực đại rõ ràng – ở median và smallest còn tăng dần theo k do có nhiều '
        'bài trùng hệt nhau về thuộc tính. Vì vậy nhóm chọn **k lớn nhất trong khoảng 3–6 có silhouette gần cực đại và '
        'cụm nhỏ nhất có 2–3 bài**: digits 5, grade 4, median 5, smallest 4.')
    D.figure('results/figures/ksweep_real.png', 'Silhouette theo số cụm k trên dữ liệu thật (K-modes)', 13,
             label='ksweep')
    D.h2('4.6. Sinh luật và đặt tên cụm')
    D.p('Sau khi gom cụm, mã cụm được dùng làm nhãn lớp, ILA sinh luật trên các thuộc tính O, A, D (tối đa 3 điều kiện '
        'mỗi luật). Với mỗi cụm, đề tài lập hồ sơ gồm: các cặp thuộc tính – giá trị có tần suất trong cụm cao hơn rõ rệt '
        'so với toàn bài, các luật có độ phủ cao nhất, và bài đại diện (medoid) kèm diff so với bản đúng. Tên quan niệm '
        'sai lầm được đặt dựa trên hồ sơ này và **kiểm tra lại bằng diff giữa bài sai và bản sinh viên tự sửa**; ví dụ, '
        'một cụm ban đầu được gắn nhãn M6 đã được đổi tên sau khi diff cho thấy lỗi thực sự là điều kiện trung vị chỉ xét '
        'một chiều thứ tự. Ví dụ luật trên bài smallest:')
    D.code('R1: NẾU [D:diff.cmp_if = T] THÌ Cụm 0  [coverage 48/48, accuracy 1.00]\n'
           'R2: NẾU [D:diff.size = 1] THÌ Cụm 1  [coverage 2/2, accuracy 1.00]\n'
           'R3: NẾU [A:condition.if_cmp = nonstrict] VÀ [D:diff.size = 21+] THÌ Cụm 2  [coverage 5/7, accuracy 1.00]\n'
           'R5: NẾU [O:tests_zero.fail = none] VÀ [D:diff.cmp_if = F] THÌ Cụm 3  [coverage 4/7, accuracy 1.00]')
    D.p('Luật R1 được diễn giải: “nếu bài đổi phép so sánh trong điều kiện if (so với bản đúng) thì thuộc cụm 0” – phủ '
        'toàn bộ 48 bài của cụm, tương ứng quan niệm sai lầm “so sánh chặt không xử lý giá trị bằng nhau”.')

    # =================================================================================== CHƯƠNG 5
    D.h1('CHƯƠNG 5: THỰC NGHIỆM VÀ KẾT QUẢ', chap=5)
    D.h2('5.1. Khôi phục quan niệm sai lầm đã cấy (E1, E2)')
    D.p('Bảng {T:e1} so sánh ba phương pháp gom cụm trên dữ liệu cấy lỗi với trọng số đã chọn, k bằng số nhãn đơn.')
    D.table(['Bài tập', 'N', 'k', 'K-modes ARI', 'K-modes NMI', 'K-modes Purity', 'Agglomerative ARI',
             'K-means ARI'], [
        ['digits', '247', '7', '0,66', '0,75', '0,79', '0,64', '0,70'],
        ['grade', '79', '5', '0,73', '0,73', '0,82', '0,67', '0,98'],
        ['median', '82', '7', '0,48', '0,71', '0,66', '0,51', '0,65'],
        ['smallest', '51', '5', '0,67', '0,72', '0,75', '0,56', '0,47'],
        ['average', '21', '5', '0,54', '0,77', '0,71', '0,54', '0,56'],
    ], [1.4, 0.7, 0.5, 1.2, 1.2, 1.3, 1.6, 1.2], 'Kết quả gom cụm trên dữ liệu cấy lỗi (E1, E2)', label='e1',
        align=[None] + ['r'] * 7)
    D.p('K-modes đạt ARI 0,48–0,73 (trung bình 0,62), NMI 0,71–0,77: các cụm phần lớn trùng với quan niệm sai lầm đã '
        'cấy. Không có phương pháp thắng tuyệt đối: K-means trên one-hot rất tốt ở grade (0,98) và median nhưng kém nhất '
        'ở smallest (0,47); gom cụm phân cấp ổn định nhưng hiếm khi tốt nhất. Ma trận nhầm lẫn (Hình {F:confusion}) cho '
        'thấy các nhầm lẫn chủ yếu ở các bài lỗi kép và giữa các quan niệm có biểu hiện gần nhau (M1 – M6 ở digits).')
    D.figure('results/figures/confusion_syn_digits.png', 'Ma trận nhãn cấy × cụm (K-modes) ở bài digits', 12,
             label='confusion')
    D.h2('5.2. Ablation nhóm thuộc tính (E3)')
    D.p('Thực nghiệm quan trọng nhất kiểm tra đóng góp của từng nhóm thuộc tính (Hình {F:ablation}, Bảng {T:e3}).')
    D.figure('results/figures/ablation_E3.png', 'ARI theo tổ hợp nhóm thuộc tính (K-modes)', 15, label='ablation')
    D.table(['Nhóm thuộc tính', 'digits', 'grade', 'median', 'smallest', 'average'], [
        ['O', '0,25', '0,48', '0,06', '0,06', '0,14'],
        ['A', '0,06', '0,51', '0,24', '0,17', '0,04'],
        ['O + A', '0,27', '0,89', '0,23', '0,09', '0,22'],
        ['D', '0,28', '0,60', '0,53', '0,17', '0,40'],
        ['O + D', '0,63', '0,60', '0,71', '0,40', '0,50'],
        ['A + D', '0,51', '0,67', '0,63', '0,40', '0,54'],
        ['**O + A + D (chọn)**', '**0,66**', '**0,73**', '**0,48**', '**0,67**', '**0,54**'],
        ['T + O + A + D', '0,39', '0,94', '0,43', '0,33', '0,54'],
    ], [2.4, 1.1, 1.1, 1.1, 1.1, 1.1], 'ARI theo tổ hợp nhóm thuộc tính (K-modes)', label='e3',
        align=[None] + ['r'] * 5)
    D.p('Ba kết luận: (1) **Nhóm D là quyết định**: mọi tổ hợp có D đều vượt xa các tổ hợp không có D (trừ grade, nơi '
        'nhóm M7 chiếm 50/79 bài nên O + A đã đủ); (2) chỉ dùng thông tin output (O) hoặc cấu trúc (A) gần như không '
        'phân biệt được quan niệm sai lầm ở median và smallest; (3) thêm nhóm T làm giảm ARI ở 3/5 bài – kết quả test thô '
        'gây nhiễu hơn là giúp ích. Cần nhắc lại rằng trên dữ liệu sinh, D có lợi thế “gần như biết phép đột biến” '
        '(Phần 4.3), nên mức chênh lệch thực tế có thể nhỏ hơn.')
    D.h2('5.3. Độ nhạy của trọng số (E1b)')
    D.p('Để ước lượng thiên lệch do chọn trọng số trên chính dữ liệu đánh giá, nhóm thực hiện leave-one-problem-out: với '
        'mỗi bài tập, chọn trọng số tốt nhất trên 4 bài còn lại rồi đánh giá trên bài bị bỏ ra (Bảng {T:lopo}).')
    D.table(['Bài bỏ ra', 'Trọng số chọn từ 4 bài còn lại (T, O, A, D)', 'ARI (LOPO)', 'ARI với trọng số chung'], [
        ['digits', '1; 0; 0,5; 3', '0,28', '0,64'],
        ['grade', '0; 0,5; 0,5; 3', '0,67', '0,67'],
        ['median', '0; 0,5; 0,5; 3', '0,51', '0,51'],
        ['smallest', '0,5; 0; 0,5; 3', '0,15', '0,56'],
        ['average', '0,5; 0; 0; 3', '0,34', '0,54'],
    ], [1.4, 3.6, 1.4, 2.2], 'Đánh giá trọng số bằng leave-one-problem-out (gom cụm phân cấp)', label='lopo',
        align=[None, 'c', 'r', 'r'])
    D.p('Kết quả cho thấy trọng số D = 3 luôn được chọn, nhưng trọng số của T, O, A **nhạy theo bài tập**: ở digits và '
        'smallest, ARI giảm mạnh (0,64 → 0,28 và 0,56 → 0,15) khi trọng số được chọn từ các bài khác. Kết quả E1 vì vậy '
        'có phần lạc quan; trong ứng dụng thực tế nên tinh chỉnh trọng số cho từng bài tập, hoặc dùng cấu hình ổn định '
        '(D chiếm ưu thế, T tắt).')
    D.h2('5.4. Kết quả trên dữ liệu thật IntroClass (E4)')
    D.table(['Bài tập', 'Số bài', 'k', 'Silhouette', 'Davies–Bouldin', 'Số bài mỗi cụm', 'Số SV mỗi cụm'], [
        ['digits', '108', '5', '0,30', '2,07', '60/4/19/15/10', '35/3/12/11/7'],
        ['grade', '38', '4', '0,50', '1,11', '15/7/4/12', '12/5/1/7'],
        ['median', '69', '5', '0,25', '1,66', '27/19/3/16/4', '19/13/2/12/3'],
        ['smallest', '64', '4', '0,45', '1,24', '48/2/7/7', '36/2/4/5'],
    ], [1.3, 0.9, 0.5, 1.2, 1.4, 2, 2], 'Độ đo nội tại trên dữ liệu thật (K-modes)', label='e4',
        align=[None, 'r', 'r', 'r', 'r', 'c', 'c'])
    D.p('grade và smallest tách cụm tốt (silhouette ≈ 0,5), digits và median kém hơn (0,25–0,30). Kích thước cụm lệch: '
        'thường có một cụm lớn chiếm đa số – chính là quan niệm sai lầm phổ biến nhất. Bảng {T:macro} là bảng phản hồi '
        'vĩ mô (rút gọn) cho giảng viên; tên quan niệm sai lầm được đặt từ hồ sơ cụm và kiểm tra bằng diff với bản sửa '
        'của chính sinh viên.')
    D.table(['Bài', 'Cụm', 'Quan niệm sai lầm', 'Taxonomy', 'SV', 'Bài'], [
        ['smallest', 'C0', 'So sánh chặt (<) không xử lý các giá trị bằng nhau', 'M7', '36', '48'],
        ['smallest', 'C3', 'Dùng else-if làm mất các phép so sánh tiếp theo', '—', '5', '7'],
        ['smallest', 'C2', 'Cập nhật min sai biến (so với phần tử thay vì min hiện tại)', '—', '4', '7'],
        ['smallest', 'C1', 'Biên vòng lặp sai (duyệt thiếu phần tử)', 'M1', '2', '2'],
        ['median', 'C0', 'So sánh chặt bỏ sót trường hợp bằng nhau', 'M7', '19', '27'],
        ['median', 'C1', 'Sắp xếp/hoán đổi thiếu bước (bỏ biến tạm, bỏ ca bằng nhau)', '—', '13', '19'],
        ['median', 'C3', 'Điều kiện trung vị chỉ xét một chiều thứ tự', '—', '12', '16'],
        ['median', 'C4 / C2', 'Khởi tạo biến trung gian sai / lỗi chạy', 'M5', '3 / 2', '4 / 3'],
        ['digits', 'C0', 'Bỏ sót trường hợp n = 0 (vòng lặp while(n) không in gì)', '—', '35', '60'],
        ['digits', 'C2', 'Tách chữ số bằng log10/lũy thừa, sai với chữ số 0', '—', '12', '19'],
        ['digits', 'C3', 'Đặt dấu âm sai chỗ (in dấu cho mọi chữ số)', 'M8', '11', '15'],
        ['digits', 'C4', 'Cách tiếp cận lệch chuẩn (đọc chuỗi, break sớm) – cụm hỗn hợp', '—', '7', '10'],
        ['digits', 'C1', 'Xử lý số âm sai trong điều kiện vòng lặp', 'M8+M1', '3', '4'],
        ['grade', 'C0', 'Thiếu nhánh “failed” / chuỗi if độc lập không loại trừ nhau', '—', '12', '15'],
        ['grade', 'C3', 'Biên so sánh ngưỡng: dùng > thay vì >=', 'M7', '7', '12'],
        ['grade', 'C1', 'So sánh số thực bằng float và sắp thứ tự ngưỡng sai', '—', '5', '7'],
        ['grade', 'C2', 'Hiểu sai đề (tính trung bình ngưỡng) – 1 SV', '—', '1', '4'],
    ], [1.2, 0.9, 4.8, 1.1, 0.8, 0.8], 'Bảng phản hồi vĩ mô cho giảng viên (dữ liệu thật)', label='macro',
        align=[None, 'c', None, 'c', 'r', 'r'])
    D.p('Một số nhận xét định tính:')
    D.bullets([
        'Quan niệm sai lầm **“so sánh chặt bỏ sót trường hợp bằng nhau” (M7)** là phổ biến nhất ở cả smallest (36 SV) và '
        'median (19 SV), trùng với taxonomy cấy lỗi – dù ở dữ liệu sinh, đột biến M7 trên median/smallest đều tương '
        'đương. Điều này cho thấy ở dữ liệu thật, lỗi biểu hiện qua cấu trúc điều kiện của cả chuỗi if (Hình {F:heat}).',
        'Nhiều cụm **không thuộc taxonomy ban đầu** (else-if làm mất phép so sánh, điều kiện trung vị một chiều, dùng '
        'float khi so sánh ngưỡng): đây là giá trị của cách tiếp cận phi giám sát – phát hiện quan niệm sai lầm mà người '
        'thiết kế taxonomy chưa nghĩ tới.',
        'Các cụm digits kém thuần nhất: digits có nhiều cách giải rất khác nhau và chỉ 59% bài có bản tự sửa, nên bản '
        'đúng gần nhất nhiều khi khác xa bài sai (diff lớn), làm nhóm D kém đặc trưng.',
    ])
    D.figure('results/figures/heatmap_real_smallest.png', 'Tần suất thuộc tính theo cụm ở bài smallest (dữ liệu thật)',
             15, label='heat')
    D.h2('5.5. Đối chiếu trên ITSP (E4b)')
    D.p('Trên 602 cặp ITSP, đề tài gom cụm **gộp mọi bài tập** (nhóm D và nhóm O dạng tổng quát không phụ thuộc đề bài; '
        'nhóm O tổng quát so dãy số và dãy token của output: sai chữ, sai khoảng trắng, thừa/thiếu phần tử, lệch 1, sai '
        'dấu, sai thứ tự…), D so với **bản sửa của chính sinh viên**. Để có tham chiếu, một mẫu 45 cặp có diff nhỏ (1–4 '
        'dòng, tối đa 1 cặp mỗi bài, hạt giống 42) được gán nhãn thủ công từ diff **trước khi** gom cụm, theo 9 lớp: M1, '
        'M2, M6, M7, IDX (lệch chỉ số mảng), VAR (nhầm biến/thứ tự), LOGIC (sai điều kiện/công thức), MISSING (thiếu '
        'nhánh/câu lệnh), FMT (chỉ sai định dạng); còn 41 cặp sau lọc.')
    D.table(['Nhóm thuộc tính', 'k = 6', 'k = 10', 'k = 12', 'k = 20'], [
        ['O', '−0,01', '−0,03', '−0,02', '−0,01'],
        ['A', '−0,04', '−0,02', '−0,03', '−0,05'],
        ['D', '0,02', '0,06', '0,06', '0,06'],
        ['O + D', '0,04', '0,04', '0,04', '0,18'],
        ['O + A + D', '0,08', '0,12', '0,14', '0,09'],
    ], [2.4, 1.3, 1.3, 1.3, 1.3], 'ARI trên mẫu có nhãn của ITSP (K-modes)', label='itsp', align=[None] + ['r'] * 4)
    D.p('Với cấu hình chính (O + A + D, K-modes) và k = 9 bằng số lớp nhãn, ARI đạt 0,20, NMI 0,54, purity 0,51; khi '
        'quét k, ARI dao động 0,07–0,14 – mức thấp và không ổn định do mẫu nhãn nhỏ. Các cụm nhận diện tốt là “đổi so '
        'sánh trong if theo kiểu chặt ↔ không chặt” (3/3 bài M7 cùng cụm, thuần nhất), “đổi so sánh ở vòng lặp” (M1) và '
        '“thiếu câu lệnh” (MISSING). Ngược lại, hai cụm lớn (226 và 158 bài) gom theo kích thước diff và lỗi chỉ ở phần '
        'chữ của output, trộn lẫn FMT, VAR, LOGIC và M1. Kết luận: nhóm D hiện **chưa phân biệt được nhầm biến và sai '
        'công thức**, và việc gộp nhiều bài tập khác nhau vào một lần gom cụm khó hơn đáng kể so với gom theo từng bài.')
    D.h2('5.6. Chất lượng luật (E5)')
    D.table(['Dữ liệu', 'Bài tập', 'ILA: số luật', 'ILA: điều kiện/luật', 'ILA: độ chính xác', 'ID3: số luật',
             'ID3: điều kiện/luật', 'ID3: độ chính xác'], [
        ['Thật', 'digits', '36', '1,8', '0,75', '18', '4,6', '0,74'],
        ['Thật', 'grade', '12', '1,5', '0,79', '8', '3,4', '0,81'],
        ['Thật', 'median', '25', '1,8', '0,70', '11', '3,8', '0,91'],
        ['Thật', 'smallest', '8', '1,8', '0,92', '7', '3,9', '0,92'],
        ['Sinh', 'digits', '46', '2,0', '0,87', '15', '4,6', '0,97'],
        ['Sinh', 'grade', '13', '1,8', '0,87', '8', '3,4', '0,92'],
        ['Sinh', 'median', '14', '1,6', '0,81', '12', '3,8', '0,90'],
        ['Sinh', 'smallest', '13', '1,8', '0,82', '11', '4,3', '0,88'],
        ['Sinh', 'average', '7', '1,3', '0,78', '6', '2,8', '0,72'],
    ], [0.9, 1.3, 1.1, 1.3, 1.3, 1.1, 1.3, 1.3], 'So sánh luật của ILA và ID3 (độ chính xác: kiểm định chéo)',
        label='e5', align=[None, None] + ['r'] * 6)
    D.p('Luật của ILA **ngắn hơn rõ rệt** (1,3–2,0 điều kiện so với 2,8–4,6 của ID3) nên dễ đọc hơn đối với giảng viên, '
        'nhưng ILA sinh nhiều luật hơn và độ chính xác kiểm định chéo thường thấp hơn ID3 (0,70–0,92 so với 0,72–0,97), '
        'đặc biệt ở median thật (0,70 so với 0,91). Đây là đánh đổi điển hình: ILA ưu tiên luật nhất quán tuyệt đối trên '
        'tập huấn luyện nên dễ quá khớp với cụm nhỏ. Với mục tiêu giải thích cụm (không phải dự đoán), các luật ngắn, độ '
        'phủ cao của ILA phù hợp hơn; ví dụ luật R1 ở Phần 4.6 phủ 48/48 bài của cụm chỉ với một điều kiện.')
    D.h2('5.7. Demo hệ thống')
    D.p('Chương trình demo là một ứng dụng web (Streamlit) gồm bốn trang: giới thiệu, trang dành cho giảng viên, trang '
        'thử nộp bài và trang kết quả thực nghiệm. Trang giảng viên (Hình {F:teacher}) cho phép chọn bài tập để xem các '
        'quan niệm sai lầm xếp theo số sinh viên mắc, dấu hiệu đặc trưng, luật ILA diễn giải bằng tiếng Việt và bài minh '
        'họa kèm diff.')
    D.figure('results/figures/demo/ui_teacher.png', 'Trang giảng viên: các lỗi phổ biến ở bài smallest', 13,
             label='teacher')
    D.p('Trang thử nộp bài (Hình {F:submit}) nhận một bài C mới, chấm test, trích OAV, gán bài vào cụm có mode gần nhất '
        '(đúng bước gán của K-modes), chỉ ra luật khớp, mức tương đồng với từng cụm và diff so với bài đúng tương tự '
        'nhất. Thời gian chẩn đoán thường dưới 1 giây; bài lặp vô hạn mất khoảng 25 giây vì mỗi test chạy tới giới hạn '
        'thời gian.')
    D.figure('results/figures/demo/ui_submit.png', 'Trang thử nộp bài: chẩn đoán một bài smallest dùng so sánh chặt', 13,
             label='submit')
    D.p('Về kiến trúc, giao diện chạy trong một container riêng không có trình biên dịch; bài nộp được chuyển qua hàng '
        'đợi tệp cho một **container sandbox** không có mạng, hệ thống tệp chỉ đọc, chỉ ghi được hàng đợi và vùng tạm. '
        'Khi rà soát, nhóm phát hiện phiên bản đầu chạy bài nộp trong container nghiên cứu nên bài nộp có thể ghi vào thư '
        'mục dự án; lỗi này đã được khắc phục bằng sandbox. Bảng {T:security} tóm tắt kết quả thử với các bài nộp độc '
        'hại.')
    D.table(['Bài nộp thử', 'Kết quả'], [
        ['Lặp vô hạn / ngủ dài', 'TIMEOUT ở mọi test'],
        ['In vô hạn', 'OUTPUT_LIMIT ở mọi test'],
        ['Cấp phát bộ nhớ liên tục', 'Bị chặn bởi giới hạn bộ nhớ'],
        ['Ghi tệp vào thư mục dự án / mã nguồn', 'Bị chặn (hệ thống tệp chỉ đọc)'],
        ['Mở kết nối mạng', 'Thất bại (không có mạng)'],
        ['Fork bomb', 'Bị chặn; sandbox tự hồi phục'],
        ['#include "/dev/zero"', 'Trình biên dịch bị dừng ở giới hạn bộ nhớ, báo lỗi biên dịch'],
        ['Tự diệt tiến trình chấm', 'Sandbox tự khởi động lại, báo lỗi cho bài đó, bài sau chấm bình thường'],
    ], [4, 5], 'Thử nghiệm sandbox với các bài nộp độc hại', label='security')
    D.p('Độ chính xác chẩn đoán trên bài mới: 5/6 bài mẫu tự viết (5 bài sai, 1 bài đúng) được chẩn đoán đúng; 16/18 bài '
        'đại diện của các cụm được gán lại đúng cụm của chính nó. Sai lệch xuất phát từ việc bài mới không có bản tự sửa, '
        'nên nhóm D phải so với bản đúng gần nhất trong kho – ví dụ bài digits chỉ quên trường hợp n = 0 bị gán vào cụm '
        '“tách chữ số bằng log10” vì bản đúng gần nhất có cấu trúc khác.')
    D.h2('5.8. Thảo luận')
    D.bullets([
        '**Kết quả test là chưa đủ**: chỉ dùng kết quả test hay kiểu sai của output gần như không phân biệt được quan '
        'niệm sai lầm; thông tin “bài sai khác bài đúng ở đâu” mới là tín hiệu quyết định. Điều này ủng hộ việc tận dụng '
        'các bản sửa của sinh viên (lịch sử nộp bài) trong hệ thống chấm.',
        '**Đánh giá trên dữ liệu sinh lạc quan**: nhóm D gần như biết phép đột biến, và trọng số được chọn trên chính '
        'dữ liệu đánh giá; LOPO cho thấy ARI có thể giảm còn 0,15–0,28 ở một số bài.',
        '**Giá trị phát hiện**: trên dữ liệu thật, phương pháp phi giám sát tìm ra các quan niệm sai lầm ngoài taxonomy '
        'và lượng hóa được mức độ phổ biến (số sinh viên), đúng mục tiêu macro-feedback.',
        '**Vai trò của con người**: tên quan niệm sai lầm vẫn cần giảng viên đặt và kiểm tra; luật ILA và diff đại diện '
        'giúp việc này nhanh hơn nhiều so với đọc toàn bộ bài.',
    ])

    # =================================================================================== CHƯƠNG 6
    D.h1('CHƯƠNG 6: KẾT LUẬN', chap=6)
    D.h2('6.1. Tóm tắt kết quả')
    D.p('Đề tài đã xây dựng quy trình đầu–cuối tự động phát hiện và cụm hóa quan niệm sai lầm trong bài làm C sai: chấm '
        'bài an toàn và khớp 98–100% với siêu dữ liệu IntroClass; hình thức hóa bài làm thành bộ ba OAV gồm bốn nhóm '
        'thuộc tính; gom cụm bằng K-modes với khoảng cách Hamming có trọng số; sinh luật bằng ILA tự cài đặt. Trên 480 '
        'bài cấy lỗi có nhãn, K-modes đạt ARI 0,48–0,73; nhóm thuộc tính “khác biệt so với bản đúng” là yếu tố quyết '
        'định. Trên 279 bài sai thật, hệ thống tìm ra 18 cụm có ý nghĩa, trong đó lỗi so sánh chặt bỏ sót giá trị bằng '
        'nhau là phổ biến nhất (36 sinh viên ở smallest, 19 ở median). Trên ITSP, kết quả còn hạn chế (ARI 0,07–0,20).')
    D.h2('6.2. Đóng góp chính')
    D.bullets([
        'Bộ công cụ chấm bài an toàn, được kiểm định với dữ liệu gốc, xử lý biến chưa khởi tạo và lỗi định dạng.',
        'Bộ dữ liệu 480 bài cấy lỗi có nhãn theo taxonomy 8 quan niệm sai lầm, đã loại đột biến tương đương.',
        'Bộ thuộc tính OAV bốn nhóm, trong đó nhóm D (khác biệt so với bản đúng gần nhất) được chứng minh qua ablation.',
        'Cài đặt ILA và so sánh với ID3 cho bài toán giải thích cụm.',
        'Bảng macro-feedback và chương trình demo có giao diện web, chạy trong sandbox đã kiểm thử.',
    ])
    D.h2('6.3. Hạn chế')
    D.bullets([
        'Dữ liệu thật quy mô nhỏ (38–108 bài mỗi bài tập), các bài tập đơn giản; không có quan niệm sai lầm về con trỏ '
        'trong dữ liệu thật.',
        'Trọng số chọn trên dữ liệu sinh và nhạy theo bài tập; ARI trên dữ liệu sinh lạc quan do nhóm D gần như biết phép '
        'đột biến.',
        'Nhóm D phụ thuộc chất lượng bản đúng tham chiếu; khi không có bản tự sửa, chẩn đoán kém chính xác hơn.',
        'Đánh giá trên ITSP dựa trên mẫu nhãn nhỏ (41 cặp), do một người gán, chưa kiểm tra độ đồng thuận giữa nhiều '
        'người gán.',
        'Mỗi bài được gán đúng một cụm, trong khi một bài có thể mang nhiều quan niệm sai lầm.',
        'Tên quan niệm sai lầm do con người đặt, chưa có đánh giá từ giảng viên thực tế.',
    ])
    D.h2('6.4. Hướng phát triển')
    D.bullets([
        'Kết hợp véc-tơ biểu diễn mã nguồn học sẵn (CodeBERT, UniXcoder) với véc-tơ OAV (gom cụm lai), so sánh với OAV '
        'thuần túy.',
        'Mở rộng nhóm D để phân biệt nhầm biến và sai công thức (theo luồng dữ liệu, kiểu của biểu thức).',
        'Gom cụm mềm (fuzzy K-modes) hoặc đa nhãn để xử lý bài mang nhiều quan niệm sai lầm.',
        'Dùng mô hình ngôn ngữ lớn để đề xuất tên và giải thích cụm từ luật và bài đại diện, có giảng viên kiểm duyệt.',
        'Thu thập dữ liệu lớp học thực tế (có bài về con trỏ, mảng, hàm) và đánh giá cùng giảng viên.',
    ])

    # =================================================================================== TÀI LIỆU
    D.h1('TÀI LIỆU THAM KHẢO')
    refs = [
        'C. Le Goues, N. Holtschulte, E. K. Smith, Y. Brun, P. Devanbu, S. Forrest, and W. Weimer, “The ManyBugs and '
        'IntroClass Benchmarks for Automated Repair of C Programs,” *IEEE Transactions on Software Engineering*, vol. 41, '
        'no. 12, pp. 1236–1256, 2015.',
        'J. Yi, U. Z. Ahmed, A. Karkare, S. H. Tan, and A. Roychoudhury, “A Feasibility Study of Using Automated Program '
        'Repair for Introductory Programming Assignments,” in *Proc. ESEC/FSE*, 2017.',
        'Y. Qian and J. Lehman, “Students’ Misconceptions and Other Difficulties in Introductory Programming: A '
        'Literature Review,” *ACM Transactions on Computing Education*, vol. 18, no. 1, 2017.',
        'J. Sorva, “Notional Machines and Introductory Programming Education,” *ACM Transactions on Computing '
        'Education*, vol. 13, no. 2, 2013.',
        'E. L. Glassman, J. Scott, R. Singh, P. J. Guo, and R. C. Miller, “OverCode: Visualizing Variation in Student '
        'Solutions to Programming Problems at Scale,” *ACM Transactions on Computer-Human Interaction*, vol. 22, no. 2, '
        '2015.',
        'C. Piech, J. Huang, A. Nguyen, M. Phulsuksombati, M. Sahami, and L. Guibas, “Learning Program Embeddings to '
        'Propagate Feedback on Student Code,” in *Proc. ICML*, 2015.',
        'S. Gulwani, I. Radiček, and F. Zuleger, “Automated Clustering and Program Repair for Introductory Programming '
        'Assignments,” in *Proc. PLDI*, 2018.',
        'A. Head, E. Glassman, G. Soares, R. Suzuki, L. Figueredo, L. D’Antoni, and B. Hartmann, “Writing Reusable '
        'Code Feedback at Scale with Mixed-Initiative Program Synthesis,” in *Proc. ACM Learning@Scale*, 2017.',
        'Z. Huang, “Extensions to the k-Means Algorithm for Clustering Large Data Sets with Categorical Values,” *Data '
        'Mining and Knowledge Discovery*, vol. 2, no. 3, pp. 283–304, 1998.',
        'F. Cao, J. Liang, and L. Bai, “A new initialization method for categorical data clustering,” *Expert Systems '
        'with Applications*, vol. 36, no. 7, pp. 10223–10228, 2009.',
        'M. R. Tolun and S. M. Abu-Soud, “ILA: An Inductive Learning Algorithm for Rule Extraction,” *Expert Systems '
        'with Applications*, vol. 14, no. 3, pp. 361–370, 1998.',
        'J. R. Quinlan, “Induction of Decision Trees,” *Machine Learning*, vol. 1, no. 1, pp. 81–106, 1986.',
        'L. Hubert and P. Arabie, “Comparing Partitions,” *Journal of Classification*, vol. 2, pp. 193–218, 1985.',
        'A. Strehl and J. Ghosh, “Cluster Ensembles – A Knowledge Reuse Framework for Combining Multiple Partitions,” '
        '*Journal of Machine Learning Research*, vol. 3, pp. 583–617, 2002.',
        'P. J. Rousseeuw, “Silhouettes: A Graphical Aid to the Interpretation and Validation of Cluster Analysis,” '
        '*Journal of Computational and Applied Mathematics*, vol. 20, pp. 53–65, 1987.',
        'D. L. Davies and D. W. Bouldin, “A Cluster Separation Measure,” *IEEE Transactions on Pattern Analysis and '
        'Machine Intelligence*, vol. PAMI-1, no. 2, pp. 224–227, 1979.',
        'Y. Jia and M. Harman, “An Analysis and Survey of the Development of Mutation Testing,” *IEEE Transactions on '
        'Software Engineering*, vol. 37, no. 5, pp. 649–678, 2011.',
        'J. B. Kruskal, “Multidimensional Scaling by Optimizing Goodness of Fit to a Nonmetric Hypothesis,” '
        '*Psychometrika*, vol. 29, pp. 1–27, 1964.',
        'F. Pedregosa et al., “Scikit-learn: Machine Learning in Python,” *Journal of Machine Learning Research*, vol. 12, '
        'pp. 2825–2830, 2011.',
        'M. Brunsfeld et al., “Tree-sitter: a parser generator tool and an incremental parsing library.” '
        'https://tree-sitter.github.io',
        'L. Kaufman and P. J. Rousseeuw, *Finding Groups in Data: An Introduction to Cluster Analysis*. Wiley, 1990.',
        'J. MacQueen, “Some Methods for Classification and Analysis of Multivariate Observations,” in *Proc. 5th '
        'Berkeley Symposium on Mathematical Statistics and Probability*, vol. 1, pp. 281–297, 1967.',
    ]
    for i, r in enumerate(refs, 1):
        D.blocks.append(('ref', f'[{i}] {r}'))

    # =================================================================================== PHỤ LỤC
    D.h1('PHỤ LỤC: MÃ NGUỒN VÀ HƯỚNG DẪN CHẠY LẠI', chap='PL')
    D.p('Mã nguồn được tổ chức thành các mô-đun dùng chung (`src/`), các script cho từng bước (`scripts/`) và kiểm thử '
        '(`tests/`). Mọi thao tác biên dịch/chạy diễn ra trong container `aai-lab`; dữ liệu gốc được gắn chỉ đọc.')
    D.table(['Thành phần', 'Vai trò'], [
        ['`src/runner.py`', 'Biên dịch và chạy bài C có giới hạn tài nguyên, chấm hai chế độ'],
        ['`src/normalize.py`', 'Bộ chấm strict (mô phỏng IntroClass) và semantic'],
        ['`src/mutators.py`', 'Toán tử đột biến M1–M8 theo vị trí byte trên AST'],
        ['`src/features.py`, `src/diff_features.py`', 'Trích xuất thuộc tính OAV nhóm T, O, A và D'],
        ['`src/cluster.py`', 'Khoảng cách Hamming có trọng số, K-modes, Agglomerative, K-means one-hot, độ đo'],
        ['`src/ila.py`', 'Cài đặt thuật toán ILA'],
        ['`src/classify.py`, `ui/app.py`', 'Chẩn đoán bài mới và giao diện demo'],
        ['`scripts/p1_*` … `p8_*`', 'Các bước: chấm và lọc dữ liệu, sinh đột biến, trích OAV, gom cụm, thực nghiệm, '
                                    'hình, demo'],
    ], [3.4, 5.6], 'Các thành phần mã nguồn chính', label='code')
    D.p('Các lệnh chính:', indent=False)
    D.code('# môi trường nghiên cứu + 94 kiểm thử\n'
           'docker compose up -d lab\n'
           'docker exec aai-lab pytest -q\n'
           '# gom cụm, sinh luật, thực nghiệm E1–E5; hình + bảng macro-feedback\n'
           'docker exec aai-lab python scripts/p5_experiments.py\n'
           'docker exec aai-lab python scripts/p6_figures.py\n'
           '# giao diện demo: http://127.0.0.1:8501\n'
           './demo/start.sh')
    return D
