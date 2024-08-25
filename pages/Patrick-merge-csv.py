import streamlit as st
import pandas as pd
import numpy as np
import chardet

def detect_encoding(file):
    with open(file, 'rb') as f:
        result = chardet.detect(f.read())
    return result['encoding']

def merge_csvs(file1, file2, delimiter1=',', delimiter2=','):
    df1 = pd.read_csv(file1, sep=delimiter1, encoding='utf-8', index_col=False)
    encoding2 = detect_encoding(file2)
    df2 = pd.read_csv(file2, sep=delimiter2, encoding=encoding2, index_col=False)
    
    common_columns = df1.columns.intersection(df2.columns)
    merged_df = pd.merge(df1, df2, on=common_columns, how='outer', indicator=True)
    
    # Identify unmatched rows
    unmatched = merged_df[merged_df['_merge'] == 'left_only']
    
    return merged_df, unmatched

def main():
    st.title("Merge CSV Files")
    st.write("This app merges two CSV files based on common columns.")
    
    # File uploaders
    file1 = st.file_uploader("Select the first CSV file", type=['csv'])
    file2 = st.file_uploader("Select the second CSV file", type=['csv'])
    
    # Delimiter selection
    delimiter1 = st.selectbox("Delimiter for the first file", [',', ';', '\t', '|'])
    delimiter2 = st.selectbox("Delimiter for the second file", [',', ';', '\t', '|'])
    
    # Merge button
    if st.button("Merge Files"):
        if file1 and file2:
            merged_df, unmatched = merge_csvs(file1, file2, delimiter1, delimiter2)
            
            # Display merged data
            st.write("Merged Data:")
            st.write(merged_df)
            
            # Display unmatched data
            if not unmatched.empty:
                st.write("\nUnmatched Rows:")
                st.write(unmatched)
            else:
                st.write("\nNo unmatched rows found.")
        else:
            st.error("Please select both files.")

if __name__ == "__main__":
    main()
