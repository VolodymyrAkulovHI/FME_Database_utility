import pandas as pd
import numpy as np

# Generate sample data
num_records = 1000
data = {
    'ROADNAME': np.random.choice(['Road A', 'Road B', 'Road C'], num_records),
    'MeasureFromKM': np.random.randint(0, 100, num_records),
    'MeasureToKM': np.random.randint(1, 101, num_records)
}
df = pd.DataFrame(data)
df['MeasureToKM'] = df[['MeasureFromKM', 'MeasureToKM']].max(axis=1)

# Randomly select a subset of ids for testing
id_columns = ['ROADNAME', 'MeasureFromKM', 'MeasureToKM']
ids = [tuple(x) for x in df[id_columns].sample(100).values]

# Method 1: Original Optimized Method
def extract_records_original(df, ids):
    records = []
    for id_tuple in ids:
        condition = (
            (df[id_columns[0]] == id_tuple[0]) & 
            (df[id_columns[1]] == id_tuple[1]) & 
            (df[id_columns[2]] == id_tuple[2])
        )
        records.extend(df[condition].to_dict('records'))
    return records

# Method 2: MultiIndex Method
def extract_records(df, ids, id_columns):
    ids = set(ids)
    df_indexed = df.set_index(id_columns)
    mask = df_indexed.index.isin(ids)
    return df_indexed[mask].reset_index().to_dict('records')

# Extract records using both methods
result_original = extract_records_original(df, ids)
result_multiindex = extract_records(df, ids, id_columns)

# Sort results for accurate comparison
result_original_sorted = sorted(result_original, key=lambda x: (x['ROADNAME'], x['MeasureFromKM'], x['MeasureToKM']))
result_multiindex_sorted = sorted(result_multiindex, key=lambda x: (x['ROADNAME'], x['MeasureFromKM'], x['MeasureToKM']))

# Convert to DataFrames for a more robust comparison
df_original = pd.DataFrame(result_original_sorted)
df_multiindex = pd.DataFrame(result_multiindex_sorted)

# Check lengths first
print(f"Length of original method result: {len(result_original_sorted)}")
print(f"Length of multiindex method result: {len(result_multiindex_sorted)}")

# Align DataFrames for comparison
df_original_aligned, df_multiindex_aligned = df_original.align(df_multiindex, join='outer', axis=0)

# Check if DataFrames are equal
if df_original_aligned.equals(df_multiindex_aligned):
    print("Both methods produce the same result.")
else:
    print("The results are not the same")
    
    # Detailed row-by-row comparison
    comparison = df_original_aligned.compare(df_multiindex_aligned)
    print("\nDetailed comparison of differences:")
    print(comparison)

    # Check for any missing rows in each DataFrame
    missing_in_original = df_multiindex_aligned[~df_multiindex_aligned.apply(tuple, 1).isin(df_original_aligned.apply(tuple, 1))]
    missing_in_multiindex = df_original_aligned[~df_original_aligned.apply(tuple, 1).isin(df_multiindex_aligned.apply(tuple, 1))]
    
    if not missing_in_original.empty:
        print("\nRows in multiindex method result but not in original method result:")
        print(missing_in_original)
        
    if not missing_in_multiindex.empty:
        print("\nRows in original method result but not in multiindex method result:")
        print(missing_in_multiindex)
