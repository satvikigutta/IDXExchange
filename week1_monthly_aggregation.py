# Import the libraries needed for the script
import pandas as pd
import glob
import os


# Set the folder path where all of the downloaded MLS CSV files are stored
# Replace this with the actual folder path on your computer
folder_path = folder_path = "/Users/satvikigutta/Downloads/idx files"


# Find all monthly sold files in the folder
# The * means it will match any file that starts with CRMLSSold and ends with .csv
sold_files = glob.glob(os.path.join(folder_path, "CRMLSSold*.csv"))

# Find all monthly listing files in the folder
# The * means it will match any file that starts with CRMLSListing and ends with .csv
listing_files = glob.glob(os.path.join(folder_path, "CRMLSListing*.csv"))


# -----------------------------
# COMBINE SOLD DATASETS
# -----------------------------

# Create an empty list to store each monthly sold dataframe
sold_dfs = []

# Loop through each sold CSV file
for file in sold_files:
    # Read the CSV file into a pandas dataframe
    df = pd.read_csv(file)

    # Print the row count for this individual monthly file before combining
    print(f"{os.path.basename(file)} sold rows before concatenation: {len(df)}")

    # Add the monthly dataframe to the list
    sold_dfs.append(df)

# Combine all monthly sold dataframes into one large sold dataframe
sold_combined = pd.concat(sold_dfs, ignore_index=True)

# Print the total number of sold rows after all monthly files are combined
print(f"Sold rows after concatenation: {len(sold_combined)}")

# Filter the combined sold dataset to include only Residential properties
sold_residential = sold_combined[sold_combined["PropertyType"] == "Residential"]

# Print the number of sold rows after filtering to Residential only
print(f"Sold rows after Residential filter: {len(sold_residential)}")

# Save the combined and filtered sold dataset as a new CSV file
sold_residential.to_csv(
    os.path.join(folder_path, "combined_sold_residential.csv"),
    index=False
)


# -----------------------------
# COMBINE LISTING DATASETS
# -----------------------------

# Create an empty list to store each monthly listing dataframe
listing_dfs = []

# Loop through each listing CSV file
for file in listing_files:
    # Read the CSV file into a pandas dataframe
    df = pd.read_csv(file)

    # Print the row count for this individual monthly file before combining
    print(f"{os.path.basename(file)} listing rows before concatenation: {len(df)}")

    # Add the monthly dataframe to the list
    listing_dfs.append(df)

# Combine all monthly listing dataframes into one large listing dataframe
listing_combined = pd.concat(listing_dfs, ignore_index=True)

# Print the total number of listing rows after all monthly files are combined
print(f"Listing rows after concatenation: {len(listing_combined)}")

# Filter the combined listing dataset to include only Residential properties
listing_residential = listing_combined[listing_combined["PropertyType"] == "Residential"]

# Print the number of listing rows after filtering to Residential only
print(f"Listing rows after Residential filter: {len(listing_residential)}")

# Save the combined and filtered listing dataset as a new CSV file
listing_residential.to_csv(
    os.path.join(folder_path, "combined_listing_residential.csv"),
    index=False
)


# Print a final message to confirm the script finished successfully
print("Done. Combined Residential sold and listing CSV files have been created.")