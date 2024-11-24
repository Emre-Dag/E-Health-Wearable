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
    fft_result = np.fft.fft(data)
    freqs = np.fft.fftfreq(len(data), 1 / sampling_rate)
    fft_result[(freqs < low_cutoff_freq)] = 0
    fft_result[(freqs > high_cutoff_freq)] = 0
    filtered_data = np.fft.ifft(fft_result)
    return np.real(filtered_data)

def calculate_heart_rate_fft(ppg_data, sampling_rate):
    ppg_data = remove_dc_component(ppg_data)
    ppg_data = bandpass_filter(ppg_data, 0.6667, 3.3333, sampling_rate)
    fft_result = np.fft.fft(ppg_data)
    freqs = np.fft.fftfreq(len(ppg_data), 1 / sampling_rate)
    fft_magnitude = np.abs(fft_result)
    peak_freq = freqs[np.argmax(fft_magnitude[1:]) + 1]
    return abs(peak_freq * 60)

def calculate_respiratory_rate_fft(rip_data, sampling_rate):
    rip_data = remove_dc_component(rip_data)
    fft_result = np.fft.fft(rip_data)
    freqs = np.fft.fftfreq(len(rip_data), 1 / sampling_rate)
    fft_magnitude = np.abs(fft_result)
    peak_freq = freqs[np.argmax(fft_magnitude[1:]) + 1]
    return abs(peak_freq * 60)

def remove_dc_component(signal):
    return signal - np.mean(signal)

# Function to calculate exercise intensity based on heart rate: Karvonen method
def calculate_exercise_intensity(hr, resting_hr, max_hr):
    intensity = ((hr - resting_hr) / (max_hr - resting_hr)) * 100 
    return max(0, min(intensity, 100))  # Clamp intensity between 0 and 100%

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

# Function to fetch Age from InfluxDB
def get_user_age():
    query = f"""
    from(bucket: "{INFLUXDB_BUCKET}")
        |> range(start: -1m)
        |> filter(fn: (r) => r["_measurement"] == "Person" and r["_field"] == "Age")
        |> last()
    """
    result = client.query_api().query(query)
    for table in result:
        for record in table.records:
            return int(record["_value"])
    return 20  # Default age if no data is available

# Function to write HR to InfluxDB
def write_heart_rate_to_influxdb(hr):
    print(f"DEBUG: Writing HR to InfluxDB: {hr} bpm")
    point = Point("HeartRate") \
        .tag("sensor", "PPG") \
        .field("heart_rate", float(hr)) \
        .time(datetime.utcnow(), WritePrecision.NS)
    write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)

# Function to write RR to InfluxDB
def write_respiratory_rate_to_influxdb(rr):
    print(f"DEBUG: Writing RR to InfluxDB: {rr} breaths/min")
    point = Point("RespiratoryRate") \
        .tag("sensor", "RIP") \
        .field("respiratory_rate", float(rr)) \
        .time(datetime.utcnow(), WritePrecision.NS)
    write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)

# Function to write Exercise Intensity to InfluxDB
def write_exercise_intensity_to_influxdb(intensity):
    print(f"DEBUG: Writing Exercise Intensity to InfluxDB: {intensity}%")
    point = Point("ExerciseIntensity") \
        .tag("calculation", "dynamic") \
        .field("intensity", float(intensity)) \
        .time(datetime.utcnow(), WritePrecision.NS)
    write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)

# Function to write Average HR and Standard Deviation to InfluxDB
def write_avg_stdev_hr_to_influxdb(avg_hr, stdev_hr):
    print(f"DEBUG: Writing Average HR to InfluxDB: {avg_hr} bpm")
    print(f"DEBUG: Writing Standard Deviation to InfluxDB: {stdev_hr}")
    point = Point("HeartRate") \
        .tag("sensor", "PPG") \
        .field("average_heart_rate", float(avg_hr)) \
        .field("standard_deviation", float(stdev_hr)) \
        .time(datetime.utcnow(), WritePrecision.NS)
    write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)

# Function to write Average RR and Standard Deviation to InfluxDB
def write_avg_stdev_rr_to_influxdb(avg_rr, stdev_rr):
    print(f"DEBUG: Writing Average RR to InfluxDB: {avg_rr} breaths/min")
    print(f"DEBUG: Writing Standard Deviation to InfluxDB: {stdev_rr}")
    point = Point("RespiratoryRate") \
        .tag("sensor", "RIP") \
        .field("average_respiratory_rate", float(avg_rr)) \
        .field("standard_deviation", float(stdev_rr)) \
        .time(datetime.utcnow(), WritePrecision.NS)
    write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)

# Main function
def main():
    PPG_SAMPLING_RATE = 500
    RIP_SAMPLING_RATE = 500
    RESTING_HR = 60.0  # Default resting HR
    
    # HR data array
    hr_data = []
    # RR data array
    rr_data = []
    while True:
        user_age = get_user_age()
        max_hr = 220 - user_age
        ppg_data, rip_data = get_latest_data()
        
        if len(ppg_data) > 0 and len(rip_data) > 0:
            hr = calculate_heart_rate_fft(ppg_data, PPG_SAMPLING_RATE)
            rr = calculate_respiratory_rate_fft(rip_data, RIP_SAMPLING_RATE)
            write_heart_rate_to_influxdb(hr)
            write_respiratory_rate_to_influxdb(rr)
            
            intensity = calculate_exercise_intensity(hr, RESTING_HR, max_hr)
            write_exercise_intensity_to_influxdb(intensity)
            
            # calculate average hr and standard deviation
            if len(hr_data) >= 10:
                avg_hr = np.mean(hr_data)
                stdev_hr = np.std(hr_data)
                #delete oldest one and add newest one
                hr_data.pop(0)
                hr_data.append(hr)
                write_avg_stdev_hr_to_influxdb(avg_hr, stdev_hr)
            else:
                hr_data.append(hr)
            # calculate average rr and standard deviation
            if len(rr_data) >= 10:
                avg_rr = np.mean(rr_data)
                stdev_rr = np.std(rr_data)
                #delete oldest one and add newest one
                rr_data.pop(0)
                rr_data.append(rr)
                write_avg_stdev_rr_to_influxdb(avg_rr, stdev_rr)
            else:
                rr_data.append(rr)
        time.sleep(2)

if __name__ == "__main__":
    main()
