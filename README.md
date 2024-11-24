# Advanced Wearable System for Fitness and Health Monitoring

## Introduction
This project involves designing and implementing a sophisticated wearable system tailored for fitness and health monitoring. The system captures two types of raw data, along with personal details, processes this data both on the node and in the cloud, and visualizes it dynamically using a Grafana dashboard.

### Purpose
To create a wearable solution that integrates and processes data effectively, combining sensor-based measurements with user-specific parameters for real-time monitoring and actionable insights.


## Sensor Data: PPG and RIP

### What is PPG?
Photoplethysmography (PPG) is a non-invasive optical technique that measures changes in blood volume in tissues using light absorption. It's commonly used to track heart rate and oxygen saturation. The **green wavelength PPG** (used in this project) is ideal for wearables like watches because it offers high accuracy in detecting blood flow beneath the skin.

#### PPG Data Source
The PPG data was sourced from the [PhysioNet Pulse Transit Time PPG dataset](https://physionet.org/content/pulse-transit-time-ppg/1.1.0/csv/#files-panel). Specifically, the **`s2_run.csv` file** was used, with the **`pleth_3` column** representing green wavelength PPG. This data includes natural noise, simulating real-world conditions.

---

### What is RIP?
Respiratory Inductive Plethysmography (RIP) measures respiratory patterns by detecting changes in thoracic or abdominal circumference during breathing. It works by using elastic bands embedded with conductive loops that detect variations in inductance as the body expands and contracts. These changes are converted into electrical signals, processed to extract respiratory rate, depth, and patterns. RIP provides precise respiratory data and can be integrated into sportswear (e.g., sports bras, T-shirts) for athletes, offering a non-invasive, real-time solution for monitoring breathing efficiency and performance during physical activity.

#### RIP Data Generation
The RIP data was synthetically generated using a Python script that simulates a wave corresponding to a typical breathing rate during running (22 breaths per minute). Unlike the PPG data, RIP data in this project is noise-free to demonstrate its reliability in sports wearables.

---

## Data Transmission to the Cloud

The raw PPG and RIP data, alongside user details (age, height, weight, activity status), are transmitted to an **InfluxDB** instance using the ESP32. Data transfer is optimized using the following settings:

```cpp
client.setWriteOptions(WriteOptions()
    .writePrecision(WritePrecision::MS)
    .batchSize(500)
    .bufferSize(1000)
    .flushInterval(100));
```
This ensures efficient and precise data storage in the cloud.


## Cloud-Based Data Analysis

A Python script is used to calculate various metrics. This script runs on the PC, retrieves data from InfluxDB using Flux queries, processes the data to calculate metrics, and then writes the results back to InfluxDB.

### Heart Rate (HR) and Respiratory Rate (RR) Calculations
- **Bandpass Filter:** To process the raw PPG and RIP data, a bandpass filter is applied. This helps to remove noise and eliminate the DC component, isolating the relevant frequency components.
- **Heart Rate (HR):** The heart rate is calculated by detecting the dominant frequency in the PPG data and converting it into beats per minute (bpm). This provides a real-time measure of cardiovascular performance.
- **Respiratory Rate (RR):** The respiratory rate is derived from the RIP data, with breaths per minute (Br/min) being calculated from the signal's periodic nature.

### Exercise Intensity
Exercise intensity is determined using the **Karvonen formula**, which relates heart rate to exercise effort:
```python
intensity = ((hr - resting_hr) / (max_hr - resting_hr)) * 100
```
The calculated intensity value provides a meaningful measure of the user’s effort during physical activity. It is dynamically updated based on real-time heart rate data and can be used to monitor workout intensity for optimizing fitness goals.

### Statistical Metrics
To enhance the analysis, the system computes statistical metrics for both Heart Rate (HR) and Respiratory Rate (RR):

- **Average HR and RR:** These are the mean values of heart rate and respiratory rate calculated over a rolling window. They provide an overview of the user's physiological trends during activity.
- **Standard Deviation (Stdev) of HR and RR:** This metric reflects the variability or consistency of the heart and respiratory rates, indicating how stable the physiological responses are under different activity levels.

These statistical insights are stored in InfluxDB for further visualization and to offer a comprehensive view of user performance.


## Data Visualization with Grafana

To make the data accessible and actionable, a Grafana dashboard was designed. This dashboard retrieves real-time and historical data from the InfluxDB bucket using Flux queries. The key features of the dashboard include:

1. **Personal Information Panel:**
   - Displays user details such as age, height, weight, and activity status.

2. **PPG and RIP Signal Graphs:**
   - Visualizes raw PPG and RIP data over time, allowing users to monitor signal quality.

3. **Real-Time Metrics:**
   - Shows current Heart Rate (HR) and Respiratory Rate (RR).

4. **Statistical Overview:**
   - Displays the average and standard deviation of HR and RR, offering insights into physiological stability.

5. **Exercise Intensity and Max HR:**
   - Tracks exercise intensity as a percentage and provides the calculated maximum heart rate (Max HR) based on the user’s age.

This dashboard is fully interactive and dynamically updates, providing an intuitive interface for users to monitor their performance and physiological responses.


## Conclusion

This project demonstrates a robust implementation of a wearable health monitoring system, integrating real-time data collection, cloud-based analysis, and dynamic visualization. By combining PPG and RIP data, this system highlights the potential of advanced physiological monitoring for fitness and healthcare applications. With its detailed insights and scalability, the project serves as a valuable platform for future innovations in wearable technology.