

from src.recommendation_engine import calculate_distance_savings
from src.factory_rules import get_expected_factory


def test_distance_savings():
    result = calculate_distance_savings(1000, 700)

    assert result["distance_saved_km"] == 300
    assert result["distance_saved_percent"] == 30
    assert result["is_closer"] is True


def test_no_distance_savings():
    result = calculate_distance_savings(500, 700)

    assert result["distance_saved_km"] == -200
    assert result["is_closer"] is False


def test_factory_mapping():
    assert (
        get_expected_factory("Wonka Bar - Milk Chocolate")
        == "Wicked Choccy's"
    )

    assert (
        get_expected_factory("Nerds")
        == "Sugar Shack"
    )


def test_unknown_product():
    assert get_expected_factory("Unknown Product") is None


if __name__ == "__main__":
    test_distance_savings()
    test_no_distance_savings()
    test_factory_mapping()
    test_unknown_product()

    print("All recommendation engine tests passed!")
