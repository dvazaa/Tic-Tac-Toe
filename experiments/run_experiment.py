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


main()