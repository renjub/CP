import os
import pandas as pd

def combine_csv_files_from_subfolders(output_file='MouthShut.csv'):
    # Get the current working directory
    cwd = os.getcwd()
    
    combined_data = []
    
    # Walk through all subdirectories under 'Reviews'
    reviews_dir = os.path.join(cwd, 'Reviews')
    for root, dirs, files in os.walk(reviews_dir):
        for file in files:
            if file.endswith('.csv'):
                try:
                    file_path = os.path.join(root, file)
                    # Read each CSV file into a DataFrame
                    df = pd.read_csv(file_path)
                    # Add a column for the source file name
                    df['Source File'] = file
                    # Add a column for the folder name
                    df['Folder'] = os.path.basename(root)
                    combined_data.append(df)
                    print(f"Processed file: {file_path}")
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
    
    # Combine all DataFrames
    if combined_data:
        combined_df = pd.concat(combined_data, ignore_index=True)
        # Save the combined DataFrame to a new CSV file
        combined_df.to_csv(output_file, index=False)
        print(f"Combined CSV saved as {output_file}")
    else:
        print("No CSV files found in subfolders.")

# Run the function
combine_csv_files_from_subfolders()
