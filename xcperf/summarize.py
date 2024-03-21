import pandas as pd
import sys

process_name = sys.argv[1]
column0 = 'Process Name'
column1 ='% CPU'
column2 = 'Memory'

# Function to read CSV file, filter rows, and then select columns
def filter_rows_and_select_columns(process_name, column1, column2):
    file_path = f"sysmon-process.csv"
    # file_path = f"{process_name}-sysmon-process.csv"

    df = pd.read_csv(file_path, usecols=[column0, column1, column2])

    result_df = df[df[column0].str.contains(process_name, na=False)]

    result_df.loc[:, column1] = result_df.loc[:, column1].str.replace('%', '').astype(float)
    result_df.loc[:, column2] = result_df.loc[:, column2].str.replace('MiB', '').astype(float)
    # print(result_df)

    average1 = result_df[column1].mean(skipna=True)
    print(f'Average={average1:.2f}')
    max_value1 = result_df[column1].max()
    print(f'Maximum={max_value1}')

    average2 = result_df[column2].mean(skipna=True)
    print(f'Average={average2:.2f}')
    max_value2 = result_df[column2].max()
    print(f'Maximum={max_value2}')

    output_file_path = f"{process_name}-sysmon-process.csv"

    result_df.to_csv(output_file_path, index=False)

# Example usage
if len(sys.argv) < 2:
    print("Usage: python script.py <process_name> ")
    sys.exit(1)

filter_rows_and_select_columns(process_name, column1, column2)
