
import pandas as pd

from src.factory_rules import get_expected_factory


FACTORY_DISTANCE_COLUMNS = {
    "Lot's O' Nuts": "Distance to Lot's O' Nuts (km)",
    "Wicked Choccy's": "Distance to Wicked Choccy's (km)",
    "Sugar Shack": "Distance to Sugar Shack (km)",
    "Secret Factory": "Distance to Secret Factory (km)",
    "The Other Factory": "Distance to The Other Factory (km)",}


def calculate_distance_savings(
    current_distance: float,
    alternative_distance: float,
) -> dict:
    """Calculate potential straight-line distance savings."""

    distance_saved = current_distance - alternative_distance

    percentage_saved = (
        distance_saved / current_distance * 100
        if current_distance > 0
        else 0.0)

    return {
        "current_distance_km": round(current_distance, 2),
        "alternative_distance_km": round(alternative_distance, 2),
        "distance_saved_km": round(distance_saved, 2),
        "distance_saved_percent": round(percentage_saved, 2),
        "is_closer": distance_saved > 0,}


def generate_geographic_opportunities(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Find closer alternative factories for each record.

    These are geographic screening results, not approved
    manufacturing or shipping recommendations.
    """

    required_columns = [
        "Product Name",
        "Current Factory",
        "Current Factory Distance (km)",
        *FACTORY_DISTANCE_COLUMNS.values(),]

    missing_columns = [
        column for column in required_columns
        if column not in df.columns]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}")

    results = []

    for _, row in df.iterrows():
        current_factory = row["Current Factory"]
        current_distance = row["Current Factory Distance (km)"]

        if pd.isna(current_distance):
            continue

        expected_factory = get_expected_factory(row["Product Name"])

        for alternative_factory, distance_column in (
            FACTORY_DISTANCE_COLUMNS.items()):
            if alternative_factory == current_factory:
                continue

            alternative_distance = row[distance_column]

            if pd.isna(alternative_distance):
                continue

            savings = calculate_distance_savings(
                float(current_distance),
                float(alternative_distance),)

            if not savings["is_closer"]:
                continue

            results.append({
                "Row ID": row.get("Row ID"),
                "Product Name": row["Product Name"],
                "Current Factory": current_factory,
                "Alternative Factory": alternative_factory,
                "Expected Factory": expected_factory,
                **savings,
                "Mapping Compatible": (
                    alternative_factory == expected_factory),
                "Requires Feasibility Review": True,})

    return pd.DataFrame(results)


def classify_opportunities(
    opportunities: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    """Separate opportunities by factory-mapping compatibility."""
    required_column = "Mapping Compatible"

    if required_column not in opportunities.columns:
        raise ValueError(
            f"Missing required column: {required_column}")

    compatible = opportunities[
        opportunities[required_column] == True
    ].copy()

    requires_review = opportunities[
        opportunities[required_column] == False
    ].copy()

    return {
        "mapping_compatible": compatible,
        "requires_review": requires_review,
    }

def select_best_geographic_alternative(
    opportunities: pd.DataFrame,
) -> pd.DataFrame:
    """Select the closest geographic alternative for each record."""

    if opportunities.empty:
        return opportunities.copy()

    required_columns = [
        "Row ID",
        "Alternative Factory",
        "distance_saved_km",
        "distance_saved_percent",
        "Mapping Compatible",]

    missing_columns = [
        column
        for column in required_columns
        if column not in opportunities.columns]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}")

    best_alternatives = (
        opportunities
        .sort_values(
            ["Row ID", "distance_saved_km"],
            ascending=[True, False],)
        .drop_duplicates(subset=["Row ID"], keep="first")
        .reset_index(drop=True))

    return best_alternatives

