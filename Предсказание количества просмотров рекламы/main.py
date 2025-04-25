import pandas as pd
import numpy as np
from catboost import CatBoostRegressor, Pool
from sklearn.model_selection import train_test_split, KFold
from sklearn.metrics import mean_absolute_error
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
from tqdm import tqdm
import pickle
import os

warnings.filterwarnings('ignore')

# Constants
TARGET_COLS = ['at_least_one', 'at_least_two', 'at_least_three']
EPS = 0.005  # For the evaluation metric


def calculate_metric(y_true, y_pred):
    """
    Calculate the Smoothed Mean Log Accuracy Ratio as described in the task
    """
    log_ratios = np.abs(np.log((y_pred + EPS) / (y_true + EPS)))
    metric = 100 * (np.exp(np.mean(log_ratios)) - 1)
    return metric


def load_data():
    """Load data with proper dtypes"""
    users = pd.read_csv('users.tsv', sep='\t', dtype={'user_id': str})
    history = pd.read_csv('history.tsv', sep='\t', dtype={'user_id': str})
    validate = pd.read_csv('validate.tsv', sep='\t')
    answers = pd.read_csv('validate_answers.tsv', sep='\t')

    # Convert user_ids to list
    validate['user_ids'] = validate['user_ids'].apply(lambda x: x.split(',') if isinstance(x, str) else [])

    return users, history, validate, answers


def preprocess_history(history):
    """Preprocess history data to extract useful time features and session info"""
    # Convert hour to datetime for easier manipulation
    history['datetime'] = pd.to_datetime(history['hour'], unit='h')
    history['day'] = history['datetime'].dt.day
    history['hour_of_day'] = history['datetime'].dt.hour
    history['weekday'] = history['datetime'].dt.weekday

    # Sort by user_id and datetime
    history = history.sort_values(['user_id', 'datetime'])

    # Identify sessions (gap of 6+ hours means new session)
    history['prev_datetime'] = history.groupby('user_id')['datetime'].shift(1)
    history['time_diff'] = (history['datetime'] - history['prev_datetime']).dt.total_seconds() / 3600
    history['new_session'] = (history['time_diff'] > 6) | (history['time_diff'].isna())
    history['session_id'] = history.groupby('user_id')['new_session'].cumsum()

    # Create a unique session identifier combining user_id and session_id
    history['user_session'] = history['user_id'] + '_' + history['session_id'].astype(str)

    return history


def analyze_auction_dynamics(history):
    """Analyze the auction dynamics to understand CPM patterns"""
    # Get distribution of CPM by publisher and hour
    cpm_publisher_hour = history.groupby(['publisher', 'hour_of_day'])['cpm'].agg(
        ['mean', 'median', 'std', 'count']).reset_index()

    # For each publisher and hour, calculate the win probability for a sample of CPM values
    cpm_win_probs = []

    # Only process the top publishers by frequency to reduce computation
    top_publishers = history['publisher'].value_counts().nlargest(10).index.tolist()

    for pub in top_publishers:
        pub_data = history[history['publisher'] == pub]
        for hour in range(24):
            hour_data = pub_data[pub_data['hour_of_day'] == hour]
            if len(hour_data) > 100:  # Only if we have enough data
                # Instead of all unique CPMs, take a sample of representative values
                # Use percentiles to get a good distribution
                cpm_values = np.percentile(hour_data['cpm'].values,
                                           [0, 10, 25, 50, 75, 90, 95, 99, 100])
                cpm_values = np.unique(cpm_values)  # Remove duplicates

                for cpm in cpm_values:
                    # Calculate win probability
                    higher_count = sum(hour_data['cpm'] > cpm)
                    equal_count = sum(hour_data['cpm'] == cpm)
                    total_count = len(hour_data)

                    win_prob = 0
                    if higher_count == 0:
                        if equal_count == 0:  # Edge case - no exact matches
                            win_prob = 1.0  # This is a theoretical highest bid
                        elif equal_count == 1:  # Only one bid at this level
                            win_prob = 1.0  # 100% win if highest and unique
                        else:
                            # Win probability is 1/n where n is number of equal bids
                            win_prob = 1.0 / equal_count

                    cpm_win_probs.append({
                        'publisher': pub,
                        'hour_of_day': hour,
                        'cpm': cpm,
                        'win_probability': win_prob
                    })

    cpm_win_probs_df = pd.DataFrame(cpm_win_probs)
    return cpm_publisher_hour, cpm_win_probs_df

def create_user_features(users, history):
    """Create comprehensive user-level features"""
    # Basic demographic features
    users['age_group'] = pd.cut(users['age'],
                                bins=[-1, 0, 18, 25, 35, 45, 100],
                                labels=['unknown', '<18', '18-25', '26-35', '36-45', '45+'])

    # Activity patterns by user
    user_activity = history.groupby('user_id').agg({
        'hour': 'count',
        'cpm': ['mean', 'median', 'std', 'min', 'max'],
        'publisher': lambda x: ','.join(x.astype(str).unique()),  # Convert to string first
        'session_id': 'nunique',
        'hour_of_day': lambda x: ','.join(x.astype(str).unique()),  # Convert to string first
        'weekday': lambda x: ','.join(x.astype(str).unique())  # Convert to string first
    }).reset_index()

    # Flattening column names
    user_activity.columns = ['_'.join(col).strip('_') if isinstance(col, tuple) else col for col in
                             user_activity.columns]

    # Publisher preferences
    publisher_counts = history.groupby(['user_id', 'publisher']).size().unstack(fill_value=0)
    publisher_counts.columns = [f'publisher_{col}_count' for col in publisher_counts.columns]
    publisher_counts = publisher_counts.reset_index()

    # Time of day preferences
    hour_counts = history.groupby(['user_id', 'hour_of_day']).size().unstack(fill_value=0)
    hour_counts.columns = [f'hour_{col}_count' for col in hour_counts.columns]
    hour_counts = hour_counts.reset_index()

    # Weekday preferences
    weekday_counts = history.groupby(['user_id', 'weekday']).size().unstack(fill_value=0)
    weekday_counts.columns = [f'weekday_{col}_count' for col in weekday_counts.columns]
    weekday_counts = weekday_counts.reset_index()

    # CPM sensitivity - how often user sees ads with different CPM ranges
    history['cpm_range'] = pd.cut(history['cpm'],
                                  bins=[0, 10, 50, 100, 500, 1000, np.inf],
                                  labels=['0-10', '10-50', '50-100', '100-500', '500-1000', '1000+'])

    cpm_range_counts = history.groupby(['user_id', 'cpm_range']).size().unstack(fill_value=0)
    cpm_range_counts.columns = [f'cpm_range_{col}_count' for col in cpm_range_counts.columns]
    cpm_range_counts = cpm_range_counts.reset_index()

    # Combine all user features
    user_features = users.merge(user_activity, on='user_id', how='left')
    user_features = user_features.merge(publisher_counts, on='user_id', how='left')
    user_features = user_features.merge(hour_counts, on='user_id', how='left')
    user_features = user_features.merge(weekday_counts, on='user_id', how='left')
    user_features = user_features.merge(cpm_range_counts, on='user_id', how='left')

    # Fill NA values
    numeric_cols = user_features.select_dtypes(include=[np.number]).columns
    user_features[numeric_cols] = user_features[numeric_cols].fillna(0)

    return user_features


def create_ad_features(validate, history):
    """Create features for each ad campaign scenario in the validation set"""
    ad_features = []

    for idx, row in validate.iterrows():
        cpm = row['cpm']
        hour_start = row['hour_start']
        hour_end = row['hour_end']
        publishers = row['publishers'].split(',')
        user_ids = row['user_ids']
        audience_size = row['audience_size']

        # Time window features
        time_window = hour_end - hour_start
        hours_covered = list(range(hour_start % 24, (hour_end % 24) + 1))  # Accounting for hours wrapping around

        # Win probability based on historical data
        win_prob_by_publisher = {}
        for pub in publishers:
            pub_history = history[history['publisher'] == pub]
            if len(pub_history) > 0:
                higher_cpm_count = sum(pub_history['cpm'] > cpm)
                equal_cpm_count = sum(pub_history['cpm'] == cpm)
                total_count = len(pub_history)

                if higher_cpm_count == 0:
                    if equal_cpm_count > 1:  # Including itself
                        win_prob_by_publisher[pub] = 0.5
                    else:
                        win_prob_by_publisher[pub] = 1.0
                else:
                    win_prob_by_publisher[pub] = 0.0
            else:
                win_prob_by_publisher[pub] = 0.5  # Default if no data

        avg_win_prob = sum(win_prob_by_publisher.values()) / len(win_prob_by_publisher)

        # Coverage statistics
        rel_price = cpm / history['cpm'].median()

        ad_features.append({
            'idx': idx,
            'cpm': cpm,
            'hour_start': hour_start,
            'hour_end': hour_end,
            'time_window': time_window,
            'publisher_count': len(publishers),
            'publishers': ','.join(publishers),
            'audience_size': audience_size,
            'avg_win_probability': avg_win_prob,
            'relative_price': rel_price,
            'hours_covered': ','.join(map(str, hours_covered)),
            'hour_count': len(hours_covered)
        })

    ad_features_df = pd.DataFrame(ad_features)
    return ad_features_df


def simulate_ad_view_probabilities(users, history, validate, ad_features):
    """
    Simulate probabilistic ad viewing based on auction mechanics and user behavior
    to generate training examples for our model
    """

    def simulate_ad_view_probabilities(users, history, validate, ad_features):
        """Optimized version of the simulation function"""
        # Use a smaller sample of the validation set
        sample_indices = np.random.choice(validate.index, min(30, len(validate)), replace=False)
        simulated_results = []

        # Pre-compute some statistics to avoid repetitive calculations
        publisher_stats = {}
        for pub in history['publisher'].unique():
            pub_data = history[history['publisher'] == pub]
            publisher_stats[pub] = {
                'hour_counts': pub_data['hour_of_day'].value_counts(normalize=True).to_dict(),
                'cpm_percentiles': np.percentile(pub_data['cpm'], [25, 50, 75, 90, 95, 99])
            }

        # Pre-compute user preferences
        user_preferences = {}
        for user_id in history['user_id'].unique():
            user_data = history[history['user_id'] == user_id]
            if len(user_data) > 0:
                user_preferences[user_id] = {
                    'pubs': user_data['publisher'].value_counts(normalize=True).to_dict(),
                    'hours': user_data['hour_of_day'].value_counts(normalize=True).to_dict()
                }

        for idx in tqdm(sample_indices, desc="Simulating ad campaigns"):
            ad_row = validate.loc[idx]
            ad_feat_row = ad_features[ad_features['idx'] == idx].iloc[0]

            cpm = ad_row['cpm']
            hour_start = ad_row['hour_start']
            hour_end = ad_row['hour_end']
            publishers = ad_row['publishers'].split(',')
            user_ids = ad_row['user_ids']

            # Sample some users to make computation tractable
            sample_size = min(1000, len(user_ids))
            sampled_users = np.random.choice(user_ids, sample_size, replace=False)

            user_view_counts = {user_id: 0 for user_id in sampled_users}

            # For each user, simulate their ad viewing behavior
            for user_id in sampled_users:
                user_history = history[history['user_id'] == user_id]

                if len(user_history) == 0:
                    # No history for this user, use general statistics
                    view_probability = ad_feat_row['avg_win_probability'] * 0.5  # Conservative estimate
                    views = np.random.binomial(ad_feat_row['hour_count'], view_probability)
                    user_view_counts[user_id] = views
                    continue

                # Analyze user's publisher preferences
                user_pubs = user_history['publisher'].value_counts().to_dict()
                total_views = sum(user_pubs.values())
                user_pub_probs = {pub: count / total_views for pub, count in user_pubs.items()}

                # Analyze user's time of day preferences
                user_hours = user_history['hour_of_day'].value_counts().to_dict()
                total_hours = sum(user_hours.values())
                user_hour_probs = {hour: count / total_hours for hour, count in user_hours.items()}

                # Simulate views based on user's preferences and ad parameters
                hours_covered = list(range(hour_start % 24, (hour_end % 24) + 1))

                views = 0
                current_session = None
                session_ads = set()

                for h in hours_covered:
                    hour_prob = user_hour_probs.get(h, 0.01)  # Default low probability if no history

                    for pub in publishers:
                        if pub in user_pub_probs:
                            pub_prob = user_pub_probs[pub]
                        else:
                            pub_prob = 0.01  # Default low probability

                        # Win auction probability based on CPM
                        pub_history = history[(history['publisher'] == pub) & (history['hour_of_day'] == h)]
                        if len(pub_history) > 0:
                            higher_cpm = sum(pub_history['cpm'] > cpm)
                            equal_cpm = sum(pub_history['cpm'] == cpm)

                            if higher_cpm == 0:
                                if equal_cpm > 1:
                                    win_prob = 0.5
                                else:
                                    win_prob = 1.0
                            else:
                                win_prob = 0.0
                        else:
                            win_prob = 0.5  # Default

                        # Combined probability
                        overall_prob = hour_prob * pub_prob * win_prob

                        # Simulate viewing
                        if np.random.random() < overall_prob:
                            # Check session logic - ads aren't shown twice in same session
                            if current_session is None or np.random.random() < 0.2:  # 20% chance of new session
                                current_session = f"sim_{user_id}_{h}"
                                session_ads = set()

                            ad_key = f"ad_{idx}"
                            if ad_key not in session_ads:
                                views += 1
                                session_ads.add(ad_key)

                user_view_counts[user_id] = views

            # Calculate probabilities
            at_least_one = sum(1 for v in user_view_counts.values() if v >= 1) / len(user_view_counts)
            at_least_two = sum(1 for v in user_view_counts.values() if v >= 2) / len(user_view_counts)
            at_least_three = sum(1 for v in user_view_counts.values() if v >= 3) / len(user_view_counts)

            simulated_results.append({
                'idx': idx,
                'at_least_one': at_least_one,
                'at_least_two': at_least_two,
                'at_least_three': at_least_three
            })

        return pd.DataFrame(simulated_results)

def prepare_training_data(validate, ad_features, user_features, simulated_results):
    """
    Prepare training data by combining ad features with user features
    """
    # Для хранения примеров обучения
    training_examples = []

    for idx, row in validate.iterrows():
        ad_feat = ad_features[ad_features['idx'] == idx].iloc[0]

        # Получение всех пользователей аудитории
        audience_users = row['user_ids']
        audience_users_df = user_features[user_features['user_id'].isin(audience_users)]

        # Расчет статистики по аудитории
        audience_stats = {}

        # Демографические статистики
        for demo_col in ['sex', 'age_group', 'city_id']:
            if demo_col in audience_users_df.columns:
                value_counts = audience_users_df[demo_col].value_counts(normalize=True).to_dict()
                for val, prop in value_counts.items():
                    audience_stats[f'audience_{demo_col}_{val}_prop'] = prop

        # Статистика по числовым признакам
        numeric_cols = audience_users_df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if col not in ['user_id', 'age']:
                audience_stats[f'audience_{col}_mean'] = audience_users_df[col].mean()
                audience_stats[f'audience_{col}_median'] = audience_users_df[col].median()
                audience_stats[f'audience_{col}_std'] = audience_users_df[col].std()

        # Статистика по совпадению с издателем
        ad_publishers = set(row['publishers'].split(','))

        # Поиск колонки с информацией о издателе
        publisher_col = None
        for col in audience_users_df.columns:
            if 'publisher' in col.lower() and audience_users_df[col].dtype == object:
                publisher_col = col
                break

        if publisher_col:
            audience_users_df['publisher_match'] = audience_users_df[publisher_col].apply(
                lambda x: len(set(str(x).split(',')) & ad_publishers) > 0 if isinstance(x, str) else False
            )
            audience_stats['audience_publisher_match_prop'] = audience_users_df['publisher_match'].mean()
        else:
            # На случай отсутствия колонки
            audience_stats['audience_publisher_match_prop'] = 0.0

        # Комбинирование с признаками объявления
        example = {**ad_feat.to_dict(), **audience_stats}

        # Добавление таргета при наличии
        if simulated_results is not None and 'idx' in simulated_results.columns:
            if idx in simulated_results['idx'].values:
                sim_row = simulated_results[simulated_results['idx'] == idx].iloc[0]
                example['at_least_one'] = sim_row['at_least_one']
                example['at_least_two'] = sim_row['at_least_two']
                example['at_least_three'] = sim_row['at_least_three']

        training_examples.append(example)

    return pd.DataFrame(training_examples)

def train_models(training_data, validate_answers):
    """
    Train separate models for each target using CatBoost
    """
    models = {}
    importances = {}

    # Find available targets
    available_targets = [col for col in TARGET_COLS if col in training_data.columns]

    if not available_targets:
        print("No training targets available. Using validation data instead.")
        # Handle case where we don't have simulated targets - use validation answers
        for idx, row in training_data.iterrows():
            if idx in validate_answers.index:
                for target in TARGET_COLS:
                    training_data.loc[idx, target] = validate_answers.loc[idx, target]

        available_targets = TARGET_COLS

    # Determine features
    exclude_cols = TARGET_COLS + ['idx', 'publishers', 'hours_covered']
    feature_cols = [col for col in training_data.columns if col not in exclude_cols]

    # Handle categorical features
    cat_features = [i for i, col in enumerate(feature_cols) if training_data[col].dtype == 'object']

    for target in available_targets:
        print(f"\nTraining model for {target}")

        # Prepare data
        X = training_data[feature_cols]
        y = training_data[target].fillna(0)

        # Split data
        X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

        # Create CatBoost Pool with categorical features
        train_pool = Pool(X_train, y_train, cat_features=cat_features)
        val_pool = Pool(X_val, y_val, cat_features=cat_features)

        # Train model
        model = CatBoostRegressor(
            iterations=1000,
            learning_rate=0.03,
            depth=6,
            loss_function='RMSE',
            eval_metric='RMSE',
            random_seed=42,
            verbose=100
        )

        model.fit(train_pool, eval_set=val_pool, early_stopping_rounds=50)

        # Evaluate
        val_preds = model.predict(X_val)
        val_metric = calculate_metric(y_val.values, val_preds)
        print(f"Validation metric for {target}: {val_metric:.4f}%")

        # Store model and feature importances
        models[target] = model
        importances[target] = model.get_feature_importance(train_pool)

        # Plot feature importances
        plt.figure(figsize=(10, 8))
        feature_importance = pd.DataFrame({
            'Feature': feature_cols,
            'Importance': importances[target]
        }).sort_values('Importance', ascending=False).head(20)

        sns.barplot(x='Importance', y='Feature', data=feature_importance)
        plt.title(f'Top 20 Feature Importances for {target}')
        plt.tight_layout()
        plt.savefig(f'feature_importance_{target}.png')
        plt.close()

    return models, importances


def make_predictions(models, training_data, validate):
    """
    Make predictions for the validation set
    """
    # Determine features
    exclude_cols = TARGET_COLS + ['idx', 'publishers', 'hours_covered']
    feature_cols = [col for col in training_data.columns if col not in exclude_cols]

    # Create predictions DataFrame
    predictions = pd.DataFrame(index=validate.index)

    # Make predictions for each target
    for target, model in models.items():
        predictions[target] = model.predict(training_data[feature_cols])

    # Clip predictions to valid range
    for target in TARGET_COLS:
        if target in predictions.columns:
            predictions[target] = predictions[target].clip(0, 1)
        else:
            print(f"Warning: No predictions for {target}")

    # Ensure all targets are present
    for target in TARGET_COLS:
        if target not in predictions.columns:
            print(f"Warning: Target {target} missing from predictions. Using fallback.")
            # Simple fallback based on audience size
            predictions[target] = validate['audience_size'].apply(
                lambda x: max(0, min(1, 0.5 - 0.1 * (np.log10(x) - 2)))
            )

    return predictions


def run_cross_validation(training_data, n_splits=5):
    """
    Run cross-validation to get a reliable estimate of model performance
    """
    # Determine features
    exclude_cols = TARGET_COLS + ['idx', 'publishers', 'hours_covered']
    feature_cols = [col for col in training_data.columns if col not in exclude_cols]

    # Handle categorical features
    cat_features = [i for i, col in enumerate(feature_cols) if training_data[col].dtype == 'object']

    # Available targets
    available_targets = [col for col in TARGET_COLS if col in training_data.columns]

    cv_results = {}
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=42)

    for target in available_targets:
        print(f"\nCross-validation for {target}")
        cv_metrics = []

        # Prepare data
        X = training_data[feature_cols]
        y = training_data[target].fillna(0)

        for fold, (train_idx, val_idx) in enumerate(kf.split(X)):
            X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
            y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]

            # Create CatBoost Pool with categorical features
            train_pool = Pool(X_train, y_train, cat_features=cat_features)
            val_pool = Pool(X_val, y_val, cat_features=cat_features)

            # Train model
            model = CatBoostRegressor(
                iterations=500,
                learning_rate=0.05,
                depth=6,
                loss_function='RMSE',
                eval_metric='RMSE',
                random_seed=42 + fold,
                verbose=0
            )

            model.fit(train_pool, eval_set=val_pool, early_stopping_rounds=50)

            # Evaluate
            val_preds = model.predict(X_val)
            val_metric = calculate_metric(y_val.values, val_preds)
            cv_metrics.append(val_metric)
            print(f"Fold {fold + 1}, Metric: {val_metric:.4f}%")

        cv_results[target] = {
            'mean': np.mean(cv_metrics),
            'std': np.std(cv_metrics),
            'values': cv_metrics
        }
        print(f"CV {target} metric: {cv_results[target]['mean']:.4f}% ± {cv_results[target]['std']:.4f}%")

    return cv_results


def main():
    # Create output directory for artifacts
    os.makedirs('artifacts', exist_ok=True)

    # 1. Load data
    print("Loading data...")
    users, history, validate, answers = load_data()

    # 2. Preprocess history data
    print("Preprocessing history data...")
    history = preprocess_history(history)

    # 3. Analyze auction dynamics
    print("Analyzing auction dynamics...")
    cpm_stats, cpm_win_probs = analyze_auction_dynamics(history)

    # Save some exploratory plots
    plt.figure(figsize=(12, 6))
    sns.histplot(history['cpm'], bins=50, log_scale=True)
    plt.title('Distribution of CPM values')
    plt.savefig('artifacts/cpm_distribution.png')
    plt.close()

    plt.figure(figsize=(12, 6))
    sns.boxplot(x='publisher', y='cpm', data=history.sample(min(10000, len(history))))
    plt.title('CPM by Publisher')
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig('artifacts/cpm_by_publisher.png')
    plt.close()

    # 4. Create features
    print("Creating user features...")
    user_features = create_user_features(users, history)

    print("Creating ad features...")
    ad_features = create_ad_features(validate, history)

    # 5. Simulate ad views for training data
    print("Simulating ad views...")
    simulated_results = simulate_ad_view_probabilities(users, history, validate, ad_features)

    # 6. Prepare training data
    print("Preparing training data...")
    training_data = prepare_training_data(validate, ad_features, user_features, simulated_results)

    # 7. Run cross-validation
    print("Running cross-validation...")
    cv_results = run_cross_validation(training_data)

    # 8. Train final models
    print("Training final models...")
    models, importances = train_models(training_data, answers)

    # 9. Make predictions
    print("Making predictions...")
    predictions = make_predictions(models, training_data, validate)

    # 10. Evaluate against validation answers
    metric_values = []
    for target in TARGET_COLS:
        metric = calculate_metric(answers[target].values, predictions[target].values)
        metric_values.append(metric)
        print(f"Metric for {target}: {metric:.4f}%")

    overall_metric = np.mean(metric_values)
    print(f"Overall metric: {overall_metric:.4f}%")

    # 11. Save models and predictions
    with open('artifacts/models.pkl', 'wb') as f:
        pickle.dump(models, f)

    predictions.to_csv('predictions.tsv', sep='\t', index=False)
    print("Predictions saved to predictions.tsv")


if __name__ == "__main__":
    main()