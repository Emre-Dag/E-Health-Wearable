// Smart Fitness Optimizer
#include <Arduino.h>
#include <WiFiMulti.h>
#include <InfluxDBClient.h>
#include <InfluxDbCloud.h>
#include "Preferences.h"
#include "Demo_Data.h"

WiFiMulti wifiMulti;

// Time zone info
#define TZ_INFO "UTC1"
// Prepare InfluxDB data point
Point PPG("PPG");  // PPG Data
Point RIP("RIP");  // Respiratory Inductive Plethysmography Data
Point Person("Person");  // Person Data

// Sample time in microseconds
const unsigned long Sample_TimeUS = 1000000 / 500; // 500 Hz => 2ms per sample

// Declare variables for timekeeping
unsigned long PrevMicros = 0;
int Index = 0; // Holds the current index

// Declare function prototypes
void connectToWiFi();
// InfluxDB client
InfluxDBClient client(INFLUXDB_URL, INFLUXDB_ORG, INFLUXDB_BUCKET, INFLUXDB_TOKEN, InfluxDbCloud2CACert);

void setup() {
  // Initialize Serial
  Serial.begin(115200);

  // Connect to Wi-Fi
  connectToWiFi();

  // Set time sync servers
  timeSync(TZ_INFO, "pool.ntp.org", "time.nis.gov");

  // Check connection
  if (client.validateConnection()) {
    Serial.print("Connected to InfluxDB: ");
    Serial.println(client.getServerUrl());
  } else {
    Serial.print("InfluxDB connection failed: ");
    Serial.println(client.getLastErrorMessage());
  }

  // Set write options
  client.setWriteOptions(WriteOptions().writePrecision(WritePrecision::MS).batchSize(500).bufferSize(1000).flushInterval(100));
  client.setHTTPOptions(HTTPOptions().connectionReuse(true)); // Reuse HTTP connection
}

void loop() {
  // Check Wi-Fi connection and reconnect if necessary
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Wi-Fi disconnected. Reconnecting...");
    connectToWiFi();
  }

  // Check if it's time to take a sample
  if (micros() - PrevMicros >= Sample_TimeUS) {
    PrevMicros = micros();

    float PPGValue = PPG_Data[Index];
    float RIPValue = RIP_Data[Index];

    // Add fields to InfluxDB data
    PPG.clearFields();
    PPG.addField("value", PPGValue);
    PPG.addField("sensor", "PPG");

    RIP.clearFields();
    RIP.addField("value", RIPValue);
    RIP.addField("sensor", "RIP");

    //s2_run	Act:run	G:male	l:175	w:70	Age:20	HRs:114	HRe:118	
    // Person Data
    Person.clearFields();
    Person.addField("Age", 20);
    Person.addField("Gender", "Male");
    Person.addField("Height", 175);
    Person.addField("Weight", 70);
    Person.addField("Activity", "Running");

    Index = (Index + 1) % 5000; // Loop through array

    // Write to InfluxDB
    if (client.writePoint(PPG) && client.writePoint(RIP) && client.writePoint(Person)) {
      Serial.println("Data written to InfluxDB");
    } else {
      Serial.print("Failed to write to InfluxDB: ");
      Serial.println(client.getLastErrorMessage());
    }

    // Check if the loop has completed
    if (Index == 0) {
      Serial.println("Full loop done");
    }
  }
}

void connectToWiFi() {
  WiFi.mode(WIFI_STA);
  wifiMulti.addAP(ssid, password);

  Serial.print("Connecting to Wi-Fi");
  while (wifiMulti.run() != WL_CONNECTED) {
    Serial.print(".");
    delay(500);
  }
  Serial.println();
  Serial.printf("Connected to %s\n", WiFi.SSID().c_str());
}
