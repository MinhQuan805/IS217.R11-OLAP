"""Quy trình thực thi toàn diện Data Mining tuyển sinh theo thời gian (End-to-End Pipeline)."""
from pathlib import Path
import argparse
import importlib.metadata
import json
import platform
import numpy as np
import pandas as pd

from preprocess import (
    MINING_DIR, SCORES_PATH, MAJORS_PATH, FEATURES, GRAIN,
    load_and_preprocess_data, split_dataset
)
from train_models import train_and_validate, refit_and_test, model_catalog
from evaluate import previous_year_baseline, plot_eda, plot_results

OUTPUT_DIR = MINING_DIR / 'results'


def json_clean(value):
    """Làm sạch các cấu trúc dữ liệu để tuần tự hóa JSON an toàn."""
    if isinstance(value, dict):
        return {str(k): json_clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_clean(x) for x in value]
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, float) and not np.isfinite(value):
        return None
    return value


def export_summary(df, audit, splits, val_metrics, test_metrics, winners, importance, output_dir):
    """Xuất file JSON tổng hợp toàn bộ thông số thực nghiệm, chỉ số đánh giá và phiên bản thư viện."""
    out_path = Path(output_dir)
    catalog = {task: {name: m.get_params() for name, m in models.items()} for task, models in model_catalog().items()}

    summary = {
        'schema_version': 2,
        'source': audit,
        'features': FEATURES,
        'grain': GRAIN,
        'protocol': {
            'train': '2010-2023',
            'validation': '2024',
            'test': '2025',
            'final_refit': '2010-2024',
            'selection': 'Regression: validation MAE; classification: validation Macro F1; binary: validation ROC AUC',
            'lag': 'Chỉ lấy đúng năm liền trước cho cùng trường, ngành, tổ hợp xét tuyển',
            'target': 'score_converted_mark trong khoảng điểm [10, 30]'
        },
        'split_sizes': {k: len(v) for k, v in splits.items()},
        'selected_models_from_validation': winners,
        'validation_metrics': val_metrics.to_dict('records'),
        'test_metrics': test_metrics.to_dict('records'),
        'feature_importance_validation': importance.to_dict('records'),
        'model_parameters': catalog,
        'versions': {pkg: importlib.metadata.version(pkg) for pkg in ['pandas', 'numpy', 'scikit-learn', 'xgboost', 'lightgbm', 'matplotlib', 'joblib']},
        'python_version': platform.python_version(),
        'limitations': [
            'Thực nghiệm ngoại tuyến trên dữ liệu lịch sử, không phải thử nghiệm tương lai thời gian thực.',
            'Cột điểm quy đổi dựa trên công thức và ghi chú tuyển sinh hiện có.',
            'Ánh xạ nhóm ngành giữ trạng thái chưa xác định đối với các mã ngành chưa rõ ràng.',
            'Mã hóa thứ tự cho biến định danh tạo thứ tự ngầm định.',
            'Dữ liệu nghiên cứu giới hạn trong thang điểm [10, 30] của phương thức THPT.',
            'Độ quan trọng đặc trưng thể hiện mối liên hệ tương quan, không mang tính nhân quả tuyệt đối.'
        ]
    }
    summary = json_clean(summary)
    (out_path / 'metrics_summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')
    return summary


def run_pipeline(output_dir=OUTPUT_DIR, scores_path=SCORES_PATH, majors_path=MAJORS_PATH):
    """Thực thi pipeline hoàn chỉnh: Nạp dữ liệu -> Tiền xử lý -> Huấn luyện -> Đánh giá -> Xuất báo cáo."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("BƯỚC 1: TIỀN XỬ LÝ VÀ CHIA TẬP DỮ LIỆU")
    print("=" * 80)
    df, audit = load_and_preprocess_data(scores_path, majors_path, output_dir / 'data')
    splits = split_dataset(df)
    plot_eda(df, output_dir / 'images')

    print("\n" + "=" * 80)
    print("BƯỚC 2: HUẤN LUYỆN VÀ CHỌN LỰA MÔ HÌNH TRÊN VALIDATION 2024")
    print("=" * 80)
    validated, val_metrics, winners = train_and_validate(splits)
    val_baseline = previous_year_baseline(splits['train'], splits['validation'])
    val_baseline['split'] = 'validation_2024'
    val_metrics = pd.concat([val_metrics, pd.DataFrame([val_baseline])], ignore_index=True)

    print("\n" + "=" * 80)
    print("BƯỚC 3: HUẤN LUYỆN LẠI VÀ ĐÁNH GIÁ ĐỘC LẬP TRÊN TEST 2025")
    print("=" * 80)
    final_models, test_metrics = refit_and_test(splits, validated, output_dir / 'models')
    history = pd.concat([splits['train'], splits['validation']], ignore_index=True)
    test_baseline = previous_year_baseline(history, splits['test'])
    test_baseline['split'] = 'test_2025'
    test_metrics = pd.concat([test_metrics, pd.DataFrame([test_baseline])], ignore_index=True)

    print("\n" + "=" * 80)
    print("BƯỚC 4: VẼ BIỂU ĐỒ VÀ XUẤT CÁC BẢNG KẾT QUẢ")
    print("=" * 80)
    preds, class_report, importance = plot_results(final_models, validated, splits, val_metrics, test_metrics, winners, output_dir / 'images')

    # Lưu file CSV kết quả dự đoán năm 2025
    preds.to_csv(output_dir / 'predictions_2025.csv', index=False, encoding='utf-8-sig')

    summary = export_summary(df, audit, splits, val_metrics, test_metrics, winners, importance, output_dir)

    print("\n" + "=" * 80)
    print("TỔNG KẾT KẾT QUẢ THỰC NGHIỆM:")
    print("Mô hình được chọn từ validation:", winners)
    print("-" * 80)
    print(test_metrics.to_string(index=False))
    print(f"\nToàn bộ kết quả đã được lưu tại: {output_dir}")
    print("=" * 80)
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Pipeline Data Mining Tuyển sinh")
    parser.add_argument('--output-dir', type=Path, default=OUTPUT_DIR, help="Thư mục xuất kết quả")
    parser.add_argument('--scores', type=Path, default=SCORES_PATH, help="Đường dẫn file điểm chuẩn")
    parser.add_argument('--majors', type=Path, default=MAJORS_PATH, help="Đường dẫn file danh mục ngành")
    args = parser.parse_args()
    run_pipeline(args.output_dir, args.scores, args.majors)
