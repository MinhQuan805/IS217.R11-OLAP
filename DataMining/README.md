# ĐỒ ÁN KHAI PHÁ DỮ LIỆU TUYỂN SINH ĐẠI HỌC (2010 - 2025)

**Môn học:** KHO DỮ LIỆU VÀ OLAP (IS217.R11)  
**Trường:** Đại học Công nghệ Thông tin – ĐHQG-HCM (UIT)  
**Giảng viên hướng dẫn:** ThS. Đỗ Thị Minh Phụng  
**Nhóm sinh viên thực hiện:**  
1. Cao Thái Bảo – MSSV: 24520145  
2. Võ Minh Quân – MSSV: 24521459  

---

## 1. Giới thiệu đề tài

Thư mục này chứa toàn bộ mã nguồn, dữ liệu thực nghiệm và tài liệu báo cáo của học phần Khai phá dữ liệu (Data Mining) – **Chương 5** của Đồ án Kho dữ liệu và OLAP Tuyển sinh Đại học Việt Nam (2010 – 2025).

Nội dung nghiên cứu giải quyết 3 bài toán học máy:
1. **Hồi quy (Regression):** Dự báo điểm chuẩn thực tế (`score_mark` thang điểm 30) của từng trường, ngành và tổ hợp xét tuyển trong tương lai bằng Random Forest và XGBoost Regressor.
2. **Phân loại đa lớp (Multi-class Classification):** Phân tầng mức độ cạnh tranh của các chương trình đào tạo thành 4 phân khúc (`Dưới 18`, `Từ 18 đến dưới 22`, `Từ 22 đến dưới 25`, `Từ 25 trở lên`) bằng Decision Tree, Random Forest, XGBoost và LightGBM.
3. **Phân loại nhị phân (Binary Classification):** Dự báo và cảnh báo ngành có điểm chuẩn cạnh tranh cao ($\ge 24.0$ điểm), phân tích đường cong ROC và chỉ số AUC.
4. **Phân tích mức độ quan trọng đặc trưng (Feature Importance):** Ứng dụng kỹ thuật Permutation Importance nhằm xác định các nhân tố chi phối mạnh mẽ nhất đến điểm chuẩn (Điểm chuẩn năm trước, Danh tiếng trường, Vùng miền, Nhóm ngành, Khối thi).

---

## 2. Nguồn dữ liệu sử dụng

Bộ dữ liệu đầu vào được lấy trực tiếp từ thư mục dữ liệu sạch chuẩn hóa của đồ án tại `PythonScripts/cleaned-data`:
- `cleaned-cutoff-scores.csv`: 103,403 dòng lưu vết điểm chuẩn qua các năm. **Lưu ý:** Điểm chuẩn sử dụng trực tiếp cột `score_mark` (đã được chuẩn hóa về thang 30, không sử dụng `converted_score_mark`).
- `cleaned-majors.csv`: 506 dòng danh mục ngành và nhóm ngành đào tạo chuẩn hóa.
- `cleaned-score-blocks.csv`: 280 tổ hợp môn xét tuyển chuẩn quốc gia.

---

## 3. Cấu trúc thư mục

```text
DataMining/
├── notebooks/
│   └── Data_Mining.ipynb      # File Jupyter Notebook thực nghiệm độc lập (self-contained) chuẩn hóa theo CHƯƠNG 5
├── results/
│   └── images/                # Danh mục các biểu đồ kết quả thực nghiệm (Confusion Matrix, Feature Importance, So sánh)
├── README.md                  # Tài liệu hướng dẫn cấu trúc dự án và tóm tắt kết quả
└── requirements.txt           # Danh sách các thư viện cần thiết
```

---

## 4. Hướng dẫn cài đặt và thực thi

### Bước 1: Cài đặt các thư viện cần thiết
```bash
pip install -r requirements.txt
```

### Bước 2: Chạy thực nghiệm và theo dõi trực quan
- Mở file `notebooks/Data_Mining.ipynb` trong VS Code hoặc Jupyter Lab và chọn `Run All`.
- Toàn bộ notebook được thiết kế độc lập (self-contained), tự động đọc dữ liệu nguồn tại `PythonScripts/cleaned-data/`, thực hiện chọn lọc dữ liệu, huấn luyện các mô hình (Decision Tree, Random Forest, XGBoost, LightGBM) và trực quan hóa kết quả kiểm thử trên Test 2025.
- Đọc báo cáo hoàn chỉnh tại file `report.md` hoặc `report.docx`.

---

## 5. Tóm tắt kết quả thực nghiệm chính (Tập Test 2025)

- **Hồi quy điểm chuẩn (Score Mark):**
  - **Random Forest Regressor** đạt sai số tuyệt đối thấp nhất: $MAE = 2.548$ điểm, $RMSE = 3.224$ điểm, $R^2 = 0.4494$.
  - **XGBoost Regressor** đạt: $MAE = 2.664$ điểm, $RMSE = 3.259$ điểm, $R^2 = 0.4374$.
  - Cả hai mô hình vượt trội so với điểm năm trước (*Previous year baseline*, $MAE = 4.028$) và trung vị (*Median baseline*, $MAE = 4.371$).
- **Phân loại nhị phân ngành cạnh tranh cao ($\ge 24.0$ điểm):**
  - **XGBoost Classifier** đạt độ chính xác $80.72\%$, $Macro\ F1 = 0.7833$ và $ROC\ AUC = 0.8739$.
- **Phân loại đa lớp (4 tầng điểm):**
  - **LightGBM** đạt độ chính xác cao nhất: $Accuracy = 50.94\%$, $Macro\ F1 = 0.4699$, $Weighted\ F1 = 0.4818$.
  - **XGBoost** đạt $Accuracy = 49.95\%$, $Macro\ F1 = 0.4570$.
  - **Random Forest** đạt $Accuracy = 49.10\%$, $Macro\ F1 = 0.4542$.
- **Đặc trưng chi phối điểm chuẩn:**
  1. `previous_year_score`: $+1.525$ điểm MAE (nhân tố quan trọng nhất).
  2. `school_id`: $+0.758$ điểm MAE.
  3. `province_name`: $+0.448$ điểm MAE.
  4. `major_groups`: $+0.235$ điểm MAE.
  5. `block_set`: $+0.169$ điểm MAE.
