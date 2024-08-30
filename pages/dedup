import pandas as pd
import streamlit as st
import io

def remove_duplicates_from_csvs(file1, file2):
    """
    Remove duplicates from two CSV files and return the result as a DataFrame.
    
    Args:
    file1 (io.BytesIO): First uploaded CSV file
    file2 (io.BytesIO): Second uploaded CSV file
    
    Returns:
    pd.DataFrame: Deduplicated DataFrame
    """
    # Read both CSV files
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)
    
    # Concatenate the dataframes
    combined_df = pd.concat([df1, df2], ignore_index=True)
    
    # Remove duplicates
    deduplicated_df = combined_df.drop_duplicates()
    
    return deduplicated_df

st.title("CSV Duplicate Remover")

st.write("Upload two CSV files to remove duplicates")

file1 = st.file_uploader("Choose the first CSV file", type="csv")
file2 = st.file_uploader("Choose the second CSV file", type="csv")

if file1 is not None and file2 is not None:
    if st.button("Remove Duplicates"):
        result_df = remove_duplicates_from_csvs(file1, file2)
        st.write("Duplicates removed. Preview of the result:")
        st.dataframe(result_df.head())
        
        # Provide download link for the result
        csv = result_df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="output_without_duplicates.csv",
            mime="text/csv",
        )
