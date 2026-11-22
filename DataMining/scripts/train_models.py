"""Cấu hình, huấn luyện và đánh giá mô hình học máy trên dữ liệu tuyển sinh."""
from pathlib import Path
import time
import joblib
import pandas as pd
from sklearn.base import clone
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.dummy import DummyClassifier, DummyRegressor
from xgboost import XGBClassifier, XGBRegressor
from lightgbm import LGBMClassifier

from preprocess import FEATURES, make_encoder
from evaluate import score_model

SEED = 42
TARGETS = {
    'regression': 'target_score',
    'classification': 'competition_class',
    'binary': 'is_high_score'
}


def model_catalog():
    """Danh mục các mô hình và tham số dùng chung cho toàn bộ đồ án."""
    return {
        'regression': {
            'Median baseline': DummyRegressor(strategy='median'),
            'Random Forest': RandomForestRegressor(
                n_estimators=100, max_depth=16, min_samples_leaf=3, n_jobs=1, random_state=SEED
            ),
            'XGBoost': XGBRegressor(
                n_estimators=100, max_depth=6, learning_rate=0.1, n_jobs=4, random_state=SEED
            ),
        },
        'classification': {
            'Majority baseline': DummyClassifier(strategy='most_frequent'),
            'Decision Tree': DecisionTreeClassifier(
                max_depth=12, min_samples_split=20, min_samples_leaf=10, random_state=SEED
            ),
            'Random Forest': RandomForestClassifier(
                n_estimators=100, max_depth=16, min_samples_split=10, n_jobs=1, random_state=SEED
            ),
            'XGBoost': XGBClassifier(
                n_estimators=100, max_depth=6, learning_rate=0.1, eval_metric='mlogloss', n_jobs=4, random_state=SEED
            ),
            'LightGBM': LGBMClassifier(
                n_estimators=100, max_depth=6, learning_rate=0.1, verbosity=-1, n_jobs=4, random_state=SEED
            ),
        },
        'binary': {
            'Decision Tree': DecisionTreeClassifier(
                max_depth=10, min_samples_leaf=5, random_state=SEED
            ),
            'Random Forest': RandomForestClassifier(
                n_estimators=100, max_depth=14, n_jobs=1, random_state=SEED
            ),
            'XGBoost': XGBClassifier(
                n_estimators=100, max_depth=6, learning_rate=0.1, eval_metric='logloss', n_jobs=4, random_state=SEED
            ),
        },
    }


def make_model(estimator):
    """Đóng gói bộ tiền xử lý và mô hình ước lượng thành một Pipeline hoàn chỉnh."""
    return Pipeline([
        ('preprocess', make_encoder()),
        ('model', clone(estimator))
    ])


def train_and_validate(splits, verbose=True):
    """Huấn luyện mô hình trên tập Train (<=2023) và đánh giá chọn lọc trên Validation (2024)."""
    trained = {}
    rows = []
    catalog = model_catalog()

    for task, estimators in catalog.items():
        trained[task] = {}
        for name, estimator in estimators.items():
            model = make_model(estimator)
            
            start_time = time.perf_counter()
            model.fit(splits['train'][FEATURES], splits['train'][TARGETS[task]])
            duration = time.perf_counter() - start_time
            
            trained[task][name] = model
            row = score_model(model, splits['validation'], task, name)
            row.update({'split': 'validation_2024', 'training_seconds': duration})
            rows.append(row)
            
            if verbose:
                print(f"Validation 2024 | {task:<14} | {name:<18}: {row}")

    metrics = pd.DataFrame(rows)
    
    # Chọn mô hình tốt nhất dựa trên tập kiểm định validation 2024
    winners = {}
    selection_criteria = [
        ('regression', 'MAE', True),
        ('classification', 'Macro F1', False),
        ('binary', 'ROC AUC', False)
    ]
    for task, metric_name, ascending in selection_criteria:
        eligible = metrics[(metrics['Task'] == task) & (~metrics['Model'].str.contains('baseline', case=False))]
        best_model_name = eligible.sort_values([metric_name, 'Model'], ascending=[ascending, True]).iloc[0]['Model']
        winners[task] = best_model_name

    return trained, metrics, winners


def refit_and_test(splits, validated, models_dir=None, verbose=True):
    """Huấn luyện lại trên toàn bộ lịch sử (Train + Val) và kiểm thử độc lập trên năm 2025."""
    history = pd.concat([splits['train'], splits['validation']], ignore_index=True)
    final_models = {}
    rows = []

    if models_dir is not None:
        models_path = Path(models_dir)
        models_path.mkdir(parents=True, exist_ok=True)

    for task, models in validated.items():
        final_models[task] = {}
        for name, configured_model in models.items():
            model = clone(configured_model)
            model.fit(history[FEATURES], history[TARGETS[task]])
            final_models[task][name] = model

            row = score_model(model, splits['test'], task, name)
            row['split'] = 'test_2025'
            rows.append(row)

            if models_dir is not None:
                save_name = f"{task}_{name.lower().replace(' ', '_')}.joblib"
                joblib.dump(model, Path(models_dir) / save_name, compress=3)

            if verbose:
                print(f"Test 2025       | {task:<14} | {name:<18}: {row}")

    return final_models, pd.DataFrame(rows)
