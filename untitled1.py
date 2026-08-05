# -*- coding: utf-8 -*-

#install geopandas
get_ipython().system('pip install geopandas -q')


# imports
import numpy as np
import pandas as pd
import geopandas as gpd

REQUIRED_COLUMNS = [
    "ClosePrice", "OriginalListPrice", "LivingArea", "DaysOnMarket",
    "CloseDate", "PurchaseContractDate", "ListingContractDate",
    "PropertyType", "CountyOrParish", "Latitude", "Longitude",
]

METRIC_COLUMNS = [
    "PropertyType", "CountyOrParish",
    "PriceRatio", "CloseToOriginalListRatio", "PricePerSqFt",
    "DaysOnMarket", "Year", "Month", "YrMo",
    "ListingToContractDays", "ContractToCloseDays",
]


# load the cleaned data from Weeks 4-5
sold = pd.read_csv("sold_cleaned_flagged.csv", low_memory=False)
listing = pd.read_csv("listing_cleaned_flagged.csv", low_memory=False)

print(f"sold shape:    {sold.shape}")
print(f"listing shape: {listing.shape}")

missing_sold = [c for c in REQUIRED_COLUMNS if c not in sold.columns]
missing_listing = [c for c in REQUIRED_COLUMNS if c not in listing.columns]
if missing_sold:
    raise ValueError(f"sold is missing required column(s): {missing_sold}")
if missing_listing:
    raise ValueError(f"listing is missing required column(s): {missing_listing}")


# feature engineering function
def engineer_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Adds the Week 6 engineered market metric columns to a copy of df."""
    out = df.copy()

    for col in ["CloseDate", "PurchaseContractDate", "ListingContractDate"]:
        out[col] = pd.to_datetime(out[col], errors="coerce")

    # Guard against zero/negative denominators (real data has some) and
    # rows already flagged bad in Weeks 4-5, so we get NaN instead of inf.
    valid_price = out["OriginalListPrice"].where(out["OriginalListPrice"] > 0)
    valid_area = out["LivingArea"].where(out["LivingArea"] > 0)
    clean_mask = ~out.get("invalid_nums", pd.Series(False, index=out.index)).fillna(False)

    out["PriceRatio"] = np.where(clean_mask, out["ClosePrice"] / valid_price, np.nan)
    # Handbook lists this separately from Price Ratio; same underlying formula.
    out["CloseToOriginalListRatio"] = out["PriceRatio"]
    out["PricePerSqFt"] = np.where(clean_mask, out["ClosePrice"] / valid_area, np.nan)

    out["Year"] = out["CloseDate"].dt.year
    out["Month"] = out["CloseDate"].dt.month
    out["YrMo"] = out["CloseDate"].dt.to_period("M").astype(str).replace("NaT", np.nan)

    out["ListingToContractDays"] = (
        out["PurchaseContractDate"] - out["ListingContractDate"]
    ).dt.days
    out["ContractToCloseDays"] = (
        out["CloseDate"] - out["PurchaseContractDate"]
    ).dt.days

    return out


sold = engineer_metrics(sold)
listing = engineer_metrics(listing)


# school district spatial join
def load_school_districts(shapefile_path: str) -> gpd.GeoDataFrame:
    """Loads the CA school district shapefile and reprojects to EPSG:4326.

    NOTE: the source shapefile ships in EPSG:3857 (Web Mercator), not
    EPSG:4326. Joining against raw Latitude/Longitude points without
    reprojecting first doesn't raise an error - geopandas just emits a
    UserWarning and silently returns all-NaN matches. Always reproject
    before the spatial join.
    """
    districts = gpd.read_file(shapefile_path)
    if districts.crs is None or districts.crs.to_epsg() != 4326:
        districts = districts.to_crs("EPSG:4326")
    return districts[["DistrictNa", "DistrictTy", "CountyName", "geometry"]]


def add_school_district(
    df: pd.DataFrame,
    districts: gpd.GeoDataFrame,
    lat_col: str = "Latitude",
    lon_col: str = "Longitude",
) -> pd.DataFrame:
    """Spatial-joins each row's lat/long against school district polygons."""
    out = df.copy()
    out["SchoolDistrictName"] = pd.Series(pd.NA, index=out.index, dtype="object")
    out["SchoolDistrictType"] = pd.Series(pd.NA, index=out.index, dtype="object")

    has_coords = out[lat_col].notna() & out[lon_col].notna()
    if not has_coords.any():
        return out

    points = gpd.GeoDataFrame(
        out.loc[has_coords, [lat_col, lon_col]],
        geometry=gpd.points_from_xy(out.loc[has_coords, lon_col], out.loc[has_coords, lat_col]),
        crs="EPSG:4326",
    )
    joined = gpd.sjoin(points, districts, how="left", predicate="within")
    # A property that sits exactly on a shared boundary can match more than
    # one polygon; keep the first match per original row.
    joined = joined[~joined.index.duplicated(keep="first")]

    out.loc[has_coords, "SchoolDistrictName"] = joined["DistrictNa"]
    out.loc[has_coords, "SchoolDistrictType"] = joined["DistrictTy"]
    return out


districts = load_school_districts("DistrictAreas2425.shp")
print(f"Loaded {len(districts)} school district polygons")

sold = add_school_district(sold, districts)
listing = add_school_district(listing, districts)

matched = sold["SchoolDistrictName"].notna().sum()
print(f"School district matched for {matched:,} / {len(sold):,} sold rows ({matched / len(sold):.1%})")


# sample output table
print("\nSample of engineered metrics (fully-populated rows):")
non_id_cols = [c for c in METRIC_COLUMNS if c not in ("PropertyType", "CountyOrParish")]
sample = sold.dropna(subset=non_id_cols).head(10)
sample[METRIC_COLUMNS + ["SchoolDistrictName"]]


# segmented summary
def segment_summary(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    return (
        df.groupby(group_col, dropna=False)
        .agg(
            sales=("ClosePrice", "count"),
            median_close=("ClosePrice", "median"),
            median_ppsf=("PricePerSqFt", "median"),
            median_dom=("DaysOnMarket", "median"),
            median_price_ratio=("PriceRatio", "median"),
            avg_price_ratio=("PriceRatio", "mean"),
        )
        .round(3)
        .sort_values("sales", ascending=False)
    )

print("\nSegmented summary by CountyOrParish (top 15):")
segment_summary(sold, "CountyOrParish").head(15)


# save engineered datasets
sold.to_csv("sold_feature_engineered.csv", index=False)
listing.to_csv("listing_feature_engineered.csv", index=False)
print("\nSaved sold_feature_engineered.csv and listing_feature_engineered.csv")
