
from src.data_loader import load_audit_data
from src.recommendation_engine import (
    generate_geographic_opportunities,
    classify_opportunities,
)


def test_classify_opportunities():
    audit_data = load_audit_data()
    opportunities = generate_geographic_opportunities(audit_data)

    classified = classify_opportunities(opportunities)

    compatible = classified["mapping_compatible"]
    requires_review = classified["requires_review"]

    assert len(compatible) + len(requires_review) == len(opportunities)
    assert compatible["Mapping Compatible"].all()
    assert (~requires_review["Mapping Compatible"]).all()

    print("Total opportunities:", len(opportunities))
    print("Mapping-compatible:", len(compatible))
    print("Requires review:", len(requires_review))
    print("Classification test passed!")


if __name__ == "__main__":
    test_classify_opportunities()
