import pandas as pd

sold = pd.read_csv("/Users/satvikigutta/Downloads/idx_files/combined_sold_residential.csv")
listing = pd.read_csv("/Users/satvikigutta/Downloads/idx_files/combined_listing_residential.csv")

print("done loading!")
print(sold.shape) #how many rows and columns in the sold dataset
print(listing.shape)
print(sold.columns.tolist()) #all the column names in the sold dataset
print(sold["PropertyType"].unique()) #checking if it is only residential properties in the sold dataset
print(listing["PropertyType"].unique()) #checking if it is only residential properties in the listing dataset
print(sold.isnull().sum()) #checking for missing values in the sold dataset
null_percent = sold.isnull().sum() / len(sold) * 100
print(null_percent[null_percent > 90]) #printing columns with more than 90% missing values
null_percent = sold.isnull().sum() / len(sold) * 100
high_null = null_percent[null_percent > 90]
high_null.to_csv("sold_high_null_columns.csv") #saving the columns with more than 90% missing values to a csv file
print("saved!")
null_percent_listings = listing.isnull().sum() / len(listing) * 100
high_null_listings = null_percent_listings[null_percent_listings > 90]
high_null_listings.to_csv("listings_high_null_columns.csv") #saving the columns with more than 90% missing values to a csv file
print(high_null_listings)
pd.set_option("display.float_format", "{:,.2f}".format) #clean up the display of float numbers to 2 decimal places
print(sold["ClosePrice"].describe()) #printing the summary statistics for the ClosePrice column in the sold dataset
print(sold["LivingArea"].describe()) #summary for LivingArea column
print(sold["DaysOnMarket"].describe()) #summary for DaysOnMarket column
summary = sold[["ClosePrice", "LivingArea", "DaysOnMarket"]].describe()
summary.to_csv("sold_distribution_summary.csv") #save the summary statistics to a csv file
print("saved!")
import os
os.chdir("/Users/satvikigutta/Downloads/idx_files")
import requests

url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=MORTGAGE30US"
response = requests.get(url, verify=False)

import io

# Read the FRED API response text into a DataFrame, parsing the date column as datetime
mortgage = pd.read_csv(io.StringIO(response.text), parse_dates=["observation_date"])

# Rename columns to something more readable/usable
mortgage.columns = ["date", "rate_30yr_fixed"]

# Sanity check: preview first 5 rows of the mortgage rate data
print(mortgage.head())

# Convert each date to a year-month period (e.g. 2026-07) so daily rates can be grouped by month
mortgage["year_month"] = mortgage["date"].dt.to_period("M")

# Average the daily/weekly mortgage rates within each month to get one rate per month
mortgage_monthly = mortgage.groupby("year_month")["rate_30yr_fixed"].mean().reset_index()

# Sanity check: preview the monthly averaged rates
print(mortgage_monthly.head())

# Create a year_month column on the sold listings, based on when each sale closed
sold["year_month"] = pd.to_datetime(sold["CloseDate"]).dt.to_period("M")

# Create a year_month column on the active/all listings, based on when each was listed
listing["year_month"] = pd.to_datetime(listing["ListingContractDate"]).dt.to_period("M")

# Sanity check: preview the new year_month column on sold data
print(sold["year_month"].head())

# Left join sold listings with monthly mortgage rates, matching on year_month
sold_with_rates = sold.merge(mortgage_monthly, on="year_month", how="left")

# Left join all listings with monthly mortgage rates, matching on year_month
listing_with_rates = listing.merge(mortgage_monthly, on="year_month", how="left")

print("merge done!")

# Check how many rows failed to get a matching rate (nulls = missing mortgage data for that month)
print(sold_with_rates["rate_30yr_fixed"].isnull().sum())
print(listing_with_rates["rate_30yr_fixed"].isnull().sum())

# Save the enriched datasets to CSV files, without the index column
sold_with_rates.to_csv("sold_enriched_with_rates.csv", index=False)
listing_with_rates.to_csv("listing_enriched_with_rates.csv", index=False)

print("saved!")
