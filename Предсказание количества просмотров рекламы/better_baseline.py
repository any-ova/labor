# Новый файл better_baseline.py
import pandas as pd
import sys


def main():
    tasks = pd.read_csv(sys.argv[1], sep='\t')

    improved_values = {
        'at_least_one': 0.016,  # 75-й перцентиль вместо среднего
        'at_least_two': 0.0028,  # Оптимизировано под метрику
        'at_least_three': 0.0004  # С учетом epsilon=0.005
    }

    tasks = tasks.assign(**improved_values)
    print(tasks[['at_least_one', 'at_least_two', 'at_least_three']].to_csv(sep='\t', index=False))


if __name__ == "__main__":
    main()