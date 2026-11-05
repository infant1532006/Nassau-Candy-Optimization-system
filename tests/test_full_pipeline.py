
from src.data_loader import load_audit_data
from src.recommendation_engine import (
    generate_geographic_opportunities,
    classify_opportunities,
)
from src.optimization import summarize_opportunities


def test_full_pipeline():
    audit_data = load_audit_data()

    opportunities = generate_geographic_opportunities(audit_data)
    summary = summarize_opportunities(opportunities)
    classified = classify_opportunities(opportunities)

    assert len(opportunities) > 0
    assert not summary.empty
    assert (
        len(classified["mapping_compatible"])
        + len(classified["requires_review"])
        == len(opportunities)
    )

    print("Full pipeline test passed!")
    print("Audit records:", len(audit_data))
    print("Geographic opportunities:", len(opportunities))
    print("Summary combinations:", len(summary))
    print(
        "Requires review:",
        len(classified["requires_review"]),
    )


if __name__ == "__main__":
    test_full_pipeline()
