import streamlit as st
import pandas as pd
import csv
import io
import chardet

def detect_encoding(file):
    raw_data = file.read()
    file.seek(0)  # Reset file pointer
    result = chardet.detect(raw_data)
    return result['encoding']

def detect_delimiter(file, encoding):
    sample = file.read(1024).decode(encoding)
    file.seek(0)  # Reset file pointer
    sniffer = csv.Sniffer()
    try:
        dialect = sniffer.sniff(sample)
        return dialect.delimiter
    except:
        # If sniffer fails, try common delimiters
        for delimiter in [',', ';', '\t', '|']:
            try:
                pd.read_csv(io.StringIO(sample), sep=delimiter, nrows=5)
                return delimiter
            except:
                continue
    return ','  # Default to comma if no delimiter is detected

def read_csv_with_auto_detect(file):
    encoding = detect_encoding(file)
    delimiter = detect_delimiter(file, encoding)
    df = pd.read_csv(file, sep=delimiter, encoding=encoding, engine='python')
    return df

def merge_csvs(file1, file2):
    df1 = read_csv_with_auto_detect(file1)
    df2 = read_csv_with_auto_detect(file2)
    
    # Strip whitespace from column names
    df1.columns = df1.columns.str.strip()
    df2.columns = df2.columns.str.strip()
    
    common_columns = df1.columns.intersection(df2.columns)
    
    if not common_columns.empty:
        merged_df = pd.merge(df1, df2, on=list(common_columns), how='outer', indicator=True)
        unmatched = merged_df[merged_df['_merge'] != 'both']
        merged_df = merged_df[merged_df['_merge'] == 'both'].drop(columns=['_merge'])
    else:
        st.error("No common columns found between the two files.")
        return None, None

    return merged_df, unmatched

def main():
    st.title("Patrick's CSV Merger")
    st.markdown("This tool merges two CSV files based on common columns, automatically detecting delimiters and encodings.")

    file1 = st.file_uploader("Upload File 1", type="csv")
    file2 = st.file_uploader("Upload File 2", type="csv")

    if file1 and file2:
        if st.button("Merge CSVs"):
            merged_df, unmatched = merge_csvs(file1, file2)
            if merged_df is not None:
                st.success(f"Files merged successfully! Rows: {merged_df.shape[0]}, Columns: {merged_df.shape[1]}")
                st.dataframe(merged_df.head())

                csv = merged_df.to_csv(index=False)
                st.download_button(
                    label="Download merged CSV",
                    data=csv,
                    file_name="merged_csv.csv",
                    mime="text/csv"
                )

                if not unmatched.empty:
                    st.warning(f"There were {len(unmatched)} unmatched rows.")
                    unmatched_csv = unmatched.to_csv(index=False)
                    st.download_button(
                        label="Download unmatched rows",
                        data=unmatched_csv,
                        file_name="unmatched_rows.csv",
                        mime="text/csv"
                    )
    else:
        st.info("Please upload both CSV files to merge.")

if __name__ == "__main__":
    main()
    
