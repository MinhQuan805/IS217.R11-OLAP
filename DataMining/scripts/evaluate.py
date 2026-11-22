"""Hàm tính toán chỉ số đánh giá và vẽ biểu đồ kết quả trực quan."""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.inspection import permutation_importance
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, roc_auc_score, roc_curve,
    mean_absolute_error, mean_squared_error, r2_score
)
from preprocess import CLASS_NAMES, FEATURES

# Cấu hình thẩm mỹ cho biểu đồ
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10, 'axes.unicode_minus': False})
sns.set_style('whitegrid')


def regression_metrics(actual, predicted):
    """Tính toán MAE, RMSE và R² cho bài toán hồi quy."""
    return {
        'MAE': float(mean_absolute_error(actual, predicted)),
        'RMSE': float(np.sqrt(mean_squared_error(actual, predicted))),
        'R2': float(r2_score(actual, predicted))
    }


def score_model(model, df, task, name):
    """Chấm điểm toàn diện cho một mô hình theo bài toán tương ứng."""
    target_col = {
        'regression': 'target_score',
        'classification': 'competition_class',
        'binary': 'is_high_score'
    }[task]
    
    y_true = df[target_col]
    y_pred = model.predict(df[FEATURES])
    row = {'Task': task, 'Model': name, 'Samples': len(df)}

    if task == 'regression':
        row.update(regression_metrics(y_true, y_pred))
    else:
        row.update({
            'Accuracy': float(accuracy_score(y_true, y_pred)),
            'Macro Precision': float(precision_score(y_true, y_pred, average='macro', zero_division=0)),
            'Macro Recall': float(recall_score(y_true, y_pred, average='macro', zero_division=0)),
            'Macro F1': float(f1_score(y_true, y_pred, average='macro', zero_division=0)),
            'Weighted F1': float(f1_score(y_true, y_pred, average='weighted', zero_division=0))
        })
        if task == 'binary' and y_true.nunique() > 1:
            y_prob = model.predict_proba(df[FEATURES])[:, 1]
            row['ROC AUC'] = float(roc_auc_score(y_true, y_prob))
        elif task == 'binary':
            row['ROC AUC'] = None

    return row


def previous_year_baseline(history, future):
    """Mô hình cơ sở dự đoán bằng đúng điểm chuẩn năm trước (nếu thiếu dùng trung vị)."""
    fallback_score = float(history['target_score'].median())
    predictions = future['previous_year_score'].fillna(fallback_score).to_numpy()
    metrics = regression_metrics(future['target_score'], predictions)
    return {
        'Task': 'regression',
        'Model': 'Previous year baseline',
        'Samples': len(future),
        **metrics
    }


def save_figure(fig, directory, filename):
    """Lưu biểu đồ chất lượng cao và đóng figure giải phóng bộ nhớ."""
    dir_path = Path(directory)
    dir_path.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(dir_path / filename, dpi=180, bbox_inches='tight')
    plt.close(fig)


def plot_eda(df, directory):
    """Vẽ các biểu đồ phân tích khám phá dữ liệu (EDA)."""
    # 1. Phân bố điểm chuẩn
    fig, ax = plt.subplots(figsize=(9, 4))
    sns.histplot(df['target_score'], bins=35, color='#2563eb', ax=ax)
    for threshold in [18, 22, 25]:
        ax.axvline(threshold, color='#ef4444', linestyle='--', linewidth=1)
    ax.set(title='Phân bố điểm chuẩn quy đổi trong tập nghiên cứu', xlabel='Điểm', ylabel='Số bản ghi')
    save_figure(fig, directory, '01_score_distribution.png')

    # 2. Số lượng bản ghi theo năm
    fig, ax = plt.subplots(figsize=(9, 4))
    df.groupby('score_year').size().plot.bar(ax=ax, color='#2563eb')
    ax.set(title='Số bản ghi theo năm sau tiền xử lý', xlabel='Năm', ylabel='Số bản ghi')
    save_figure(fig, directory, '02_records_by_year.png')

    # 3. Phân bố các nhóm mức độ cạnh tranh
    fig, ax = plt.subplots(figsize=(9, 4))
    df['competition_class'].value_counts().reindex(range(4), fill_value=0).plot.bar(ax=ax, color='#10b981')
    ax.set_xticklabels(['<18', '[18,22)', '[22,25)', '>=25'], rotation=0)
    ax.set(title='Phân bố nhóm điểm theo quy ước của đồ án', xlabel='Nhóm điểm', ylabel='Số bản ghi')
    save_figure(fig, directory, '03_class_distribution.png')


def plot_results(final_models, validation_models, splits, validation_metrics, test_metrics, winners, directory):
    """Vẽ toàn bộ biểu đồ kết quả đánh giá thực nghiệm trên tập kiểm thử 2025."""
    test_df = splits['test']
    best_reg_model = final_models['regression'][winners['regression']]

    # 1. Đồ thị Thực tế vs Dự đoán & Phân bố sai số hồi quy
    preds = test_df[['record_id', 'school_id', 'score_code', 'score_name', 'score_year', 'target_score', 'previous_year_score']].copy()
    preds['predicted_score'] = best_reg_model.predict(test_df[FEATURES]).astype(np.float64)
    preds['error'] = preds['predicted_score'] - preds['target_score']

    fig, ax = plt.subplots(figsize=(7, 6))
    sample = preds.sample(min(2500, len(preds)), random_state=42)
    ax.scatter(sample['target_score'], sample['predicted_score'], s=10, alpha=0.25, color='#2563eb')
    ax.plot([10, 30], [10, 30], '--', color='#ef4444')
    ax.set(xlim=(10, 30), ylim=(10, 30), xlabel='Điểm thực tế', ylabel='Điểm dự đoán', title=f"Test 2025 - {winners['regression']}")
    save_figure(fig, directory, '04_actual_vs_predicted.png')

    fig, ax = plt.subplots(figsize=(9, 4))
    sns.histplot(preds['error'], bins=35, ax=ax, color='#2563eb')
    ax.axvline(0, color='#ef4444', linestyle='--')
    ax.set(title='Phân bố sai số trên test 2025', xlabel='Dự đoán - thực tế (điểm)', ylabel='Số bản ghi')
    save_figure(fig, directory, '05_residual_distribution.png')

    # 2. So sánh MAE các mô hình hồi quy
    reg_summary = test_metrics[test_metrics['Task'] == 'regression'].sort_values('MAE', ascending=False)
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.barh(reg_summary['Model'], reg_summary['MAE'], color='#2563eb')
    ax.set(title='So sánh hồi quy và baseline trên test 2025', xlabel='MAE (điểm; thấp hơn tốt hơn)')
    save_figure(fig, directory, '06_regression_comparison.png')

    # 3. Ma trận nhầm lẫn cho từng mô hình phân loại
    class_rows = []
    for name, model in final_models['classification'].items():
        if 'baseline' in name.lower():
            continue
        y_pred = model.predict(test_df[FEATURES])
        cm = confusion_matrix(test_df['competition_class'], y_pred, labels=[0, 1, 2, 3])

        fig, ax = plt.subplots(figsize=(6, 5))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False, ax=ax,
                    xticklabels=['<18', '18-<22', '22-<25', '>=25'],
                    yticklabels=['<18', '18-<22', '22-<25', '>=25'])
        ax.set(title=f"{name} - Test 2025", xlabel='Nhóm dự đoán', ylabel='Nhóm thực tế')
        save_figure(fig, directory, f"07_confusion_{name.lower().replace(' ', '_')}.png")

        for label in [0, 1, 2, 3]:
            mask = test_df['competition_class'] == label
            class_rows.append({
                'Model': name,
                'Class': CLASS_NAMES[label],
                'Support': int(mask.sum()),
                'Recall': float(np.mean(y_pred[mask] == label))
            })

    # 4. So sánh Accuracy và Macro F1 các mô hình phân loại
    cls_summary = test_metrics[test_metrics['Task'] == 'classification']
    fig, ax = plt.subplots(figsize=(9, 4))
    x_pos = np.arange(len(cls_summary))
    ax.bar(x_pos - 0.18, cls_summary['Accuracy'], width=0.36, label='Accuracy', color='#2563eb')
    ax.bar(x_pos + 0.18, cls_summary['Macro F1'], width=0.36, label='Macro F1', color='#10b981')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(cls_summary['Model'], rotation=15)
    ax.set_ylim(0, 1)
    ax.legend()
    ax.set(title='Phân loại nhóm điểm - Test 2025', ylabel='Điểm đánh giá')
    save_figure(fig, directory, '08_classification_comparison.png')

    # 5. Đường cong ROC cho bài toán phân loại nhị phân (ngành >= 24 điểm)
    fig, ax = plt.subplots(figsize=(7, 5))
    for name, model in final_models['binary'].items():
        if test_df['is_high_score'].nunique() < 2:
            continue
        y_prob = model.predict_proba(test_df[FEATURES])[:, 1]
        fpr, tpr, _ = roc_curve(test_df['is_high_score'], y_prob)
        auc_score = roc_auc_score(test_df['is_high_score'], y_prob)
        ax.plot(fpr, tpr, label=f"{name}: AUC={auc_score:.4f}")

    ax.plot([0, 1], [0, 1], '--', color='gray')
    ax.legend()
    ax.set(title='Bài toán riêng: điểm >=24 - Test 2025', xlabel='False positive rate', ylabel='True positive rate')
    save_figure(fig, directory, '09_binary_roc.png')

    # 6. Tầm quan trọng của các đặc trưng (Permutation Importance trên tập validation 2024)
    best_val_model = validation_models['regression'][winners['regression']]
    val_sample = splits['validation'].sample(min(2500, len(splits['validation'])), random_state=42)
    imp_result = permutation_importance(
        best_val_model, val_sample[FEATURES], val_sample['target_score'],
        scoring='neg_mean_absolute_error', n_repeats=5, random_state=42, n_jobs=1
    )
    importance_df = pd.DataFrame({
        'Feature': FEATURES,
        'MAE increase': imp_result.importances_mean,
        'Std': imp_result.importances_std
    }).sort_values('MAE increase')

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.barh(importance_df['Feature'], importance_df['MAE increase'], xerr=importance_df['Std'], color='#10b981')
    ax.set(title=f"Permutation Importance - Validation 2024 - {winners['regression']}", xlabel='Mức tăng MAE khi xáo trộn (điểm)')
    save_figure(fig, directory, '10_validation_feature_importance.png')

    return preds, pd.DataFrame(class_rows), importance_df
