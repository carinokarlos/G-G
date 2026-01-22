# Gloves & Graph (G&G)

### Professional Boxing Analytics and Training Intelligence Suite

Gloves & Graph is a data-centric platform designed for combat athletes and coaches. It bridges the gap between physical exertion and quantified performance by transforming traditional training sessions into actionable insights.

Utilizing proprietary intensity metrics, stance-aware audio coaching, and a dedicated film-study suite, G&G ensures that every training interval is optimized for competitive success.

---

## Key Features

### Championship Round Timer

A high-contrast interface designed for maximum visibility in high-intensity gym environments.

* **Final Flurry Logic:** Integrated audio prompts during the final 30 seconds of a round to encourage increased work rate.
* **Regulatory Standards:** Pre-configured intervals for both professional (3-minute) and amateur (2-minute) competition standards.

### Dynamic Reaction Engine

An automated audio-command system designed to enhance cognitive reactivity and eliminate repetitive movement patterns during solo training.

* **Stance-Aware Logic:** Customizable settings for Orthodox and Southpaw stances. The system dynamically adjusts combination callouts to reflect the mechanical advantages of the selected stance.
* **Variable Pacing:** Four distinct intensity levels—Technical, Steady, Intense, and Killer—to align with different phases of a fight camp.

### Video Analysis and Film Study

A specialized suite for technical refinement through structured film review.

* **Granular Playback Control:** Integrated tools for slow-motion analysis of footwork, defensive positioning, and striking mechanics.
* **Relational Annotations:** Technical observations are saved to specific timestamps and stored within a permanent SQLite database for long-term progress tracking.

### Performance Analytics and Reporting

Quantifiable metrics to monitor training load and physiological readiness.

* **Intensity Score:** A proprietary calculation designed to measure training density:


* **Weight Management:** Daily monitoring of weight fluctuations against target competition weight.
* **Executive Reporting:** One-click CSV generation for exporting training blocks to head coaches or nutritionists.

---

## Technical Stack

* **Programming Language:** Python 3.13+
* **Interface:** Streamlit (Mobile-Responsive)
* **Data Management:** SQLite
* **Audio Processing:** Google Text-to-Speech (gTTS)
* **Data Visualization:** Pandas and Plotly Express

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/Gloves-Graph.git
cd Gloves-Graph

```

### 2. Install Dependencies

```bash
pip install streamlit pandas plotly gTTS

```

### 3. Launch the Application

```bash
python -m streamlit run app.py

```

---

## Operational Guide

1. **Timer Module:** Configure round parameters and initiate the session. Utilize "Flurry Mode" for high-intensity conditioning.
2. **Reaction Coach:** Position the device clearly, select the appropriate stance, and execute combinations based on real-time audio cues.
3. **Video Room:** Upload sparring or bag-work footage post-session to document and categorize technical errors.
4. **Analytics Dashboard:** Review the "Intensity Score" and weight trends to ensure training volume is progressing according to the camp schedule.

---

## 2026 Development Roadmap

* **Computer Vision Integration:** Automated strike counting via webcam feed.
* **Biometric Synchronization:** Integration with wearable heart rate data (e.g., Whoop, Apple Watch).
* **Strategic Modeling:** LLM-driven tactical generation based on opponent scouting data.

---

**Gloves & Graph — Built for the Modern Fighter.**
