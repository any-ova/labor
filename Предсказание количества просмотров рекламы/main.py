import sys
import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.cluster import KMeans
import os

# Конфигурационные параметры
EPSILON = 0.005
TARGET_COLS = ['at_least_one', 'at_least_two', 'at_least_three']
output_path = os.path.join(os.getcwd(), 'predictions.tsv')


def load_data():
    """Загрузка данных с обработкой различных кодировок"""
    encodings = ['utf-8', 'utf-16', 'cp1251', 'latin1']
    for encoding in encodings:
        try:
            users = pd.read_csv('users.tsv', sep='\t', encoding=encoding)
            history = pd.read_csv('history.tsv', sep='\t', encoding=encoding)
            validate = pd.read_csv('validate.tsv', sep='\t', encoding=encoding)
            answers = pd.read_csv('validate_answers.tsv', sep='\t', encoding=encoding)
            return users, history, validate, answers
        except UnicodeDecodeError:
            continue
    raise ValueError("Не удалось загрузить файлы с поддерживаемыми кодировками")


def create_features(users, history, validate):
    """Создание расширенного набора признаков"""
    # Базовые признаки пользователя
    if 'user_ids' in validate.columns:
        validate = validate.rename(columns={'user_ids': 'user_id'})

    # Преобразование типов
    for df in [users, history, validate]:
        df['user_id'] = df['user_id'].astype(str)

    # 1. Статистики по истории просмотров
    user_stats = history.groupby('user_id').agg({
        'hour': ['count', 'nunique'],
        'cpm': ['mean', 'std', 'max', 'min'],
        'publisher': ['nunique']
    })
    user_stats.columns = ['_'.join(col).strip() for col in user_stats.columns.values]
    user_stats = user_stats.reset_index()

    # 2. Временные признаки
    history['hour_diff'] = history.groupby('user_id')['hour'].diff()
    time_stats = history.groupby('user_id')['hour_diff'].agg(['mean', 'max', 'std'])
    time_stats.columns = ['time_' + col for col in time_stats.columns]
    time_stats = time_stats.reset_index()

    # 3. Кластеризация пользователей
    cluster_features = history.groupby('user_id').agg({
        'hour': ['count', 'nunique'],
        'cpm': ['mean', 'std']
    })
    cluster_features.columns = ['cluster_' + '_'.join(col).strip() for col in cluster_features.columns.values]

    kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)  # Явно указали n_init
    cluster_features['user_cluster'] = kmeans.fit_predict(cluster_features.fillna(0))
    cluster_features = cluster_features.reset_index()

    # Объединение всех признаков
    features = validate.merge(users, on='user_id', how='left')
    for stats in [user_stats, time_stats, cluster_features]:
        features = features.merge(stats, on='user_id', how='left')

    # 4. Признаки кампании
    features['campaign_duration'] = features['hour_end'] - features['hour_start']
    features['publishers'] = features['publishers'].astype(str)
    features['publisher_count'] = features['publishers'].str.split(',').apply(len)

    # 5. Дополнительные преобразования
    features['audience_ratio'] = features['audience_size'] / (features['hour_count'] + 1)
    features['is_cold_user'] = (features['hour_count'].isna() | (features['hour_count'] == 0)).astype(int)

    # Заполнение пропусков
    fill_values = {
        'hour_count': 0,
        'hour_nunique': 0,
        'cpm_mean': features['cpm'].mean(),
        'cpm_std': 0,
        'cpm_max': features['cpm'].max(),
        'cpm_min': features['cpm'].min(),
        'publisher_nunique': 0,
        'time_mean': -1,
        'time_max': -1,
        'time_std': -1,
        'sex': -1,
        'age': -1,
        'city_id': -1
    }
    features.fillna(fill_values, inplace=True)

    # Удаляем текстовые колонки
    features = features.drop(columns=['publishers'])

    return features


def train_model(X_train, y_train, X_val, y_val, target_name):
    """Обучение модели с учетом специфики таргета"""
    # Преобразование в числовые типы
    X_train = X_train.apply(pd.to_numeric, errors='coerce')
    X_val = X_val.apply(pd.to_numeric, errors='coerce')
    X_train.fillna(0, inplace=True)
    X_val.fillna(0, inplace=True)

    params = {
        'objective': 'regression',
        'metric': 'mape',
        'num_leaves': 31 if target_name == 'at_least_one' else 15,
        'learning_rate': 0.01,
        'feature_fraction': 0.7,
        'verbosity': -1,
        'seed': 42
    }

    # Логарифмическое преобразование таргета
    y_train = np.log(y_train + EPSILON)
    y_val = np.log(y_val + EPSILON)

    model = lgb.LGBMRegressor(**params)
    model.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        callbacks=[lgb.early_stopping(100)]
    )
    return model


def postprocess_predictions(preds):
    """Постобработка предсказаний"""
    preds = np.exp(preds) - EPSILON
    preds = np.clip(preds, 0, 1)

    # Обеспечение монотонности
    preds[:, 1] = np.minimum(preds[:, 0], preds[:, 1])
    preds[:, 2] = np.minimum(preds[:, 1], preds[:, 2])

    return preds


def main():
    # 1. Загрузка данных
    users, history, validate, answers = load_data()

    # 2. Создание признаков
    features = create_features(users, history, validate)

    # 3. Подготовка данных
    feature_cols = [col for col in features.columns if col not in ['user_id', *TARGET_COLS]]
    X = features[feature_cols].select_dtypes(include=['number'])  # Только числовые колонки

    # 4. Обучение моделей для каждого таргета
    predictions = np.zeros((len(X), len(TARGET_COLS)))

    for i, target in enumerate(TARGET_COLS):
        y = answers[target]

        # Фильтрация выбросов для at_least_three
        if target == 'at_least_three':
            mask = y > 0.001
            X_filtered = X[mask]
            y_filtered = y[mask]
        else:
            X_filtered = X
            y_filtered = y

        # Разделение данных
        X_train, X_val, y_train, y_val = train_test_split(
            X_filtered, y_filtered, test_size=0.2, random_state=42
        )

        # Обучение модели
        model = train_model(X_train, y_train, X_val, y_val, target)

        # Предсказание
        preds = model.predict(X)
        predictions[:, i] = preds

    # 5. Постобработка
    predictions = postprocess_predictions(predictions)

    # 6. Сохранение результатов
    results = pd.DataFrame({
        'user_id': features['user_id'],
        'at_least_one': predictions[:, 0],
        'at_least_two': predictions[:, 1],
        'at_least_three': predictions[:, 2]
    })

    # Гарантированное сохранение без ошибок формата
    try:
        # Сначала сохраняем во временный файл
        temp_path = os.path.join(os.getcwd(), 'predictions_temp.tsv')
        results[TARGET_COLS].to_csv(temp_path, sep='\t', index=False, encoding='utf-8-sig')

        # Чистим файл от возможных проблем
        with open(temp_path, 'r', encoding='utf-8-sig') as f:
            lines = [line.strip() for line in f if line.strip()]

        # Пересохраняем окончательный файл
        with open(output_path, 'w', encoding='utf-8-sig') as f:
            f.write('\n'.join(lines))

        # Удаляем временный файл
        os.remove(temp_path)

        print(f"Файл успешно сохранён: {output_path}")
        print("Первые 3 строки файла:")
        with open(output_path, 'r', encoding='utf-8-sig') as f:
            for i, line in enumerate(f):
                if i >= 3: break
                print(line.strip())
    except Exception as e:
        print(f"Ошибка сохранения: {str(e)}", file=sys.stderr)
        sys.exit(1)
if __name__ == "__main__":
    main()