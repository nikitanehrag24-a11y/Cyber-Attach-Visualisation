"""
Runs all 5 dataset cleaning pipelines in sequence and prints a summary.
Each dataset's own clean_<name>.py can still be run individually for
debugging -- this just chains them together once each is verified working.

Usage:
    python -m src.preprocessing.run_all
"""

import traceback

from src.preprocessing import (
    clean_global_threats,
    clean_cfr_incidents,
    clean_vulnerabilities,
    clean_attack_signatures,
    clean_malmem,
)

PIPELINES = [
    ("global_threats", clean_global_threats),
    ("cfr_incidents", clean_cfr_incidents),
    ("vulnerabilities", clean_vulnerabilities),
    ("attack_signatures", clean_attack_signatures),
    ("malmem_2022", clean_malmem),
]


def main():
    results = {}
    for name, module in PIPELINES:
        print(f"\n{'=' * 60}\nRunning: {name}\n{'=' * 60}")
        try:
            module.main()
            results[name] = "OK"
        except Exception as e:
            print(f"FAILED: {name} -- {e}")
            traceback.print_exc()
            results[name] = f"FAILED: {e}"

    print(f"\n{'=' * 60}\nSUMMARY\n{'=' * 60}")
    for name, status in results.items():
        print(f"  {name}: {status}")

    n_failed = sum(1 for s in results.values() if s.startswith("FAILED"))
    if n_failed:
        print(f"\n{n_failed} pipeline(s) failed -- see errors above.")
    else:
        print("\nAll 5 pipelines completed successfully.")


if __name__ == "__main__":
    main()
