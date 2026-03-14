"""
UC-0C — Number That Looks Right
Reads ward_budget.csv, calculates totals, detects suspicious numbers,
and flags inconsistencies.
"""

import argparse
import csv
import json
import re
from pathlib import Path


def parse_amount(value) -> float | None:
    """Convert cell to float; return None for empty/invalid."""
    if value is None or value == "":
        return None
    s = str(value).strip()
    if not s or s.lower().startswith("data") or s.lower().startswith("audit") or s.lower().startswith("contractor"):
        return None
    s = re.sub(r"[^\d.-]", "", s)
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def load_budget_csv(file_path: Path) -> list:
    """Read ward_budget.csv and return list of parsed rows."""
    if not file_path.exists():
        raise FileNotFoundError(f"Budget file not found: {file_path}")

    rows = []
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            budgeted = parse_amount(r.get("budgeted_amount"))
            actual = parse_amount(r.get("actual_spend"))
            rows.append({
                "period": r.get("period", ""),
                "ward": r.get("ward", ""),
                "category": r.get("category", ""),
                "budgeted_amount": budgeted,
                "actual_spend": actual,
                "notes": r.get("notes", ""),
            })
    return rows


def calculate_totals(rows: list) -> dict:
    """Compute per-ward, per-category, and grand totals."""
    ward_budget = {}
    ward_actual = {}
    cat_budget = {}
    cat_actual = {}
    total_budget = 0.0
    total_actual = 0.0

    for r in rows:
        b = r.get("budgeted_amount")
        a = r.get("actual_spend")
        ward = r.get("ward", "")
        cat = r.get("category", "")

        if b is not None:
            ward_budget[ward] = ward_budget.get(ward, 0) + b
            cat_budget[cat] = cat_budget.get(cat, 0) + b
            total_budget += b
        if a is not None:
            ward_actual[ward] = ward_actual.get(ward, 0) + a
            cat_actual[cat] = cat_actual.get(cat, 0) + a
            total_actual += a

    return {
        "ward_budget": ward_budget,
        "ward_actual": ward_actual,
        "category_budget": cat_budget,
        "category_actual": cat_actual,
        "total_budgeted": total_budget,
        "total_actual": total_actual,
    }


def detect_suspicious(rows: list, threshold: float = 1.2) -> list:
    """Flag rows where actual > budget * threshold."""
    flagged = []
    for r in rows:
        b = r.get("budgeted_amount")
        a = r.get("actual_spend")
        if b is None or a is None or b <= 0:
            continue
        if a > b * threshold:
            pct = ((a - b) / b) * 100
            flagged.append({
                **r,
                "reason": f"Overspend: {pct:.1f}% over budget",
            })
    return flagged


def flag_inconsistencies(rows: list) -> list:
    """Identify missing data and anomalies."""
    issues = []
    for r in rows:
        a = r.get("actual_spend")
        b = r.get("budgeted_amount")
        if b is not None and a is None:
            issues.append({
                "period": r["period"],
                "ward": r["ward"],
                "category": r["category"],
                "reason": "Missing actual_spend",
                "notes": r.get("notes", ""),
            })
        if b is not None and b < 0:
            issues.append({
                "period": r["period"],
                "ward": r["ward"],
                "category": r["category"],
                "reason": "Negative budgeted_amount",
                "notes": r.get("notes", ""),
            })
        if a is not None and a < 0:
            issues.append({
                "period": r["period"],
                "ward": r["ward"],
                "category": r["category"],
                "reason": "Negative actual_spend",
                "notes": r.get("notes", ""),
            })
    return issues


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Validation")
    parser.add_argument("--input", default="data/budget/ward_budget.csv", help="Path to ward_budget.csv")
    parser.add_argument("--output", help="Path to write results JSON (optional)")
    parser.add_argument("--threshold", type=float, default=1.2, help="Overspend threshold (default 1.2 = 20%%)")
    args = parser.parse_args()

    base = Path(__file__).resolve().parent.parent
    input_path = Path(args.input)
    if not input_path.is_absolute():
        # Resolve relative to cwd (user typically runs from uc-0c with ../data/...)
        input_path = (Path.cwd() / args.input).resolve()
    if not input_path.exists() and (base / "data/budget/ward_budget.csv").exists():
        input_path = base / "data/budget/ward_budget.csv"
    output_path = Path(args.output) if args.output else None
    if output_path and not output_path.is_absolute():
        output_path = base / output_path

    rows = load_budget_csv(input_path)
    totals = calculate_totals(rows)
    suspicious = detect_suspicious(rows, args.threshold)
    inconsistencies = flag_inconsistencies(rows)

    # Print report
    print("\n--- Ward Budget Validation Report ---\n")
    print("  TOTALS (lakhs)")
    print(f"    Total budgeted: {totals['total_budgeted']:.1f}")
    print(f"    Total actual:   {totals['total_actual']:.1f}")
    print(f"    Variance:       {totals['total_actual'] - totals['total_budgeted']:.1f}")
    print()
    print("  PER-WARD TOTALS (sample)")
    for ward in sorted(totals["ward_budget"].keys())[:5]:
        b = totals["ward_budget"].get(ward, 0)
        a = totals["ward_actual"].get(ward, 0)
        print(f"    {ward}: budget {b:.1f}, actual {a:.1f}")
    print()
    print("  SUSPICIOUS (overspend > 20%)")
    for s in suspicious[:10]:
        print(f"    {s['period']} {s['ward']} {s['category']}: {s['reason']}")
    if len(suspicious) > 10:
        print(f"    ... and {len(suspicious) - 10} more")
    print()
    print("  INCONSISTENCIES (missing data)")
    for i in inconsistencies[:10]:
        print(f"    {i['period']} {i['ward']} {i['category']}: {i['reason']}")
    if len(inconsistencies) > 10:
        print(f"    ... and {len(inconsistencies) - 10} more")
    print()

    result = {
        "totals": {
            "total_budgeted": totals["total_budgeted"],
            "total_actual": totals["total_actual"],
            "variance": totals["total_actual"] - totals["total_budgeted"],
        },
        "suspicious_count": len(suspicious),
        "suspicious_rows": suspicious[:50],
        "inconsistency_count": len(inconsistencies),
        "inconsistencies": inconsistencies[:50],
    }

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        print(f"  Results written to: {output_path}\n")

    print("Done.")


if __name__ == "__main__":
    main()
