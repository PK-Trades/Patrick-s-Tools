import streamlit as st
import pandas as pd
from dateutil import parser
import base64
import csv
import io

def parse_date(date_string):
    try:
        return parser.parse(date_string).date()
    except (ValueError, TypeError):
        return None

def process_data(data, thresholds, older_than_date):
    data['Average position'] = data['Average position'].astype(float)
    data['Laatste wijziging'] = data['Laatste wijziging'].astype(str).apply(parse_date)
    data['Unique Inlinks'] = data['Unique Inlinks'].astype(int)

    def should_delete(row):
        conditions = []
        for key, value in thresholds.items():
            if key == 'Average position':
                conditions.append(row[key] > value)
            elif key in row:
                conditions.append(row[key] < value)
        
        if older_than_date and row['Laatste wijziging']:
            conditions.append(row['Laatste wijziging'] < older_than_date)
        
        return all(conditions)

    data['To Delete'] = data.apply(should_delete, axis=1)
    data['Backlinks controleren'] = (data['To Delete'] &
        (data['Ahrefs Backlinks - Exact'] > thresholds.get('Backlinks', float('inf'))))
    
    data['Action'] = 'Geen actie'
    data.loc[data['To Delete'], 'Action'] = 'Verwijderen'
    data.loc[data['Backlinks controleren'], 'Action'] = 'Backlinks controleren'

    return data

def main():
    st.title("Patrick's Cleanup Tool")
    st.write("Hier onder kun je aangeven waar je post MINIMAAL aan moet voldoen om NIET in aanmerking te komen voor verwijdering./n Wanneer je een waarde van 1000 invult bij Sessie komen alle URLs met minder dan 1000 sessie in aanmerking voor verwijderen (als alle overige metrics ook kloppen)")
    st.markdown("Maak een kopie van het template hieronder en vul deze met jouw data. "
                "Vervolgens kun je hem hierboven uploaden en zal de tool aan de hand van de door jou ingestelde criteria de URLs die wegkunnen markeren")
    st.markdown("[het template hieronder](https://docs.google.com/spreadsheets/d/1GtaLaXO62Rf8Xo2gNiw6wkAXrHoE-bBJr8Uf3_e8lNw/edit?usp=sharing)")

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
    }

    older_than = st.date_input("Older than", value=pd.to_datetime("2023-01-01"))

    threshold_checks = {}
    for key in thresholds:
        threshold_checks[key] = st.checkbox(f"Apply {key} threshold", value=True)

    output_mode = st.radio("Output mode", ["Show all URLs", "Show only URLs with actions"])

    start_button = st.button("Start Processing")

    if start_button and uploaded_file is not None:
        try:
            csv_content = uploaded_file.getvalue().decode('utf-8')
            dialect = csv.Sniffer().sniff(csv_content[:1024])
            delimiter = dialect.delimiter
            csv_file = io.StringIO(csv_content)
            data = pd.read_csv(csv_file, delimiter=delimiter)

            required_columns = ['Sessions', 'Views', 'Clicks', 'Impressions', 'Average position', 'Ahrefs Backlinks - Exact', 'Word Count', 'Laatste wijziging', 'Unique Inlinks']
            missing_columns = [col for col in required_columns if col not in data.columns]

            if missing_columns:
                st.error(f"Missing columns in CSV: {', '.join(missing_columns)}")
            else:
                applied_thresholds = {k: v for k, v in thresholds.items() if threshold_checks[k]}

                processed_data = process_data(data, applied_thresholds, older_than)

                if output_mode == "Show only URLs with actions":
                    action_data = processed_data[processed_data['Action'] != 'Geen actie']
                else:
                    action_data = processed_data

                if action_data.empty:
                    st.write("No URLs require action.")
                else:
                    st.dataframe(action_data)
                    
                    csv_string = action_data.to_csv(index=False)
                    
                    st.download_button(
                        label="Download CSV",
                        data=csv_string,
                        file_name="processed_data.csv",
                        mime="text/csv"
                    )

        except Exception as e:
            st.error(f"Failed to process CSV file: {str(e)}")

    elif start_button and uploaded_file is None:
        st.error("Please upload a CSV file before starting the process.")

if __name__ == "__main__":
    main()
