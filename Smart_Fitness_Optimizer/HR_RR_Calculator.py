import time
import numpy as np
from influxdb_client import InfluxDBClient, Point, WritePrecision, WriteOptions
from datetime import datetime

# InfluxDB configuration (updated with provided credentials)
INFLUXDB_URL = "http://192.168.0.158:8080"
INFLUXDB_TOKEN = "JzaBbK_HXy5RaTBWFE7fF7NpnCvGYfMQFYfP_Guw8H-yhSyWlfecZfiqyfXjJIWRd8HaBFyM7S_Z76LiRYBQzw=="
INFLUXDB_ORG = "cf38919dce75ecce"
INFLUXDB_BUCKET = "FitnessOptimizer"

# High-pass filter (theoretical) - Difference of consecutive data points
def bandpass_filter(data, low_cutoff_freq, high_cutoff_freq, sampling_rate):
    """
    Apply a bandpass filter to the data using the specified cutoff frequencies.
    
    Args:
        data: The input signal data
        low_cutoff_freq: The low cutoff frequency for the bandpass filter
        high_cutoff_freq: The high cutoff frequency for the bandpass filter
        sampling_rate: The sampling rate of the input signal in Hz
    
    Returns:
        The filtered signal data
    """
    # convert to freq spectrum
    fft_result = np.fft.fft(data)
    freqs = np.fft.fftfreq(len(data), 1 / sampling_rate)

    # Apply bandpass filter
    fft_result[(freqs < low_cutoff_freq)] = 0
    fft_result[(freqs > high_cutoff_freq)] = 0

    # Convert back to time domain
    filtered_data = np.fft.ifft(fft_result)

    return np.real(filtered_data)


# Update the heart rate calculation to apply high-pass filter before FFT
def calculate_heart_rate_fft(ppg_data, sampling_rate):
    """
    Calculate heart rate by detecting the peak frequency in the PPG signal using FFT.
    
    Args:
        ppg_data: The PPG signal data
        sampling_rate: The sampling rate of the PPG data in Hz
    
    Returns:
        The heart rate in beats per minute (bpm)
    """
    # Remove DC component from the PPG signal
    ppg_data = remove_dc_component(ppg_data)
    
    # Apply high-pass filter to remove frequencies below 40 BPM (0.6667 Hz) and above 200 BPM (3.3333 Hz)
    ppg_data = bandpass_filter(ppg_data, 0.6667, 3.3333, sampling_rate)
    
    # Apply FFT to the filtered signal
    fft_result = np.fft.fft(ppg_data)
    freqs = np.fft.fftfreq(len(ppg_data), 1 / sampling_rate)
    
    # Get the absolute value of the FFT and find the peak frequency
    fft_magnitude = np.abs(fft_result)
    peak_freq = freqs[np.argmax(fft_magnitude[1:]) + 1]  # Skip the zero frequency (DC)
    
    # Convert the peak frequency to beats per minute (bpm)
    hr = abs(peak_freq * 60)  # bpm = Hz * 60
    print(f"Calculated HR (from FFT): {hr} bpm")  # Debug: HR from FFT output
    
    return hr

def calculate_respiratory_rate_fft(rip_data, sampling_rate):
    """
    Calculate respiratory rate by detecting the peak frequency in the RIP signal using FFT.
    Args:
        rip_data: The RIP signal data
        sampling_rate: The sampling rate of the RIP data in Hz
    Returns:
        The respiratory rate in breaths per minute (breaths/min)
    """
    # Remove DC component from the RIP signal
    rip_data = remove_dc_component(rip_data)
    
    # Apply FFT to the signal
    fft_result = np.fft.fft(rip_data)
    freqs = np.fft.fftfreq(len(rip_data), 1 / sampling_rate)
    
    # Get the absolute value of the FFT and find the peak frequency
    fft_magnitude = np.abs(fft_result)
    peak_freq = freqs[np.argmax(fft_magnitude[1:]) + 1]  # Skip the zero frequency (DC)
    
    # Convert the peak frequency to breaths per minute (breaths/min)
    rr = abs(peak_freq * 60)  # breaths/min = Hz * 60
    print(f"Calculated RR (from FFT): {rr} breaths/min")  # Debug: RR from FFT output
    
    return rr

def remove_dc_component(signal):
    """
    Remove the DC component (mean) from the signal.
    Args:
        signal: The raw signal data
    Returns:
        The signal with the DC component removed
    """
    return signal - np.mean(signal)

# Connect to InfluxDB
client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
write_api = client.write_api(write_options=WriteOptions(batch_size=500, flush_interval=100))

# Function to get the latest data from InfluxDB
def get_latest_data():
    query = f"""
    from(bucket: "{INFLUXDB_BUCKET}")
        |> range(start: -1m)
        |> filter(fn: (r) => r["_measurement"] == "PPG" or r["_measurement"] == "RIP")
        |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
    """
    result = client.query_api().query(query)
    
    ppg_data = []
    rip_data = []
    
    for table in result:
        for record in table.records:
            measurement = record["_measurement"]
            if measurement == "PPG":
                ppg_data.append(record["value"])
            elif measurement == "RIP":
                rip_data.append(record["value"])
    
    return np.array(ppg_data), np.array(rip_data)


# Function to write HR to InfluxDB
def write_heart_rate_to_influxdb(hr):
    point = Point("HeartRate") \
        .tag("sensor", "PPG") \
        .field("heart_rate", float(hr)) \
        .time(datetime.utcnow(), WritePrecision.NS)
    
    write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)
    print(f"Written Heart Rate: {hr} bpm")

# Function to write RR to InfluxDB
def write_respiratory_rate_to_influxdb(rr):
    point = Point("RespiratoryRate") \
        .tag("sensor", "RIP") \
        .field("respiratory_rate", float(rr)) \
        .time(datetime.utcnow(), WritePrecision.NS)
    
    write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)
    print(f"Written Respiratory Rate: {rr} breaths/min")


# Main function
def main():
    PPG_SAMPLING_RATE = 500  # PPG sampling rate (Hz)
    RIP_SAMPLING_RATE = 500  # RIP sampling rate (Hz)
    
    while True:
        # Get the latest PPG and RIP data from InfluxDB
        ppg_data, rip_data = get_latest_data()
        
        if len(ppg_data) > 0 and len(rip_data) > 0:
            # Calculate Heart Rate and Respiratory Rate using FFT
            hr = calculate_heart_rate_fft(ppg_data, PPG_SAMPLING_RATE)
            rr = calculate_respiratory_rate_fft(rip_data, RIP_SAMPLING_RATE)

            # Write the calculated HR to InfluxDB
            write_heart_rate_to_influxdb(hr)
            
            # Write the calculated RR to InfluxDB
            write_respiratory_rate_to_influxdb(rr)
        
        # Wait for the next loop (semi-real-time)
        time.sleep(2) # 3 seconds

if __name__ == "__main__":
    main()
