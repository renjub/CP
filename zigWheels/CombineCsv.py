import os
import pandas as pd

# Define the folder containing CSV files
folder_path = 'reviews'

# Get a list of all CSV files in the folder
csv_files = [file for file in os.listdir(folder_path) if file.endswith('.csv')]

# Combine all CSV files
combined_data = pd.DataFrame()

for file in csv_files:
    file_path = os.path.join(folder_path, file)
    data = pd.read_csv(file_path)
    combined_data = pd.concat([combined_data, data], ignore_index=True)

# Save the combined data to a new CSV file
combined_data.to_csv('Zigwheels.csv', index=False)

print("Combined CSV file saved as `Zigwheels.csv`")