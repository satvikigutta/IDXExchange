

import pandas as pd


# These are the three columns we're checking for outliers.
COLUMNS_TO_CHECK = ["ClosePrice", "LivingArea", "DaysOnMarket"]


def add_business_rule_flags(df):

    #Step 1: Catch values that are ALWAYS invalid

    # ClosePrice should never be zero or negative
    if "ClosePrice" in df.columns:
        df["invalid_price_flag"] = df["ClosePrice"] <= 0
    else:
        df["invalid_price_flag"] = False

    # LivingArea (square footage) should never be zero or negative
    if "LivingArea" in df.columns:
        df["invalid_area_flag"] = df["LivingArea"] <= 0
    else:
        df["invalid_area_flag"] = False

    # DaysOnMarket should never be negative (can't sell before listing)
    if "DaysOnMarket" in df.columns:
        df["invalid_dom_flag"] = df["DaysOnMarket"] < 0
    else:
        df["invalid_dom_flag"] = False

    return df


def add_iqr_outlier_flags(df, columns):
    """
    Step 2: For each column in `columns`, calculate the IQR (the
    "middle 50%" of the data) and flag anything that falls far outside
    of it as a statistical outlier.
    """

    for column in columns:

        # Skip a column if it's not in this dataset
        if column not in df.columns:
            print(f"  Skipping '{column}' -- not found in this dataset")
            continue

        # Calculate the IQR bounds for this column
        q1 = df[column].quantile(0.25)
        q3 = df[column].quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        # Create the flag column: True if the value is outside the bounds
        flag_column_name = column + "_outlier_flag"
        df[flag_column_name] = (df[column] < lower_bound) | (df[column] > upper_bound)

        # Print out what we found, so we can see the math happening
        num_outliers = df[flag_column_name].sum()
        print(f"  {column}: normal range is {lower_bound:,.2f} to {upper_bound:,.2f}")
        print(f"    -> {num_outliers:,} records flagged as outliers")

    return df


def print_before_after_comparison(original_df, clean_df, columns):
    """
    Step 5: print out how the dataset changed after filtering -- record count and median values.
    """

    print()
    print("=" * 60)
    print("BEFORE vs AFTER FILTERING")
    print("=" * 60)

    print(f"Record count before: {len(original_df):,}")
    print(f"Record count after:  {len(clean_df):,}")
    num_removed = len(original_df) - len(clean_df)
    print(f"Records removed:     {num_removed:,}")

    print()
    for column in columns:
        if column not in original_df.columns:
            continue
        median_before = original_df[column].median()
        median_after = clean_df[column].median()
        print(f"{column} median before: {median_before:,.2f}")
        print(f"{column} median after:  {median_after:,.2f}")
        print()


def process_one_dataset(input_file, output_name):
   #save CSVs

    print()
    print("#" * 60)
    print(f"PROCESSING: {input_file}")
    print("#" * 60)

    # --- Load the data ---
    print(f"Loading {input_file} ...")
    df = pd.read_csv(input_file, low_memory=False)
    print(f"  Loaded {len(df):,} rows and {len(df.columns)} columns")

    # --- Step 1: business rule flags ---
    print()
    print("Checking business rules...")
    df = add_business_rule_flags(df)

    # --- Step 2: IQR outlier flags ---
    print()
    print("Checking for statistical outliers with the IQR method...")
    df = add_iqr_outlier_flags(df, COLUMNS_TO_CHECK)

    # --- Combine all the flags into one "should this be removed?" column ---
    # A record gets removed if ANY flag is True (business rule OR outlier)
    flag_columns = [
        "invalid_price_flag",
        "invalid_area_flag",
        "invalid_dom_flag",
    ]
    for column in COLUMNS_TO_CHECK:
        outlier_column = column + "_outlier_flag"
        if outlier_column in df.columns:
            flag_columns.append(outlier_column)

    df["any_flag"] = df[flag_columns].any(axis=1)

    # --- Step 3: save the FULL dataset (nothing deleted, just flagged) ---
    full_output_file = output_name + "_flagged_full.csv"
    df.to_csv(full_output_file, index=False)
    print()
    print(f"Saved full flagged dataset to: {full_output_file}")

    # --- Step 4: save the CLEAN dataset (flagged rows removed) ---
    clean_df = df[df["any_flag"] == False].copy()
    # Drop the helper flag columns so the clean file just looks like normal data
    clean_df = clean_df.drop(columns=flag_columns + ["any_flag"], errors="ignore")

    clean_output_file = output_name + "_filtered_clean.csv"
    clean_df.to_csv(clean_output_file, index=False)
    print(f"Saved clean filtered dataset to: {clean_output_file}")

    # --- Step 5: print the written comparison ---
    print_before_after_comparison(df, clean_df, COLUMNS_TO_CHECK)


#run script
if __name__ == "__main__":

    listing_file = "/Users/satvikigutta/Downloads/idx_files/listing_feature_engineered.csv"
    sold_file = "/Users/satvikigutta/Downloads/idx_files/sold_feature_engineered.csv"

    process_one_dataset(listing_file, "listing")
    process_one_dataset(sold_file, "sold")
