import os
import pandas as pd

def combine_csv_files(root_folder, output_file):
    """
    Combines all .csv files in the given folder and its subfolders into a single .csv file.

    Parameters:
    root_folder (str): The root folder to search for .csv files.
    output_file (str): The output file to save the combined .csv.
    """
    # List to store dataframes
    combined_data = []

    # Walk through all files and directories in the root folder
    for subdir, _, files in os.walk(root_folder):
        for file in files:
            if file.endswith('.csv'):
                file_path = os.path.join(subdir, file)
                try:
                    # Read CSV file into a dataframe
                    df = pd.read_csv(file_path)
                    combined_data.append(df)
                    print(f"`Processed:` {file_path}")
                except Exception as e:
                    print(f"`Error reading:` {file_path} - {e}")

    # Combine all dataframes
    if combined_data:
        final_df = pd.concat(combined_data, ignore_index=True)
        # Save to the output file
        final_df.to_csv(output_file, index=False)
        print(f"`Combined CSV saved to:` {output_file}")
    else:
        print("`No CSV files found to combine.`")

# Usage
root_folder = './reviews'  # Replace with your folder path
output_file = 'Bikewale.csv'    # Replace with your desired output file name
combine_csv_files(root_folder, output_file)
