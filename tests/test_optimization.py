
from src.data_loader import load_audit_data
from src.recommendation_engine import generate_geographic_opportunities
from src.optimization import summarize_opportunities


def test_opportunity_summary():
    audit_data = load_audit_data()
    opportunities = generate_geographic_opportunities(audit_data)

    summary = summarize_opportunities(opportunities)

    assert not summary.empty
    assert "Records" in summary.columns
    assert "Avg_Distance_Saved_km" in summary.columns
    assert "Mapping Compatible" in summary.columns

    assert (summary["Avg_Distance_Saved_km"] > 0).all()

    print("Individual opportunities:", len(opportunities))
    print("Summarized combinations:", len(summary))
    print("\nTop 10 geographic opportunities:")
    print(summary.head(10).round(2).to_string(index=False))
    print("\nOptimization summary test passed!")


if __name__ == "__main__":
    test_opportunity_summary()
