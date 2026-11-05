
from src.data_loader import load_modeling_data, load_audit_data

def test_modeling_data():
    df = load_modeling_data()

    assert len(df) == 10194
    assert "Lead Time" in df.columns
    assert "Product Name" in df.columns

    print("Modeling dataset:", df.shape)


def test_audit_data():
    df = load_audit_data()

    assert len(df) == 10194
    assert "Current Factory Distance (km)" in df.columns
    assert "Lead Time" in df.columns

    print("Audit dataset:", df.shape)


if __name__ == "__main__":
    test_modeling_data()
    test_audit_data()
    print("All data loader tests passed!")
