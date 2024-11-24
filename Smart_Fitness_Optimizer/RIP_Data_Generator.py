# RIP Data Generator: This script generates simulated Respiratory Inductive Plethysmography (RIP) data and saves it in a C++ array format.
import numpy as np

# Constants
RIP_SAMPLING_RATE = 500  # Hz
RIP_DATA_POINTS = 5000
FREQUENCY = 0.37  # Frequency of the respiratory signal (in Hz, typical for respiration rate) Corresponds to 18 Breaths per minute
AMPLITUDE = 1000  # Amplitude of the RIP signal (in arbitrary units)

# Generate simulated time values (in seconds)
time = np.arange(0, RIP_DATA_POINTS) / RIP_SAMPLING_RATE

# Generate a sine wave to simulate the respiratory pattern (RIP signal)
rip_signal = AMPLITUDE * np.sin(2 * np.pi * FREQUENCY * time)

# Round the data to two decimal places (optional)
simulated_rip_data = np.round(rip_signal, 2)

# Prepare the C++ array format
cpp_file = "rip_data.cpp"
cpp_content = f"""
// Auto-generated C++ file containing simulated RIP data (Sampling rate: {RIP_SAMPLING_RATE} Hz)

const float RIP_Data[] = {{
    {', '.join(map(str, simulated_rip_data))}  // Simulated RIP data (arbitrary units, 2 decimal precision)
}};

const int RIP_Data_Length = {RIP_DATA_POINTS};
"""

# Write the C++ data to a file
try:
    with open(cpp_file, "w") as cpp_output_file:
        cpp_output_file.write(cpp_content)
    print(f"Successfully generated C++ file: {cpp_file}")
except Exception as e:
    print(f"Error while writing C++ file: {e}")
