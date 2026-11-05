
from src.data_loader import load_audit_data
from src.recommendation_engine import generate_geographic_opportunities


def test_geographic_opportunities():
    df = load_audit_data()
    opportunities = generate_geographic_opportunities(df)

    assert not opportunities.empty
    assert (opportunities["distance_saved_km"] > 0).all()
    assert opportunities["Requires Feasibility Review"].all()

    print("Input records:", len(df))
    print("Geographic opportunities:", len(opportunities))
    print(
        "Mapping-compatible alternatives:",
        int(opportunities["Mapping Compatible"].sum()),
    )
    print("Geographic opportunity test passed!")


if __name__ == "__main__":
    test_geographic_opportunities()
