import sys
import pandas as pd
import numpy as np


def load_answers(filename):
    """Улучшенная загрузка TSV-файлов"""
    try:
        # Сначала пробуем стандартное чтение
        df = pd.read_csv(filename, sep='\t', encoding='utf-8-sig')

        # Проверяем структуру
        if not {'at_least_one', 'at_least_two', 'at_least_three'}.issubset(df.columns):
            raise ValueError(f"Файл {filename} имеет неверную структуру")

        return df
    except Exception as e:
        # Если ошибка - пробуем почистить файл
        try:
            with open(filename, 'r', encoding='utf-8-sig') as f:
                lines = [line.strip().split('\t') for line in f if line.strip()]

            # Проверяем одинаковое количество столбцов
            col_count = len(lines[0])
            if any(len(line) != col_count for line in lines[1:]):
                raise ValueError("Несовпадение количества столбцов в файле")

            return pd.DataFrame(lines[1:], columns=lines[0])
        except Exception as e2:
            raise ValueError(f"Не удалось прочитать файл {filename}: {str(e2)}")
def get_smoothed_log_mape_column_value(responses_column, answers_column, epsilon):
    return np.abs(np.log(
        (responses_column + epsilon) / (answers_column + epsilon)
    )).mean()


def get_smoothed_mean_log_accuracy_ratio(answers, responses, epsilon=0.005):
    log_accuracy_ratio_mean = np.array([
        get_smoothed_log_mape_column_value(responses['at_least_one'], answers['at_least_one'], epsilon),
        get_smoothed_log_mape_column_value(responses['at_least_two'], answers['at_least_two'], epsilon),
        get_smoothed_log_mape_column_value(responses['at_least_three'], answers['at_least_three'], epsilon),
    ]).mean()

    percentage_error = 100 * (np.exp(log_accuracy_ratio_mean) - 1)
    return round(percentage_error, 2)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Использование: python metrics.py <answers_file> <responses_file>")
        sys.exit(1)

    answers_file = sys.argv[1]
    responses_file = sys.argv[2]

    try:
        answers = load_answers(answers_file)
        responses = load_answers(responses_file)
        print(get_smoothed_mean_log_accuracy_ratio(answers, responses))
    except Exception as e:
        print(f"Ошибка: {str(e)}")
        sys.exit(1)