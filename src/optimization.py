
import pandas as pd

def summarize_opportunities(
    opportunities: pd.DataFrame,
) -> pd.DataFrame:
    """Summarize geographic opportunities by product and factory."""

    if opportunities.empty:
        return pd.DataFrame()

    summary = (
        opportunities
        .groupby(
            [
                "Product Name",
                "Current Factory",
                "Alternative Factory",
                "Mapping Compatible",
            ],
            dropna=False,)
        .agg(
            Records=("Row ID", "count"),
            Avg_Distance_Saved_km=("distance_saved_km", "mean"),
            Avg_Distance_Saved_pct=("distance_saved_percent", "mean"),)
        .reset_index()
        .sort_values(
            "Avg_Distance_Saved_km",
            ascending=False,)
        .reset_index(drop=True))

    return summary
