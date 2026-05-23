# 🌫️ Pune AQI Dashboard

An interactive Dash dashboard for analyzing Pune's Air Quality Index (AQI), pollution levels, and health risk trends across 20 wards from 2022–2024.

## 📊 Features

- 5 KPI Cards (AQI, PM2.5, Health Risk, Unhealthy Days, Hospital Admissions)
- Monthly AQI Trend Analysis
- AQI Category Distribution
- Ward-wise AQI Ranking
- Seasonal Pollutant Comparison
- Ward × Season AQI Heatmap
- PM2.5 vs Hospital Admissions Analysis
- Health Risk Leaderboard Table
- Interactive Filters & AQI Threshold Slider

## 📂 Dataset

**Pune_AQI_Dataset.xlsx**

Contains:
- Daily AQI Records
- PM2.5, NO2, CO Levels
- Health Risk Scores
- Hospital Admissions
- Ward, Zone & Season Information

##  Tech Stack

- Python
- Dash
- Plotly
- Pandas
- NumPy
- Dash Bootstrap Components

##  Installation

```bash
git clone <your-repository-url>
cd pune-aqi-dashboard

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt
```

##  Run Application

```bash
python pune_aqi_dashboard.py
```

Open:

```text
http://localhost:8050
```

## Project Structure

```text
pune-aqi-dashboard/
│
├── pune_aqi_dashboard.py
├── Pune_AQI_Dataset.xlsx
├── requirements.txt
└── README.md
```

##  Dashboard Insights

- Identify high pollution wards
- Compare seasonal pollution patterns
- Track AQI trends over time
- Analyze pollution impact on public health
- Monitor ward-level health risk scores

Savitribai Phule Pune University

📧 patil.sarthak0610@gmail.com
