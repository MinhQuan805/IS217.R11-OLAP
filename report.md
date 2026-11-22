Phần bạn đang nhớ là **chương “Trực quan hóa dữ liệu và xây dựng báo cáo”** — trình bày dashboard bằng Power BI và Looker Studio đó.

Mình xem các file trong đồ án rồi, nhưng **chưa thấy mục lục báo cáo tổng hợp để xác định chính xác số chương**. Bạn đặt chương này sau phần xây dựng cube SSAS và truy vấn MDX là hợp lý. Dưới đây mình ký hiệu là **Chương X** nhé. Mình đang hiểu “Looker” bạn nói là **Looker Studio**.

**1. Với đồ án của bạn, nên làm theo luồng nào?**

```text
Kho dữ liệu tuyển sinh
    ├── Cube SSAS → Power BI
    └── Dữ liệu xuất từ kho → Google Sheets → Looker Studio
```

Power BI dùng cube bạn đã xây dựng. Looker Studio dùng dữ liệu xuất từ cùng kho để hai bên có thể đối chiếu kết quả.

**2. Cách làm bằng Power BI**

**Bước 1 — Triển khai cube**

Mở project `ADMISSION_SSAS` trong Visual Studio, kiểm tra kết nối rồi **Deploy và Process** thành công.

File `.cube` là định nghĩa mô hình; bạn cần kết nối đến cube đang chạy trên SSAS.

Trong cấu hình triển khai hiện có:

- Server: `CAOTHAIBAO`.
- Database: `ADMISSION_SSAS`.
- Cube: `Admission Data Warehouse`.

Đây là cấu hình lưu trong project; nếu bạn chạy trên máy khác thì thay server tương ứng.

**Bước 2 — Kết nối Power BI Desktop**

Chọn:

**Home → Get data → SQL Server Analysis Services database → nhập server → Connect live → chọn cube.**

Microsoft hỗ trợ kết nối trực tiếp đến SSAS Multidimensional theo cách này. [Hướng dẫn Microsoft](https://learn.microsoft.com/en-us/power-bi/connect-data/desktop-ssas-multidimensional).

**Bước 3 — Làm 3 trang báo cáo**

| Trang | Nội dung | Trường và độ đo trong cube |
|---|---|---|
| Tổng quan tuyển sinh | Thẻ số liệu, biểu đồ điểm chuẩn qua năm | `FACT CUTOFF SCORE Count`, `Mean SCORE MARK`, `Minimum SCORE MARK`, `Maximum SCORE MARK`, `DIM YEAR` |
| Phân tích trường và ngành | Top 10 ngành theo điểm chuẩn trung bình; so sánh trường; bảng chi tiết | `DIM MAJOR`, `DIM SCHOOL`, `DIM PROGRAM`, `Mean SCORE MARK` |
| Biến động điểm chuẩn | So sánh 2024–2025; mức tăng giảm theo trường/chương trình | `Score 2024`, `Score 2025`, `Diff 2025-2024` |

Thêm **Slicer** cho năm, tỉnh/thành, trường và phương thức xét tuyển.

Ví dụ làm biểu đồ đầu tiên:

1. Chọn **Line chart**.
2. Kéo `DIM YEAR → YEAR` vào trục X.
3. Kéo `Mean SCORE MARK` vào trục Y.
4. Lọc phương thức bằng **Điểm thi THPT**.
5. Đặt tên: **“Xu hướng điểm chuẩn trung bình theo năm”**.

Với biểu đồ Top 10 ngành: dùng **Bar chart**, trục là tên ngành, giá trị là `Mean SCORE MARK`, rồi đặt bộ lọc **Top N = 10** theo độ đo này.

**Hai điểm cần chú ý với cube của bạn:**

- `FACT CUTOFF SCORE Count` là **số bản ghi điểm chuẩn**, không phải số thí sinh hay số người trúng tuyển.
- Các phương thức có thể khác thang điểm; cần lọc cùng phương thức và kiểm tra cùng thang điểm trước khi so sánh. Độ đo `SCORE MARK` đang cộng điểm, nên biểu đồ điểm chuẩn thường dùng `Mean SCORE MARK`, Min hoặc Max.

Cube có các **named set** như `Programs Up 2.5`, nhưng Power BI không hiển thị named set của SSAS; bạn tái hiện điều kiện bằng bộ lọc trên biểu đồ. [Giới hạn được Microsoft nêu](https://learn.microsoft.com/en-us/power-bi/connect-data/desktop-ssas-multidimensional#considerations-and-limitations).

**3. Cách làm bằng Looker Studio**

Với SQL Server chạy trên máy cá nhân, mình đề xuất **xuất dữ liệu từ kho ra CSV rồi đưa vào Google Sheets**. Connector SQL Server của Looker Studio yêu cầu server có địa chỉ truy cập được từ bên ngoài, không kết nối trực tiếp đến `localhost`. [Tài liệu Google](https://docs.cloud.google.com/data-studio/connect-to-microsoft-sql-server).

**Bước 1 — Chuẩn bị bảng dữ liệu phẳng**

Xuất dữ liệu sau ETL, gồm các cột:

```text
FACT_ID, YEAR, SCHOOL_NAME, PROVINCE_NAME,
PROGRAM_NAME, MAJOR_NAME, ADMISSION_METHOD_NAME, SCORE_MARK
```

Giữ **một dòng tương ứng một bản ghi fact**. Tránh nối thêm bảng tổ hợp môn làm một bản ghi điểm chuẩn bị nhân thành nhiều dòng.

**Bước 2 — Đưa vào Google Sheets**

Import CSV, giữ hàng đầu là tên cột, kiểm tra `SCORE_MARK` là số.

**Bước 3 — Kết nối Looker Studio**

Chọn **Create → Report → Add data → Google Sheets → chọn file và worksheet → Add**. Connector Google Sheets hỗ trợ lấy hàng đầu làm tên trường. [Hướng dẫn Google](https://docs.cloud.google.com/data-studio/connect-to-google-sheets).

**Bước 4 — Dựng báo cáo tương ứng**

- **Scorecard:** số bản ghi điểm chuẩn.
- **Line chart:** năm và `AVG(SCORE_MARK)`.
- **Bar chart:** ngành/trường và `AVG(SCORE_MARK)`.
- **Table:** trường, chương trình, năm, điểm chuẩn.
- **Drop-down control:** năm, tỉnh/thành, trường, phương thức.

Đặt phép tổng hợp điểm là **Average**, và áp dụng cùng bộ lọc như Power BI để đối chiếu.

**4. Chương báo cáo nên viết thế nào?**

Bạn có thể dùng bố cục này:

```text
CHƯƠNG X. TRỰC QUAN HÓA DỮ LIỆU VÀ XÂY DỰNG BÁO CÁO

X.1. Mục tiêu phân tích
X.2. Nguồn dữ liệu và phương án kết nối
X.3. Xây dựng báo cáo bằng Power BI
    X.3.1. Kết nối đến cube SSAS
    X.3.2. Báo cáo tổng quan tuyển sinh
    X.3.3. Báo cáo phân tích trường và ngành
    X.3.4. Báo cáo biến động điểm chuẩn
X.4. Xây dựng báo cáo bằng Looker Studio
    X.4.1. Chuẩn bị và kết nối dữ liệu
    X.4.2. Thiết kế biểu đồ và bộ lọc
X.5. Đối chiếu kết quả và nhận xét
```

Với **mỗi dashboard**, viết theo thứ tự:

1. **Câu hỏi phân tích:** dashboard giúp trả lời điều gì?
2. **Dữ liệu sử dụng:** chiều, độ đo và bộ lọc.
3. **Ảnh kết quả:** chụp dashboard có tiêu đề, nhãn và đơn vị rõ ràng.
4. **Nhận xét:** dẫn số liệu thực tế, giải thích ý nghĩa và giới hạn của kết quả.

Đoạn mở đầu có thể dùng:

> Chương này trình bày việc khai thác kho dữ liệu điểm chuẩn tuyển sinh thông qua Power BI và Looker Studio. Các báo cáo hỗ trợ theo dõi biến động điểm chuẩn theo năm, so sánh giữa các trường và ngành đào tạo, đồng thời cho phép người dùng lọc dữ liệu theo phương thức xét tuyển và địa phương. Kết quả trên hai công cụ được đối chiếu trong cùng phạm vi dữ liệu và điều kiện lọc.

Bạn cũng đã có **15 truy vấn trong [queries.mdx](</D:/Study/University/OLAP/Đồ án/IS217.R11-OLAP/queries.mdx>)**. Có thể lấy các câu hỏi phân tích đó làm nội dung dashboard và dùng kết quả MDX/Excel để kiểm chứng số liệu; như vậy chương này sẽ nối tiếp rất sát phần OLAP đã làm.