from __future__ import annotations

import argparse
import json
from pathlib import Path
from .gate import evaluate_release


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate X1 mandatory-100 release evidence")
    parser.add_argument("evidence", type=Path)
    parser.add_argument("--policy", type=Path, default=Path("config/mandatory-100.json"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    policy = json.loads(args.policy.read_text())
    evidence = json.loads(args.evidence.read_text())
    report = evaluate_release(policy, evidence)
    body = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(body)
    else:
        print(body, end="")
    return 0 if report["release_allowed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
