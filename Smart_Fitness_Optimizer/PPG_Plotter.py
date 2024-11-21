import pandas as pd
import matplotlib.pyplot as plt

# File path
csv_file = "s2_run.csv"

# Read the CSV file
try:
    data = pd.read_csv(csv_file)
    if "pleth_1" not in data.columns:
        raise KeyError("Column 'pleth_1' not found in the CSV file.")
except Exception as e:
    print(f"Error: {e}")
    exit()

# Extract the 'pleth_1' column, dropping NaN values
pleth_values = data["pleth_1"].dropna()

# Select the last 1000 values
last_1000_values = pleth_values[-1000:]

# Plot the last 1000 values
plt.figure(figsize=(10, 6))
plt.plot(last_1000_values, label="Plethysmograph Data (Last 1000)", color='blue', linewidth=1)

# Customize the plot
plt.title("Plethysmograph Data (pleth_1) - Last 1000 Values")
plt.xlabel("Sample Index (Last 1000)")
plt.ylabel("Pleth Value")
plt.legend()
plt.grid(True)

# Show the plot
plt.tight_layout()
plt.show()
