import streamlit as st
import pandas as pd
from dateutil import parser
import csv
import io
import traceback

## Data Processing Functions

### Function to parse date strings
def parse_date(date_string):
    try:
        return parser.parse(date_string).date()
    except (ValueError, TypeError):
        return None

### Function to process data
def process_data(data, thresholds, older_than_date):
    # ... (keep the rest of this function as it was)

## UI Setup Functions

### Function to set up the UI
def setup_ui():
    # ... (keep this function as it was)

### Function to display results
def display_results(data):
    # ... (keep this function as it was)

### Function to convert semicolon to comma delimiter
def convert_semicolon_to_comma(file_content):
    # Read the CSV content with semicolon delimiter
    df = pd.read_csv(io.StringIO(file_content), sep=';')
    
    # Convert the DataFrame back to CSV string with comma delimiter
    return df.to_csv(index=False)

### Function to detect delimiter
def detect_delimiter(file_content, sample_size=1024):
    sniffer = csv.Sniffer()
    delimiters = [',', ';', '\t', '|']  # Common delimiters to check
    
    # Try with CSV Sniffer first
    try:
        dialect = sniffer.sniff(file_content[:sample_size])
        return dialect.delimiter
    except:
        pass
    
    # Fallback: Check for common delimiters
    for delimiter in delimiters:
        try:
            pd.read_csv(io.StringIO(file_content[:sample_size]), sep=delimiter, engine='python')
            return delimiter
        except:
            continue
    
    # If all else fails, return None
    return None

## Main Application Logic

def main():
    setup_ui()
    uploaded_file = st.file_uploader("Select CSV file", type="csv")
    thresholds = {
        'Sessions': st.number_input("Sessions", value=1000, min_value=0),
        'Views': st.number_input("Views", value=1000, min_value=0),
        'Clicks': st.number_input("Clicks", value=50, min_value=0),
        'Impressions': st.number_input("Impressions", value=500, min_value=0),
        'Average position': st.number_input("Average position", value=19.0, min_value=0.0),
        'Backlinks': st.number_input("Backlinks", value=1, min_value=0),
        'Word Count': st.number_input("Word Count", value=500, min_value=0),
        'Unique Inlinks': st.number_input("Unique Inlinks", value=0, min_value=0),
        'Ahrefs URL Rating - Exact': st.number_input("Ahrefs URL Rating - Exact", value=5, min_value=0),
        'Ahrefs Keywords Top 3 - Exact': st.number_input("Ahrefs Keywords Top 3 - Exact", value=1, min_value=0),
        'Ahrefs Keywords Top 10 - Exact': st.number_input("Ahrefs Keywords Top 10 - Exact", value=2, min_value=0),
    }
    older_than = st.date_input("Older than", value=pd.to_datetime("2023-01-01"))
    threshold_checks = {}
    for key in thresholds:
        threshold_checks[key] = st.checkbox(f"Apply {key} threshold", value=True)
    output_mode = st.radio("Output mode", ["Show all URLs", "Show only URLs with actions"])
    start_button = st.button("Start Processing")
    
    if start_button and uploaded_file is not None:
        try:
            # Read the CSV content
            csv_content = uploaded_file.getvalue().decode('utf-8')
            
            # Detect delimiter
            delimiter = detect_delimiter(csv_content)
            
            if delimiter is None:
                st.error("Could not determine delimiter. Please check your CSV file format.")
                return
            
            # If delimiter is semicolon, convert to comma
            if delimiter == ';':
                st.info("Semicolon delimiter detected. Converting to comma delimiter.")
                csv_content = convert_semicolon_to_comma(csv_content)
                delimiter = ','
            
            # Read the CSV using the detected (or converted) delimiter
            data = pd.read_csv(io.StringIO(csv_content), sep=delimiter, engine='python')
            
            # Display the first few rows of the DataFrame
            st.write("Preview of the uploaded data:")
            st.write(data.head())
            
            # Display all column names
            st.write("Columns found in the CSV file:")
            st.write(list(data.columns))
            
            required_columns = ['Sessions', 'Views', 'Clicks', 'Impressions', 'Average position', 'Ahrefs Backlinks - Exact', 'Word Count', 'Laatste wijziging', 'Unique Inlinks']
            missing_columns = [col for col in required_columns if col not in data.columns]
            
            if missing_columns:
                st.error(f"Missing columns in CSV: {', '.join(missing_columns)}")
                st.write("Please ensure your CSV file contains all required columns.")
            else:
                applied_thresholds = {k: v for k, v in thresholds.items() if threshold_checks[k]}
                processed_data = process_data(data, applied_thresholds, older_than)
                if output_mode == "Show only URLs with actions":
                    action_data = processed_data[processed_data['Action'] != 'Geen actie']
                else:
                    action_data = processed_data
                display_results(action_data)
        except Exception as e:
            st.error(f"Failed to process CSV file: {str(e)}")
            st.write("Error details:", traceback.format_exc())
    elif start_button and uploaded_file is None:
        st.error("Please upload a CSV file before starting the process.")

if __name__ == "__main__":
    main()
