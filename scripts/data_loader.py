from __future__ import annotations

from pathlib import Path
import re
import numpy as np
import pandas as pd


DEFAULT_DATA_PATH = Path("data/telco_customer_churn.csv")


def _to_snake(name: str) -> str:
    """Convert mixed-case or spaced column names to snake_case."""
    name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name.strip())
    name = name.replace(" ", "_").replace("-", "_")
    return name.lower()


def load_and_clean_data(path: str | Path | None = None) -> pd.DataFrame:
    """
    Load the Telco dataset and perform basic cleaning:
    - Normalize column names to snake_case.
    - Convert total_charges to numeric, fixing blank entries.
    - Drop duplicates.
    """
    data_path = Path(path) if path else DEFAULT_DATA_PATH
    df = pd.read_csv(data_path)

    df = df.copy()
    df.columns = [_to_snake(col) for col in df.columns]

    # total_charges comes as string with occasional blanks
    df["total_charges"] = pd.to_numeric(
        df["total_charges"].replace(" ", np.nan), errors="coerce"
    )
    df.loc[df["total_charges"].isna() & (df["tenure"] == 0), "total_charges"] = 0.0
    df["total_charges"] = df["total_charges"].fillna(df["total_charges"].median())

    df = df.drop_duplicates().reset_index(drop=True)
    return df


def feature_engineer_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply feature engineering used in HW1:
    - Map churn to numeric flag.
    - Binary encode yes/no columns.
    - Add service counts and bundled features.
    - Add ratios, bins, and log transforms.
    """
    model_df = df.copy()

    churn_clean = (
        model_df["churn"]
        .astype(str)
        .str.strip()
        .str.lower()
        .replace({"": np.nan, "nan": np.nan, "none": np.nan})
    )
    churn_map_numeric = {
        "yes": 1,
        "no": 0,
        "churned": 1,
        "not churned": 0,
        "stayed": 0,
        "true": 1,
        "false": 0,
        "1": 1,
        "0": 0,
    }
    model_df["churn_flag"] = churn_clean.map(churn_map_numeric)
    model_df = model_df[model_df["churn_flag"].notna()].reset_index(drop=True)
    model_df["churn_flag"] = model_df["churn_flag"].astype(int)
    model_df["churn"] = model_df["churn_flag"].map({1: "Yes", 0: "No"})

    # Normalize service-related categories
    no_internet_cols = [
        "online_security",
        "online_backup",
        "device_protection",
        "tech_support",
        "streaming_tv",
        "streaming_movies",
    ]
    replacement_rules = {col: {"No internet service": "No"} for col in no_internet_cols}
    replacement_rules["multiple_lines"] = {"No phone service": "No"}
    model_df = model_df.replace(replacement_rules)

    # Binary yes/no columns
    binary_cols = [
        col
        for col in model_df.columns
        if model_df[col].dropna().isin(["Yes", "No"]).all()
    ]
    model_df[binary_cols] = model_df[binary_cols].replace({"Yes": 1, "No": 0})

    # Service flags and counts
    service_cols = [
        "phone_service",
        "multiple_lines",
        "online_security",
        "online_backup",
        "device_protection",
        "tech_support",
        "streaming_tv",
        "streaming_movies",
    ]
    available_service_cols = [col for col in service_cols if col in model_df.columns]
    service_flags = model_df[available_service_cols].apply(
        lambda col: pd.to_numeric(col, errors="coerce")
    )
    model_df["services_count"] = service_flags.sum(axis=1)

    # Contract duration in months
    contract_months_map = {"Month-to-month": 1, "One year": 12, "Two year": 24}
    model_df["contract_months"] = model_df["contract"].map(contract_months_map)

    # Ratios and aggregates
    model_df["avg_revenue_per_month"] = model_df["total_charges"] / np.where(
        model_df["tenure"] == 0, 1, model_df["tenure"]
    )
    model_df["tenure_years"] = model_df["tenure"] / 12
    model_df["tenure_quarter"] = np.floor_divide(model_df["tenure"], 3)
    model_df["tenure_bucket"] = pd.cut(
        model_df["tenure"],
        bins=[-1, 12, 24, 48, 72],
        labels=["0-12", "13-24", "25-48", "49-72"],
    )
    model_df["monthly_charge_band"] = pd.qcut(
        model_df["monthly_charges"], q=4, labels=["Low", "Mid", "High", "Premium"]
    )
    model_df["services_ratio"] = model_df["services_count"] / max(
        1, len(available_service_cols)
    )
    model_df["has_streaming_bundle"] = (
        (model_df.get("streaming_tv", 0) == 1)
        & (model_df.get("streaming_movies", 0) == 1)
    ).astype(int)
    model_df["security_plus_support"] = (
        (model_df.get("online_security", 0) == 1)
        & (model_df.get("tech_support", 0) == 1)
    ).astype(int)
    model_df["auto_pay_flag"] = model_df["payment_method"].astype(str).str.contains(
        "automatic", case=False
    ).astype(int)
    model_df["avg_charge_per_service"] = model_df["monthly_charges"] / (
        model_df["services_count"].replace(0, np.nan)
    )
    model_df["avg_charge_per_service"] = model_df["avg_charge_per_service"].fillna(
        model_df["monthly_charges"]
    )
    model_df["revenue_vs_contract"] = model_df["avg_revenue_per_month"] / model_df[
        "contract_months"
    ].replace(0, 1)

    # Log transforms
    model_df["log_total_charges"] = np.log1p(model_df["total_charges"])
    model_df["log_monthly_charges"] = np.log1p(model_df["monthly_charges"])

    # Align identifier naming
    if "customerid" in model_df.columns and "customer_id" not in model_df.columns:
        model_df = model_df.rename(columns={"customerid": "customer_id"})

    return model_df


__all__ = ["load_and_clean_data", "feature_engineer_data"]

