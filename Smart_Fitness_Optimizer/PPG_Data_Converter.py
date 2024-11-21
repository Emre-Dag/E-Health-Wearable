import pandas as pd

# File paths
csv_file = "s2_run.csv"
output_cpp_file = "ppg_data.cpp"

# Constants for 14-bit ADC resolution (ADC range = 16384)
ADC_RANGE_14BIT = 16384  # 14-bit resolution (2^14)
V_REF = 1.8  # Reference voltage in Volts

# Function to convert ADC count to mV and round to two decimal places
def adc_to_mV(adc_count, adc_range):
    return round((adc_count / adc_range) * V_REF * 1000, 2)  # Convert to millivolts and round to 2 decimal places

# Read the CSV file
try:
    data = pd.read_csv(csv_file)
    if "pleth_3" not in data.columns:
        raise KeyError("Column 'pleth_3' not found in the CSV file.")
except Exception as e:
    print(f"Error: {e}")
    exit()

# Extract the first 5000 points of 'pleth_3' data, convert to mV and round to 2 decimal places
pleth_3_values = data["pleth_3"].dropna().astype(int)[:5000]

# Convert ADC counts to mV and round to 2 decimal places for pleth_3
pleth_3_mV_values = [adc_to_mV(count, ADC_RANGE_14BIT) for count in pleth_3_values]

# Generate the C++ array
cpp_content = f"""
// Auto-generated C++ file containing the first 5000 points of PPG data in mV from {csv_file}

const float PPG_Data[] = {{
    {', '.join(map(str, pleth_3_mV_values))}  // Values in millivolts (2 decimal precision)
}};

const int PPG_Data_Length = {len(pleth_3_mV_values)};
"""

# Write the generated content to a C++ file
try:
    with open(output_cpp_file, "w") as cpp_file:
        cpp_file.write(cpp_content)
    print(f"Successfully generated C++ file: {output_cpp_file}")
except Exception as e:
    print(f"Error while writing C++ file: {e}")
