import numpy as np

# Constants
PPG_SAMPLING_RATE = 500  # Hz
PPG_DATA_POINTS = 5000
FREQUENCY = 2.5  # Frequency of the heart rate signal in Hz (about 150 BPM for running)
AMPLITUDE = 1000  # Amplitude of the PPG signal (in arbitrary units)

# Generate simulated time values (in seconds)
time = np.arange(0, PPG_DATA_POINTS) / PPG_SAMPLING_RATE

# Generate a sine wave to simulate the PPG pattern
ppg_signal = AMPLITUDE * np.sin(2 * np.pi * FREQUENCY * time)

# Round the data to two decimal places (optional)
simulated_ppg_data = np.round(ppg_signal, 2)

# Prepare the C++ array format
cpp_file = "ppg_data.cpp"
cpp_content = f"""
// Auto-generated C++ file containing simulated PPG data (Sampling rate: {PPG_SAMPLING_RATE} Hz)

const float PPG_Data[] = {{
    {', '.join(map(str, simulated_ppg_data))}  // Simulated PPG data (arbitrary units, 2 decimal precision)
}};

const int PPG_Data_Length = {PPG_DATA_POINTS};
"""

# Write the C++ data to a file
try:
    with open(cpp_file, "w") as cpp_output_file:
        cpp_output_file.write(cpp_content)
    print(f"Successfully generated C++ file: {cpp_file}")
except Exception as e:
    print(f"Error while writing C++ file: {e}")
