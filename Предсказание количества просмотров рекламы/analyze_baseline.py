import pandas as pd
import matplotlib.pyplot as plt


def load_file(filename):
    """Универсальная функция загрузки с определением кодировки"""
    encodings = ['utf-8', 'utf-16', 'cp1251', 'latin1']
    for encoding in encodings:
        try:
            return pd.read_csv(filename, sep='\t', encoding=encoding)
        except (UnicodeDecodeError, pd.errors.ParserError):
            continue
    raise ValueError(f"Не удалось загрузить файл {filename} с поддерживаемыми кодировками")


def load_data():
    """Загрузка всех необходимых файлов"""
    answers = load_file('validate_answers.tsv')
    baseline = load_file('baseline_predictions.tsv')
    return answers, baseline


def analyze_results(answers, baseline):
    """Анализ и визуализация результатов"""
    # Основная статистика
    print("\n=== Статистика реальных значений ===")
    print(answers.describe())

    print("\n=== Статистика baseline ===")
    print(baseline.describe())

    # Визуализация
    plt.figure(figsize=(12, 6))

    # Гистограмма распределения реальных значений
    plt.subplot(1, 2, 1)
    answers['at_least_one'].hist(bins=50)
    plt.title('Распределение реальных значений\n(at_least_one)')
    plt.xlabel('Значение')
    plt.ylabel('Частота')

    # Сравнение реальных и предсказанных значений
    plt.subplot(1, 2, 2)
    plt.scatter(answers['at_least_one'], baseline['at_least_one'], alpha=0.1)
    plt.plot([0, 1], [0, 1], 'r--')
    plt.title('Сравнение реальных и baseline значений')
    plt.xlabel('Реальные значения')
    plt.ylabel('Baseline предсказания')
    plt.tight_layout()
    plt.savefig('baseline_analysis.png')
    plt.show()


if __name__ == "__main__":
    print("Загрузка данных...")
    try:
        answers, baseline = load_data()

        print("\nПервые 5 строк реальных значений:")
        print(answers.head())

        print("\nПервые 5 строк baseline:")
        print(baseline.head())

        analyze_results(answers, baseline)
        print("\nГрафики сохранены в baseline_analysis.png")

    except Exception as e:
        print(f"\nОшибка: {str(e)}")
        print("\nРекомендации:")
        print("1. Проверьте, что файлы существуют в текущей директории")
        print("2. Откройте файлы в Notepad++ и определите их кодировку")
        print("3. При необходимости пересохраните файлы в UTF-8")
        print("4. Убедитесь, что файлы используют табуляцию как разделитель")