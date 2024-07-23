import streamlit as st
import pandas as pd
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import os

# Set up OAuth 2.0 flow
flow = Flow.from_client_secrets_file(
    'path/to/your/client_secret.json',
    scopes=['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/userinfo.email']
)
flow.redirect_uri = 'https://working.streamlit.app/'  # Update this with your deployed app URL

def process_data(df):
    if df is not None and not df.empty:
        # Calculate mean of numeric columns
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
        if not numeric_cols.empty:
            means = df[numeric_cols].mean()
            st.subheader("Mean values of numeric columns:")
            st.write(means)
        else:
            st.write("No numeric columns found for processing.")

        # Count unique values in string columns
        string_cols = df.select_dtypes(include=['object']).columns
        if not string_cols.empty:
            unique_counts = df[string_cols].nunique()
            st.subheader("Unique value counts in string columns:")
            st.write(unique_counts)
        else:
            st.write("No string columns found for processing.")
    else:
        st.write("No data to process.")

def main():
    st.title("Google Sheets Integration with OAuth")

    if 'credentials' not in st.session_state:
        st.session_state.credentials = None

    if st.session_state.credentials is None:
        if 'code' not in st.experimental_get_query_params():
            auth_url, _ = flow.authorization_url(prompt='consent')
            st.markdown(f'Please [login with Google]({auth_url})')
        else:
            code = st.experimental_get_query_params()['code'][0]
            flow.fetch_token(code=code)
            st.session_state.credentials = flow.credentials
            st.experimental_rerun()
    else:
        credentials = st.session_state.credentials
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())

        service = build('sheets', 'v4', credentials=credentials)

        st.header("Upload CSV to Google Sheets")
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            st.write("Uploaded Data:")
            st.write(df)

            sheet_id = st.text_input("Enter Google Sheet ID for upload:")
            worksheet_name = st.text_input("Enter Worksheet name for upload:")
            if st.button("Upload to Google Sheets"):
                try:
                    body = {
                        'values': [df.columns.tolist()] + df.values.tolist()
                    }
                    result = service.spreadsheets().values().update(
                        spreadsheetId=sheet_id, range=f'{worksheet_name}!A1',
                        valueInputOption='RAW', body=body).execute()
                    st.success(f"Data uploaded successfully! {result.get('updatedCells')} cells updated.")
                except Exception as e:
                    st.error(f"Error uploading to Google Sheet: {e}")

            st.subheader("Data Processing Results:")
            process_data(df)

        st.header("Download from Google Sheets")
        download_sheet_id = st.text_input("Enter Google Sheet ID for download:")
        download_worksheet_name = st.text_input("Enter Worksheet name for download:")
        if st.button("Download from Google Sheets"):
            try:
                result = service.spreadsheets().values().get(
                    spreadsheetId=download_sheet_id, range=download_worksheet_name).execute()
                values = result.get('values', [])
                if not values:
                    st.warning('No data found.')
                else:
                    df = pd.DataFrame(values[1:], columns=values[0])
                    st.write("Downloaded Data:")
                    st.write(df)
                    
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="Download data as CSV",
                        data=csv,
                        file_name="downloaded_data.csv",
                        mime="text/csv",
                    )

                    st.subheader("Data Processing Results:")
                    process_data(df)
            except Exception as e:
                st.error(f"Error downloading from Google Sheet: {e}")

        if st.button("Logout"):
            st.session_state.credentials = None
            st.experimental_rerun()

if __name__ == "__main__":
    main()
