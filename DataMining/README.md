# ĐỒ ÁN KHAI PHÁ DỮ LIỆU TUYỂN SINH ĐẠI HỌC (2010 - 2025)

**Môn học:** KHO DỮ LIỆU VÀ OLAP (IS217.R11)  
**Trường:** Đại học Công nghệ Thông tin – ĐHQG-HCM (UIT)  
**Giảng viên hướng dẫn:** ThS. Đỗ Thị Minh Phụng  
**Sinh viên thực hiện:**  
1. Cao Thái Bảo – MSSV: 24520145  
2. Võ Minh Quân – MSSV: 24521459  

---

## 1. Giới thiệu đề tài

Thư mục này chứa mã nguồn thực nghiệm khai phá dữ liệu (Data Mining) hỗ trợ phân tích và dự báo tuyển sinh Đại học tại Việt Nam giai đoạn 2010 – 2025:
* **Hồi quy (Regression):** Dự báo điểm chuẩn thực tế (Score Mark) bằng Random Forest và XGBoost Regressor.
* **Phân loại đa lớp (Classification):** Phân tầng mức độ cạnh tranh của các ngành học thành 4 phân khúc (Tiêu chuẩn, Trung bình, Cao, Rất cao).
* **Phân loại nhị phân (Binary Classification):** Dự báo ngành cạnh tranh cao (điểm chuẩn $\ge 24.0$) và phân tích đường cong ROC-AUC.
* **Đánh giá đặc trưng (Feature Importance):** Xác định các yếu tố chi phối mạnh nhất đến điểm chuẩn (Trường, Khu vực, Khối ngành, Khối thi, Thời gian).

---

## 2. Cấu trúc thư mục

```text
DataMining/
├── notebooks/
│   └── Data_Mining.ipynb      # File Jupyter Notebook thực nghiệm chi tiết từng bước
├── scripts/
│   ├── preprocess.py          # Tiền xử lý, lọc THPT, chuẩn hóa thang điểm và chia tập
│   ├── train_models.py        # Danh mục mô hình và huấn luyện (Decision Tree, RF, XGBoost, LightGBM)
│   ├── evaluate.py            # Tính toán các độ đo (MAE, RMSE, R2, F1, AUC) và vẽ biểu đồ
│   └── run_all.py             # Script chạy toàn bộ pipeline từ đầu đến cuối
├── results/                   # Thư mục lưu kết quả thực nghiệm
│   ├── data/                  # Dữ liệu sạch sau tiền xử lý
│   ├── images/                # Các biểu đồ kết quả (Confusion Matrix, ROC, Phân bố, Tầm quan trọng)
│   ├── models/                # Các mô hình học máy đã huấn luyện (.joblib)
│   ├── predictions_2025.csv   # Kết quả dự đoán trên tập kiểm thử năm 2025
│   └── metrics_summary.json   # Tổng hợp số liệu và chỉ số đánh giá của các mô hình
├── README.md                  # Tài liệu hướng dẫn
└── requirements.txt           # Danh sách các thư viện cần thiết
```

---

## 3. Hướng dẫn cài đặt và thực thi

### Bước 1: Cài đặt các thư viện cần thiết
```bash
pip install -r requirements.txt
```

### Bước 2: Chạy toàn bộ pipeline
Chạy lệnh sau tại thư mục `DataMining`:
```bash
python scripts/run_all.py
```

### Hoặc chạy trực quan trên Jupyter Notebook
Mở file `notebooks/Data_Mining.ipynb` trong Jupyter Lab / VS Code và nhấn **Run All** để theo dõi từng bước trực quan.
