# 🏎️ RaceVision

<div align="center">

### Formula 1 Analytics & Race Visualization Platform

Transforming Formula 1 telemetry into meaningful insights through interactive race visualization, driver analytics, tyre strategy analysis, and pit-stop intelligence.

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)
![FastF1](https://img.shields.io/badge/FastF1-Telemetry-red?style=for-the-badge)
![Arcade](https://img.shields.io/badge/Arcade-GUI-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)

</div>

---

# 📖 Overview

RaceVision is an interactive Formula 1 analytics platform built using Python and FastF1 telemetry data.

The project enables users to replay races, analyze driver performance, compare race strategies, and explore telemetry data through an intuitive graphical interface.

The long-term goal of RaceVision is to evolve into an AI-powered Formula 1 strategy assistant capable of explaining race events, comparing drivers, and generating intelligent race insights.

---

# ✨ Current Features

## 🏁 Race Replay
- Interactive Formula 1 race replay
- Real-time driver positions
- Live leaderboard
- Race progress visualization
- Safety Car visualization
- Adjustable playback speed

## 📊 Telemetry Analysis
- FastF1 telemetry integration
- Driver telemetry visualization
- Speed and lap-time analysis
- Gear and DRS information
- Lap-by-lap telemetry tracking

## 🏎️ Driver Analytics
- Individual driver analysis
- Driver-to-driver comparison
- Lap performance comparison
- Position tracking
- Race performance insights

## 🛞 Tyre Strategy & Degradation
- Tyre compound analysis
- Stint detection and visualization
- Tyre strategy comparison
- Tyre degradation modeling
- Bayesian tyre degradation model

## 🛠️ Pit Stop Analytics
- Automatic pit-stop detection
- Tyre change detection
- Pit-stop confidence classification
- Pre-stop, out-lap, and post-stop pace analysis
- Pace recovery analysis
- Explainable pit-stop effectiveness scoring
- Race-wide strategy comparison

## 🖥️ Interactive Analytics Dashboard
- PySide6 analytics windows
- Interactive driver selection
- Race strategy summaries
- Pit-stop performance tables
- Strategy comparison tables
---

# 🚀 Upcoming Features

- 🤖 AI Race Engineer
- 🧠 AI-generated Race Explanations
- 📈 Driver Performance Index
- 📊 Race Momentum Analysis
- 🏆 Championship Analytics
- 📄 Exportable Race Reports
- 🔮 Predictive Race Strategy
- 🌦️ Advanced Weather-Race Correlation
- 🏎️ Multi-Race Comparison

---

# 🛠 Tech Stack

### Language
- Python

### Data
- FastF1
- Pandas
- NumPy

### Visualization
- Arcade
- Matplotlib

### Desktop Application
- PySide6
- Arcade

### Testing & Development
- Pytest
- GitHub Actions

### AI (Planned)
- Google Gemini API
---




# 📂 Project Structure

```text
RaceVision/
│
├── src/
|   ├── cli/
│   ├── gui/
│   ├── insights/
|   ├── interfaces/
│   ├── bayesian/
│   └── telemetry/
│
├── resources/
├── images/
├── docs/
├── tests/
│
├── main.py
├── requirements.txt
├── requirements-dev.txt
├── pytest.ini
└── README.md


# ⚙️ Installation

Clone the repository

```bash
git clone https://github.com/Sanskar-2305/RaceVision.git
```

Move into the project

```bash
cd RaceVision
```

Create a virtual environment

```bash
python -m venv .venv
```

### Windows

```bash
.\.venv\Scripts\activate
```

### macOS / Linux

```bash
source .venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the application

```bash
python main.py
```

---

# 📸 Screenshots

## 🏁 Race Replay

Interactive race replay with live driver positions, leaderboard, weather information, lap tracking, and playback controls.

![Race Replay](<images/Screenshot 2026-08-18 220118.png>)

---

## 📡 Driver Telemetry

Live telemetry visualization including speed, gear, throttle, and braking data.

![Driver Telemetry](<images/Screenshot 2026-08-18 220232.png>)

---

## 🏎️ Driver Comparison

Compare lap performance and tyre usage between two drivers.

![Driver Comparison](<images/Screenshot 2026-08-18 220355.png>)

---

## 🛞 Tyre Strategy

Visualize tyre compounds and stint progression across the race.

![Tyre Strategy](<images/Screenshot 2026-08-18 220414.png>)

---

## 🛠️ Pit Stop Analysis

Analyze race strategy, pit stops, tyre stints, pit-stop performance, effectiveness scores, and race-wide strategy comparison.

![Pit Stop Analysis](<images/Screenshot 2026-08-18 220600.png>)

---

## 📈 Lap Time & Gap Evolution

Explore lap-time evolution across drivers and identify the impact of race conditions such as VSC periods and pit stops.

![Lap Time & Gap Evolution](<images/Screenshot 2026-08-18 220653.png>)

## 🏁 Race Replay


- Dashboard
- Race Replay
- Driver Analytics
- Telemetry Panel

---


# 🎯 Roadmap

### ✅ Completed

- Interactive race replay
- Driver telemetry
- Driver comparison
- Tyre strategy analysis
- Tyre degradation modeling
- Pit-stop detection
- Pit-stop performance analysis
- Pit-stop effectiveness scoring
- Race-wide strategy comparison
- Automated testing and CI

### 🔄 Planned

- AI Race Engineer
- AI-generated race explanations
- Predictive race strategy
- Championship analytics
- Multi-race comparison
- Exportable race reports
- Advanced weather correlation

---

# 💡 Motivation

RaceVision was created to combine Formula 1 data visualization with modern analytics and artificial intelligence.

The objective is to make complex telemetry data easier to understand for Formula 1 fans, developers, and aspiring data scientists.

---

# 📚 Learning Outcomes

This project demonstrates knowledge of:

- Python
- Data Processing
- FastF1 Telemetry
- Data Visualization
- Object-Oriented Programming
- Software Design
- AI Integration

---

# 📈 Future Scope

- AI Strategy Recommendations
- Team Performance Dashboard
- Driver Similarity Analysis
- Interactive Telemetry Explorer
- Multi-Race Comparison
- Predictive Models
- Cloud Deployment

---

# 👨‍💻 Developer

**Sanskar Mirajkar**

B.Tech Data Science Student

Aspiring AI Engineer

---

## 🔗 Connect With Me

GitHub:
https://github.com/Sanskar-2305

LinkedIn:
https://www.linkedin.com/in/sanskarmirajkar/

Email:
sanskarmirajkar2205@gmail.com

---

## ⭐ Support

If you found this project interesting, consider giving it a ⭐ on GitHub.

It helps support future development of RaceVision.

---

## 📜 License

This project is licensed under the MIT License.
