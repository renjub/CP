import os
import pandas as pd

def combine_csvs_in_subfolders(output_file="combined.csv"):
    """
    Combine all CSV files from subfolders into a single CSV file.

    Parameters:
        output_file (str): Name of the output CSV file.
    """
    combined_data = []  # List to store DataFrames from each CSV file

    # Walk through subdirectories only
    for root, dirs, files in os.walk(os.getcwd()):
        if root == os.getcwd():  # Skip the root directory
            continue
        
        for file in files:
            if file.endswith(".csv"):  # Process only CSV files
                file_path = os.path.join(root, file)
                print(f"Processing: {file_path}")

                try:
                    # Read each CSV and append to the combined list
                    df = pd.read_csv(file_path)
                    combined_data.append(df)
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")

    # Concatenate all the DataFrames
    if combined_data:
        combined_df = pd.concat(combined_data, ignore_index=True)
        combined_df.to_csv(output_file, index=False)
        print(f"All CSVs combined into: {output_file}")
    else:
        print("No CSV files found in subfolders.")

# Call the function
combine_csvs_in_subfolders("combined.csv")
