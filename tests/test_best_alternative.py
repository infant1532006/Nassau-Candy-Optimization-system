
import pandas as pd
from src.data_loader import load_audit_data
from src.recommendation_engine import generate_geographic_opportunities
from src.recommendation_engine import (select_best_geographic_alternative,)

def test_selects_largest_distance_reduction():
    opportunities = pd.DataFrame(
        [
            {
                "Row ID": 1,
                "Alternative Factory": "Factory A",
                "distance_saved_km": 100.0,
                "distance_saved_percent": 10.0,
                "Mapping Compatible": False,
            },
            {
                "Row ID": 1,
                "Alternative Factory": "Factory B",
                "distance_saved_km": 350.0,
                "distance_saved_percent": 35.0,
                "Mapping Compatible": False,
            },
            {
                "Row ID": 1,
                "Alternative Factory": "Factory C",
                "distance_saved_km": 200.0,
                "distance_saved_percent": 20.0,
                "Mapping Compatible": False,
            },
        ]
    )

    result = select_best_geographic_alternative(opportunities)

    assert len(result) == 1
    assert result.iloc[0]["Alternative Factory"] == "Factory B"
    assert result.iloc[0]["distance_saved_km"] == 350.0


def test_handles_empty_input():
    opportunities = pd.DataFrame()
    result = select_best_geographic_alternative(opportunities)
    assert result.empty


def test_real_dataset_best_alternatives():
    audit_data = load_audit_data()
    opportunities = generate_geographic_opportunities(audit_data)
    best_alternatives = select_best_geographic_alternative(opportunities)

    assert not best_alternatives.empty
    assert best_alternatives["Row ID"].is_unique
    assert best_alternatives["distance_saved_km"].gt(0).all()
    assert best_alternatives["Mapping Compatible"].notna().all()

    print(f"Audit records: {len(audit_data):,}")
    print(f"All geographic opportunities: {len(opportunities):,}")
    print(f"Best alternatives selected: {len(best_alternatives):,}")
    print("Mapping-compatible alternatives:",
        int(best_alternatives["Mapping Compatible"].sum()),)
    print("Real-dataset test passed!")

if __name__ == "__main__":
    test_selects_largest_distance_reduction()
    test_handles_empty_input()
    print("All best-alternative tests passed!")
