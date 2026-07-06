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

