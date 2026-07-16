import pandas as pd

from scripts.string_cleaning_pipeline import (
    clean_text_column,
    normalize_casing,
    remove_special_characters,
    standardize_categories,
    strip_all_strings,
)


def test_string_cleaning_pipeline_functions():
    df = pd.DataFrame(
        {
            "customer_name": [" John ", "john", "JOHN"],
            "product_category": [" Electronics ", "electronics", "ELECTRONICS"],
            "customer_segment": ["B2B", "b 2 b", "business-to-business"],
            "city": ["São Paulo", "Montréal", "New York"],
        }
    )

    df = strip_all_strings(df.copy())
    assert df.loc[0, "customer_name"] == "John"
    assert df.loc[0, "product_category"] == "Electronics"

    df = normalize_casing(df, ["customer_name", "product_category", "customer_segment"])
    assert df.loc[0, "customer_name"] == "john"
    assert df.loc[0, "product_category"] == "electronics"

    df = remove_special_characters(df, ["city"])
    assert df.loc[0, "city"] == "so paulo"

    mapping = {
        "b2b": "B2B",
        "b 2 b": "B2B",
        "business-to-business": "B2B",
        "sme": "SMB",
        "small medium enterprise": "SMB",
        "enterprise": "Enterprise",
    }
    df = standardize_categories(df, {"customer_segment": mapping})
    assert set(df["customer_segment"].unique()) <= {"b2b", "smb", "enterprise"}

    cleaned = clean_text_column(pd.Series(["  Product A  ", "PRODUCT B", "Product_C", None, ""]), lowercase=True, strip=True, remove_special=True)
    assert cleaned.iloc[0] == "product a"
    assert cleaned.iloc[1] == "product b"
    assert cleaned.iloc[2] == "productc"
    assert pd.isna(cleaned.iloc[3])
    assert cleaned.iloc[4] == ""
