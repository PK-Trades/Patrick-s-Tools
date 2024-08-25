import streamlit as st
import pandas as pd
from dateutil import parser
import csv
import io
import traceback
from typing import Dict, Any

## Data Processing Functions

def parse_date(date_string: str) -> pd.Timestamp:
    try:
        return pd.to_datetime(date_string).date()
    except (ValueError, TypeError):
        return pd.NaT

def process_data(data: pd.DataFrame, thresholds: Dict[str, float], older_than_date: pd.Timestamp) -> pd.DataFrame:
    # Convert columns to appropriate types
    if 'Average position' in data.columns:
        data['Average position'] = pd.to_numeric(data['Average position'], errors='coerce')
    data['Laatste wijziging'] = pd.to_datetime(data['Laatste wijziging'], errors='coerce').dt.date
    if 'Unique Inlinks' in data.columns:
        data['Unique Inlinks'] = pd.to_numeric(data['Unique Inlinks'], errors='coerce').astype('Int64')

    def should_delete(row: pd.Series) -> bool:
        conditions = []
        for key, value in thresholds.items():
            if key in row:
                if key == 'Average position':
                    conditions.append(row[key] > value)
                else:
                    conditions.append(row[key] < value)
        if older_than_date and pd.notnull(row['Laatste wijziging']):
            conditions.append(row['Laatste wijziging'] < older_than_date)
        return all(conditions)

    data['To Delete'] = data.apply(should_delete, axis=1)
    data['Backlinks controleren'] = (data['To Delete'] & 
                                     (data['Ahrefs Backlinks - Exact'] > thresholds.get('Backlinks', float('inf'))) 
                                     if 'Ahrefs Backlinks - Exact' in data.columns else False)
    data['Action'] = 'Geen actie'
    data.loc[data['To Delete'], 'Action'] = 'Verwijderen'
    data.loc[data['Backlinks controleren'], 'Action'] = 'Backlinks controleren'
    return data

## UI Setup Functions

def setup_ui():
    st.title("Patrick's Cleanup Tool")
    st.markdown("Hier onder kun je aangeven waar je post :blue-background[minimaal] aan moet voldoen om :blue-background[niet] in aanmerking te komen voor verwijdering.")
    st.markdown("Wanneer je dus een waarde van 1000 invult bij Sessions komen alle URLs met minder dan 1000 sessie in aanmerking voor verwijderen (als alle overige metrics ook kloppen)")
    st.markdown("Maak een kopie van het template hieronder en vul deze met jouw data. ")
    st.markdown("Vervolgens kun je hem hierboven uploaden en zal de tool aan de hand van de door jou ingestelde criteria de URLs die wegkunnen markeren")
    st.markdown("[het template hieronder](https://docs.google.com/spreadsheets/d/1GtaLaXO62Rf8Xo2gNiw6wkAXrHoE-bBJr8Uf3_e8lNw/edit?usp=sharing)")

def display_results(data: pd.DataFrame) -> None:
    if data.empty:
        st.write("No URLs require action.")
    else:
        st.dataframe(data)
        csv_string = data.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv_string,
            file_name="processed_data.csv",
            mime="text/csv"
        )

def detect_delimiter(file_content: str) -> str:
    sniffer = csv.Sniffer()
    try:
        dialect = sniffer.sniff(file_content[:1024])
        return dialect.delimiter
    except csv.Error:
        # If sniffer fails, try common delimiters
        for delimiter in [',', ';', '\t', '|']:
            try:
                pd.read_csv(io.StringIO(file_content[:1024]), sep=delimiter, nrows=5)
                return delimiter
            except:
                continue
    return ','  # Default to comma if no delimiter is detected

## Main Application Logic

def main() -> None:
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
    threshold_checks = {key: st.checkbox(f"Apply {key} threshold", value=True) for key in thresholds}
    output_mode = st.radio("Output mode", ["Show all URLs", "Show only URLs with actions"])
    start_button = st.button("Start Processing")
    
    if start_button and uploaded_file is not None:
        try:
            csv_content = uploaded_file.getvalue().decode('utf-8')
            delimiter = detect_delimiter(csv_content)
            data = pd.read_csv(io.StringIO(csv_content), sep=delimiter, engine='python')
            
            required_columns = ['Laatste wijziging'] + [col for col in thresholds if threshold_checks[col]]
            missing_columns = [col for col in required_columns if col not in data.columns]
            
            if missing_columns:
                st.error(f"Missing columns in CSV: {', '.join(missing_columns)}")
                st.write("Please ensure your CSV file contains all required columns for the enabled thresholds.")
            else:
                applied_thresholds = {k: v for k, v in thresholds.items() if threshold_checks[k]}
                processed_data = process_data(data, applied_thresholds, older_than)
                action_data = processed_data[processed_data['Action'] != 'Geen actie'] if output_mode == "Show only URLs with actions" else processed_data
                display_results(action_data)
        except Exception as e:
            st.error(f"Failed to process CSV file: {str(e)}")
            st.write("Error details:", traceback.format_exc())
    elif start_button and uploaded_file is None:
        st.error("Please upload a CSV file before starting the process.")

if __name__ == "__main__":
    main()
