import os
import sys

ROOT_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from experiments.scenario_1 import run_scenario_1
from experiments.scenario_2 import run_scenario_2
from experiments.scenario_3 import run_scenario_3


def main():
    print("=== MENJALANKAN SELURUH EKSPERIMEN ===")

    print("\n--- SKENARIO 1 ---")
    run_scenario_1()

    print("\n--- SKENARIO 2 ---")
    run_scenario_2()

    print("\n--- SKENARIO 3 ---")
    run_scenario_3()

    print("\n=== SELURUH EKSPERIMEN SELESAI ===")


if __name__ == "__main__":
    main()