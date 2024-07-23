import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import csv
import os

def process_csv(file_path):
    try:
        df = pd.read_csv(file_path)
        print(f"Successfully loaded CSV file: {file_path}")
        return df
    except Exception as e:
        print(f"Error loading CSV file: {e}")
        return None

def process_google_sheet(sheet_id, worksheet_name):
    try:
        # Set up credentials
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds_file = 'path/to/your/credentials.json'
        
        if not os.path.exists(creds_file):
            print(f"Credentials file not found: {creds_file}")
            return None
        
        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file, scope)
        client = gspread.authorize(creds)

        # Open the sheet
        sheet = client.open_by_key(sheet_id).worksheet(worksheet_name)

        # Get all values
        data = sheet.get_all_values()

        # Convert to dataframe
        df = pd.DataFrame(data[1:], columns=data[0])
        print(f"Successfully loaded Google Sheet: {sheet_id}, Worksheet: {worksheet_name}")
        return df
    except Exception as e:
        print(f"Error loading Google Sheet: {e}")
        return None

def process_data(df):
    if df is not None and not df.empty:
        # Example processing: calculate mean of numeric columns
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
        if not numeric_cols.empty:
            means = df[numeric_cols].mean()
            print("\nMean values of numeric columns:")
            print(means)
        else:
            print("No numeric columns found for processing.")
        
        # Example processing: count unique values in string columns
        string_cols = df.select_dtypes(include=['object']).columns
        if not string_cols.empty:
            unique_counts = df[string_cols].nunique()
            print("\nUnique value counts in string columns:")
            print(unique_counts)
        else:
            print("No string columns found for processing.")
    else:
        print("No data to process.")

def main():
    while True:
        input_type = input("Enter 'csv' for CSV file, 'sheet' for Google Sheet, or 'quit' to exit: ").lower()

        if input_type == 'quit':
            print("Exiting the program.")
            break

        if input_type == 'csv':
            file_path = input("Enter the path to your CSV file: ")
            df = process_csv(file_path)
        elif input_type == 'sheet':
            sheet_id = input("Enter the Google Sheet ID: ")
            worksheet_name = input("Enter the worksheet name: ")
            df = process_google_sheet(sheet_id, worksheet_name)
        else:
            print("Invalid input type. Please enter 'csv', 'sheet', or 'quit'.")
            continue

        if df is not None:
            print("\nFirst few rows of the data:")
            print(df.head())
            
            process_data(df)
        
        print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    main()
