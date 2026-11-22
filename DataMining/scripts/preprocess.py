"""Tiền xử lý dữ liệu tuyển sinh có kiểm soát và chia tập theo thời gian."""
from pathlib import Path
import hashlib
import re
import unicodedata
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder

# Đường dẫn và cấu hình các thuộc tính
MINING_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = MINING_DIR.parent
SCORES_PATH = PROJECT_DIR / 'Data/cleaned/cleaned-cutoff-scores.csv'
MAJORS_PATH = PROJECT_DIR / 'Data/cleaned/cleaned-majors.csv'

CLASS_NAMES = ['Dưới 18', 'Từ 18 đến dưới 22', 'Từ 22 đến dưới 25', 'Từ 25 trở lên']
CATEGORICAL_FEATURES = ['school_id', 'school_type', 'province_name', 'program_name', 'major_groups', 'block_set']
NUMERIC_FEATURES = ['score_year', 'previous_year_score', 'has_previous_year_score']
FEATURES = CATEGORICAL_FEATURES + NUMERIC_FEATURES

PROGRAM_KEY = ['school_id', 'score_code', 'program_name', 'block_set']
GRAIN = PROGRAM_KEY + ['score_year', 'score_admission_name']


def normalize_text(value):
    """Chuẩn hóa văn bản: Unicode NFKC, chữ thường và bỏ khoảng trắng thừa."""
    if pd.isna(value):
        return ''
    cleaned = unicodedata.normalize('NFKC', str(value)).casefold()
    return re.sub(r'\s+', ' ', cleaned).strip()


def normalize_blocks(value):
    """Chuẩn hóa danh sách khối xét tuyển thành chuỗi phân tách bởi dấu chấm phẩy."""
    if pd.isna(value):
        return 'Chưa xác định'
    parts = re.split(r'[;,]', str(value))
    valid_codes = sorted({p.strip().upper() for p in parts if re.fullmatch(r'[A-Za-z]\d{2,3}', p.strip())})
    return ';'.join(valid_codes) if valid_codes else 'Chưa xác định'


def major_candidates(majors_df):
    """Tạo bảng tra cứu mã ngành sang bộ (tên ngành, nhóm ngành)."""
    candidates = {}
    for row in majors_df.itertuples():
        for code in str(row.score_codes).split(';'):
            code = code.strip()
            if code and code != 'nan':
                norm_name = normalize_text(row.major_name)
                candidates.setdefault(code, set()).add((norm_name, str(row.major_group_name)))
    return candidates


def resolve_major(code, program_name, candidates):
    """Khớp nhóm ngành dựa trên mã và tên ngành để tránh gán nhầm."""
    options = candidates.get(str(code).strip(), set())
    exact_matches = {group for name, group in options if name == program_name}
    if exact_matches:
        return ' | '.join(sorted(exact_matches)), 'Khớp mã và tên'
    
    unique_names = {name for name, _ in options}
    if len(unique_names) == 1:
        return ' | '.join(sorted({g for _, g in options})), 'Mã có một tên ngành'
    if options:
        return 'Chưa xác định', 'Mã nhiều tên ngành, chưa khớp tên'
    return 'Chưa xác định', 'Không có mã trong danh mục'


def add_history_features(df):
    """Nối điểm chuẩn của đúng năm liền trước cho từng ngành của từng trường."""
    history = df[PROGRAM_KEY + ['score_year', 'target_score']].copy()
    history['score_year'] += 1
    history = history.rename(columns={'target_score': 'previous_year_score'})
    
    merged = df.merge(history, on=PROGRAM_KEY + ['score_year'], how='left', validate='one_to_one')
    merged['has_previous_year_score'] = merged['previous_year_score'].notna().astype(int)
    return merged


def load_and_preprocess_data(scores_path=SCORES_PATH, majors_path=MAJORS_PATH, output_dir=None):
    """Nạp, làm sạch và chuẩn hóa dữ liệu tuyển sinh có kiểm soát chất lượng."""
    scores_path, majors_path = Path(scores_path), Path(majors_path)
    raw = pd.read_csv(scores_path, dtype={'school_id': str, 'score_code': str})
    majors = pd.read_csv(majors_path)

    # 1. Lọc phương thức xét tuyển Điểm thi THPT
    df = raw[raw['score_admission_name'] == 'Điểm thi THPT'].copy()
    thpt_rows = len(df)
    duplicates_removed = int(df.duplicated().sum())
    df = df.drop_duplicates().copy()

    # 2. Chuẩn hóa trường dữ liệu
    df['source_row'] = df.index + 2
    df['target_score'] = pd.to_numeric(df['score_converted_mark'], errors='coerce')
    df['score_year'] = pd.to_numeric(df['score_year'], errors='coerce')
    df['program_name'] = df['score_name'].map(normalize_text)
    df['block_set'] = df['score_blocks'].map(normalize_blocks)

    for col in ['school_id', 'score_code', 'school_type', 'province_name']:
        df[col] = df[col].fillna('Chưa xác định').astype(str).str.strip()

    # 3. Kiểm tra tính hợp lệ về thang điểm và ghi chú
    note = df['score_introtext'].fillna('').map(normalize_text)
    weighted = note.str.contains(r'nhân|hệ số|thang\s*(?:điểm\s*)?40', regex=True)
    already_converted = note.str.contains(r'đã.*quy đổi|quy đổi.*30', regex=True)
    score_changed = ~np.isclose(pd.to_numeric(df['score_mark'], errors='coerce'), df['target_score'], equal_nan=False)
    uncertain_scale = weighted & ~score_changed & ~already_converted
    mixed_method = note.str.contains(r'\bhsa\b|v-act|\btsa\b|đánh giá năng lực|đánh giá tư duy', regex=True)

    reasons = pd.Series('', index=df.index)
    def flag(mask, msg):
        reasons.loc[mask] = reasons.loc[mask].apply(lambda x: (x + '; ' if x else '') + msg)

    flag(~df['target_score'].between(10, 30), 'Điểm ngoài phạm vi [10, 30] hoặc thiếu')
    flag(~df['score_year'].between(2010, 2025) | df['score_year'].mod(1).ne(0), 'Năm không hợp lệ')
    flag(df['program_name'].eq('') | df['school_id'].eq('Chưa xác định') | df['score_code'].eq('Chưa xác định'), 'Thiếu định danh')
    flag(uncertain_scale, 'Ghi chú hệ số chưa xác nhận quy đổi')
    flag(mixed_method, 'Ghi chú có phương thức kết hợp')

    valid_mask = reasons.eq('')
    quarantine = df[~valid_mask].copy()
    quarantine['exclusion_reason'] = reasons[~valid_mask]
    df = df[valid_mask].copy()
    df['score_year'] = df['score_year'].astype(int)

    # 4. Loại bỏ các bản ghi trùng khóa nhưng lệch điểm (conflict grain)
    conflicts = df.groupby(GRAIN, dropna=False)['target_score'].transform('nunique') > 1
    conflicting = df[conflicts].copy()
    conflicting['exclusion_reason'] = 'Cùng khóa nhưng có nhiều điểm khác nhau'
    df = df[~conflicts].copy()

    same_grain_dups = int(df.duplicated(GRAIN).sum())
    df = df.sort_values('source_row').drop_duplicates(GRAIN).copy()

    # 5. Ánh xạ nhóm ngành và tạo nhãn mục tiêu
    candidates = major_candidates(majors)
    mapping = [resolve_major(c, n, candidates) for c, n in zip(df['score_code'], df['program_name'])]
    df[['major_groups', 'major_mapping_status']] = pd.DataFrame(mapping, index=df.index)

    df['competition_class'] = np.searchsorted([18.0, 22.0, 25.0], df['target_score'], side='right')
    df['competition_label'] = df['competition_class'].map(dict(enumerate(CLASS_NAMES)))
    df['is_high_score'] = df['target_score'].ge(24).astype(int)

    # 6. Thêm đặc trưng lịch sử và mã định danh duy nhất
    df = add_history_features(df).sort_values(['score_year'] + PROGRAM_KEY).reset_index(drop=True)
    df['record_id'] = pd.util.hash_pandas_object(df[GRAIN], index=False).astype(str)

    # Tổng hợp nhật ký audit
    audit = {
        'source_path': str(scores_path.resolve()),
        'source_sha256': hashlib.sha256(scores_path.read_bytes()).hexdigest(),
        'majors_path': str(majors_path.resolve()),
        'majors_sha256': hashlib.sha256(majors_path.read_bytes()).hexdigest(),
        'source_rows': len(raw),
        'source_columns': raw.columns.tolist(),
        'source_missing': raw.isna().sum().to_dict(),
        'thpt_rows': thpt_rows,
        'exact_duplicates_removed': duplicates_removed,
        'quality_excluded_rows': len(quarantine),
        'quality_exclusion_reasons': quarantine['exclusion_reason'].value_counts().to_dict(),
        'conflicting_score_rows_excluded': len(conflicting),
        'conflicting_grain_count': len(conflicting[GRAIN].drop_duplicates()),
        'same_grain_same_score_duplicates_removed': same_grain_dups,
        'major_mapping_status': df['major_mapping_status'].value_counts().to_dict(),
        'final_rows': len(df),
        'year_counts': df['score_year'].value_counts().sort_index().to_dict(),
        'score_statistics': df['target_score'].describe().to_dict(),
        'class_counts': df['competition_label'].value_counts().to_dict(),
        'missing_blocks': int(df['block_set'].eq('Chưa xác định').sum()),
        'previous_year_coverage': float(df['has_previous_year_score'].mean()),
        'remaining_duplicate_grains': int(df.duplicated(GRAIN).sum())
    }

    # Xuất file kiểm toán nếu được chỉ định
    if output_dir is not None:
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)
        df.to_csv(out_path / 'dataset_mining.csv', index=False, encoding='utf-8-sig')
        pd.concat([quarantine, conflicting], ignore_index=True).to_csv(out_path / 'excluded_records.csv', index=False, encoding='utf-8-sig')
        unresolved = df[df['major_mapping_status'].str.contains('chưa|Không', case=False, na=False)]
        unresolved[['school_id', 'score_code', 'score_name', 'major_mapping_status']].drop_duplicates().to_csv(
            out_path / 'unresolved_major_mapping.csv', index=False, encoding='utf-8-sig'
        )

    print(f"Nguồn: {len(raw):,}; THPT: {thpt_rows:,}; tập nghiên cứu: {len(df):,}")
    return df, audit


def split_dataset(df):
    """Chia tập dữ liệu theo thời gian: Train (<=2023), Validation (2024), Test (2025)."""
    train = df[df['score_year'] <= 2023].copy()
    validation = df[df['score_year'] == 2024].copy()
    test = df[df['score_year'] == 2025].copy()

    if train.empty or validation.empty or test.empty:
        raise ValueError('Dữ liệu cần có đủ tập train <=2023, validation 2024 và test 2025.')

    print(f"Train <=2023: {len(train):,}; validation 2024: {len(validation):,}; test 2025: {len(test):,}")
    return {'train': train, 'validation': validation, 'test': test}


def make_encoder():
    """Tạo bộ tiền xử lý ColumnTransformer mã hóa dữ liệu đầu vào."""
    categorical_pipe = Pipeline([
        ('impute', SimpleImputer(strategy='constant', fill_value='Chưa xác định')),
        ('encode', OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1))
    ])
    return ColumnTransformer([
        ('categorical', categorical_pipe, CATEGORICAL_FEATURES),
        ('numeric', SimpleImputer(strategy='median', keep_empty_features=True), NUMERIC_FEATURES)
    ], verbose_feature_names_out=False)
