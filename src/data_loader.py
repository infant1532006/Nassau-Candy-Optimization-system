
from pathlib import Path
import pandas as pd

def get_project_root() -> Path:
    """Find the project root directory."""
    return Path(__file__).resolve().parent.parent

def load_modeling_data() -> pd.DataFrame:
    """Load the processed dataset used for lead-time modeling."""
    project_root = get_project_root()

    data_path = (
        project_root
        / "data"
        / "processed"
        / "nassau_candy_modeling_dataset.csv")

    if not data_path.exists():
        raise FileNotFoundError(
            f"Modeling dataset not found: {data_path}")

    return pd.read_csv(data_path)

def load_audit_data() -> pd.DataFrame:
    """Load the full processed dataset with geographic information."""
    project_root = get_project_root()

    data_path = (
        project_root
        / "data"
        / "processed"
        / "nassau_candy_processed_audit.csv")

    if not data_path.exists():
        raise FileNotFoundError(
            f"Audit dataset not found: {data_path}")

    return pd.read_csv(data_path)
