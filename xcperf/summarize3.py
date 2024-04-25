import pandas as pd
import sys

process_name = sys.argv[1]
column0 = 'GPU Hardware Utilization'
file_name = process_name+"-MetalSystemTrace-core-animation-fps-estimate.csv"

# Function to read CSV file, filter rows, and then select columns
def filter_rows_and_select_columns(process_name, column0):
    file_path = f"{file_name}"

    df = pd.read_csv(file_path, usecols=[column0])

    result_df = df.iloc[:-1]
    # print(result_df)

    result_df.loc[:, column0] = result_df.loc[:, column0].str.replace('%', '').astype(float)

    average1 = result_df[column0].mean(skipna=True)
    print(f'% GPU Average={average1:.2f}')
    max_value1 = result_df[column0].max()
    print(f'% GPU Maximum={max_value1}')

    print(f'{average1:.2f},{max_value1}')

    output_file_path = f"summary-{file_name}"

    result_df.to_csv(output_file_path, index=False)

# Example usage
if len(sys.argv) < 2:
    print("Usage: python summarize3.py <process_name> ")
    sys.exit(1)

filter_rows_and_select_columns(process_name, column0)
