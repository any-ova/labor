import sys
import pandas as pd


def load_tasks(tasks_filename):
    return pd.read_csv(tasks_filename, sep="\t")


def main():
    tasks_filename = sys.argv[1]
    tasks = load_tasks(tasks_filename)
    tasks = tasks.assign(
        at_least_one=0,
        at_least_two=0,
        at_least_three=0,
    )
    print(tasks[['at_least_one', 'at_least_two', 'at_least_three']].to_csv(sep="\t", index=False))


if __name__ == "__main__":
    main()
