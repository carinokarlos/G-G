import streamlit as st
import pandas as pd
import sqlite3
import time
import random
import base64
import os
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
from gtts import gTTS
from io import BytesIO

# ==========================================
# 1. THEME & STYLING
# ==========================================
st.set_page_config(page_title="CornerMan AI Pro", page_icon="🥊", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    
    .main { background-color: #0e1117; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        height: 60px;
        white-space: pre-wrap;
        background-color: #262730;
        border-radius: 10px 10px 0px 0px;
        gap: 10px;
        padding-top: 10px;
    }
    .stTabs [aria-selected="true"] { background-color: #ff4b4b; }
    
    .timer-display {
        font-family: 'Orbitron', sans-serif;
        font-size: 120px;
        font-weight: bold;
        text-align: center;
        color: #ff4b4b;
        text-shadow: 0 0 20px rgba(255, 75, 75, 0.5);
    }
    
    .combo-text {
        font-family: 'Orbitron', sans-serif;
        font-size: 45px;
        text-align: center;
        color: #ffffff;
        background: #1e1e1e;
        padding: 20px;
        border-radius: 15px;
        border-left: 10px solid #ff4b4b;
    }
    
    .metric-card {
        background: #1e1e1e;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #333;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DATABASE & DATA MODELS
# ==========================================
class CornerManDB:
    def __init__(self, db_name='boxing_pro_2026.db'):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.init_db()

    def init_db(self):
        cursor = self.conn.cursor()
        # Training Logs
        cursor.execute('''CREATE TABLE IF NOT EXISTS training 
                        (id INTEGER PRIMARY KEY, date TEXT, type TEXT, rounds INTEGER, 
                         punches INTEGER, intensity REAL, stance TEXT)''')
        # Weight Tracking
        cursor.execute('''CREATE TABLE IF NOT EXISTS weights 
                        (id INTEGER PRIMARY KEY, date TEXT, weight REAL)''')
        # Sparring Film Analysis
        cursor.execute('''CREATE TABLE IF NOT EXISTS film_notes 
                        (id INTEGER PRIMARY KEY, date TEXT, video_name TEXT, 
                         timestamp TEXT, observation TEXT, tag TEXT)''')
        # Camp Configuration
        cursor.execute('''CREATE TABLE IF NOT EXISTS camp 
                        (id INTEGER PRIMARY KEY, fight_date TEXT, weight_goal REAL)''')
        self.conn.commit()

db = CornerManDB()

# ==========================================
# 3. CORE UTILITIES
# ==========================================
def get_audio_html(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        return f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}"></audio>'

def play_sound(file):
    try: st.markdown(get_audio_html(file), unsafe_allow_html=True)
    except: pass

def coach_voice(text):
    tts = gTTS(text=text, lang='en', tld='ie') # Irish coach accent
    tts.save("voice.mp3")
    st.markdown(get_audio_html("voice.mp3"), unsafe_allow_html=True)

# ==========================================
# 4. DASHBOARD LOGIC
# ==========================================
def show_dashboard():
    st.title("🏆 Fighter Dashboard")
    
    # Session Metrics
    df = pd.read_sql_query("SELECT * FROM training", db.conn)
    col1, col2, col3, col4 = st.columns(4)
    
    if not df.empty:
        with col1: st.metric("Sessions", len(df))
        with col2: st.metric("Total Rounds", int(df['rounds'].sum()))
        with col3: st.metric("Avg Intensity", f"{df['intensity'].mean():.1f}")
        with col4: 
            latest_score = df['intensity'].iloc[-1]
            prev_score = df['intensity'].iloc[-2] if len(df) > 1 else latest_score
            st.metric("Last Workout", f"{latest_score:.0f}", delta=f"{latest_score-prev_score:.0f}")
        
        # Plotly chart for Intensity
        fig = px.area(df, x='date', y='intensity', title="Performance Growth (Intensity Score)")
        fig.update_traces(line_color='#ff4b4b')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No training data logged. Start your first round!")

# ==========================================
# 5. ROUND TIMER (CHAMPIONSHIP)
# ==========================================
def show_timer():
    st.title("🕒 Pro Boxing Clock")
    
    with st.sidebar:
        st.header("Timer Settings")
        r_type = st.selectbox("Round Type", ["Classic", "Amateur", "Heavy Bag", "Custom"])
        r_len = st.slider("Round (Min)", 1, 12, 3) if r_type == "Custom" else (2 if r_type == "Amateur" else 3)
        rest_len = st.slider("Rest (Sec)", 30, 90, 60)
        rounds_to_go = st.number_input("Number of Rounds", 1, 15, 6)
        stance = st.radio("Stance", ["Orthodox", "Southpaw"])
    
    # Main Timer Interface
    timer_container = st.container()
    
    if st.button("🔔 START WORKOUT", type="primary", use_container_width=True):
        for r in range(1, rounds_to_go + 1):
            # Work Phase
            play_sound("bell.mp3")
            work_time = r_len * 60
            while work_time > 0:
                mins, secs = divmod(work_time, 60)
                timer_container.markdown(f"<div class='timer-display'>{mins:02d}:{secs:02d}</div>", unsafe_allow_html=True)
                timer_container.markdown(f"<h3 style='text-align:center;'>ROUND {r}</h3>", unsafe_allow_html=True)
                
                if work_time == 30: 
                    coach_voice("Final flurry! 30 seconds!")
                
                time.sleep(1)
                work_time -= 1
            
            # Rest Phase
            play_sound("bell.mp3")
            if r < rounds_to_go:
                rest_time = rest_len
                while rest_time > 0:
                    timer_container.markdown(f"<div class='timer-display' style='color: #00cc66;'>{rest_time:02d}</div>", unsafe_allow_html=True)
                    timer_container.markdown(f"<h3 style='text-align:center;'>RESTING...</h3>", unsafe_allow_html=True)
                    time.sleep(1)
                    rest_time -= 1
        
        st.balloons()
        coach_voice("Workout complete. Log your rounds.")

# ==========================================
# 6. VIDEO ROOM (FILM ANALYSIS)
# ==========================================
def show_video_room():
    st.title("🎥 Video Analysis Room")
    st.write("Upload sparring footage to analyze habits and time-stamp errors.")
    
    uploaded_file = st.file_uploader("Upload Sparring MP4", type=["mp4", "mov"])
    
    if uploaded_file:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.video(uploaded_file)
            st.caption("Tip: Use the playback speed in the player settings for slow-motion.")

        with col2:
            st.subheader("Add Analysis Note")
            with st.form("film_form"):
                timestamp = st.text_input("Timestamp (e.g. 02:45)")
                tag = st.selectbox("Category", ["Defense", "Footwork", "Mistake", "Good Move", "Opponent Habit"])
                obs = st.text_area("Observation")
                
                if st.form_submit_button("Save Entry"):
                    c = db.conn.cursor()
                    c.execute("INSERT INTO film_notes (date, video_name, timestamp, observation, tag) VALUES (?,?,?,?,?)",
                              (date.today().strftime("%Y-%m-%d"), uploaded_file.name, timestamp, obs, tag))
                    db.conn.commit()
                    st.success("Analysis saved to database.")

        # Display history for THIS video
        st.divider()
        st.subheader("Analysis Log")
        notes_df = pd.read_sql_query(f"SELECT * FROM film_notes WHERE video_name='{uploaded_file.name}'", db.conn)
        if not notes_df.empty:
            st.dataframe(notes_df[['timestamp', 'tag', 'observation']], use_container_width=True)

# ==========================================
# 7. REACTION COACH
# ==========================================
def show_coach():
    st.title("⚡ Reaction Coach")
    col_l, col_r = st.columns([1, 2])
    
    with col_l:
        st.write("Voice Command Engine")
        intensity = st.select_slider("Workout Intensity", options=["Low", "Medium", "High", "Pro"])
        delay = {"Low": 6, "Medium": 4, "High": 3, "Pro": 2}[intensity]
        
        active = st.toggle("Activate Coach")
    
    with col_r:
        display = st.empty()
        
        ortho_combos = ["1-2-3", "Jab-Cross-Hook", "Slip-Slip-Upper", "Body-Body-Head", "Double Jab-2"]
        south_combos = ["1-2-3", "Jab-Left Cross-Hook", "Roll-Roll-Left", "Body-Body-Head", "Double Jab-Left"]
        
        if active:
            while active:
                current = random.choice(ortho_combos)
                display.markdown(f"<div class='combo-text'>{current}</div>", unsafe_allow_html=True)
                coach_voice(current)
                time.sleep(delay)

# ==========================================
# 8. WEIGHT & CAMP
# ==========================================
def show_camp():
    st.title("⚖️ Fight Camp Tracker")
    
    col1, col2 = st.columns(2)
    with col1:
        with st.form("weight_form"):
            w = st.number_input("Today's Weight", format="%.2f")
            if st.form_submit_button("Log Weight"):
                c = db.conn.cursor()
                c.execute("INSERT INTO weights (date, weight) VALUES (?,?)", (date.today().strftime("%Y-%m-%d"), w))
                db.conn.commit()
                st.success("Weight recorded.")

    with col2:
        df_w = pd.read_sql_query("SELECT * FROM weights", db.conn)
        if not df_w.empty:
            fig = px.line(df_w, x='date', y='weight', title="Weight Cut Progress")
            st.plotly_chart(fig, use_container_width=True)

# ==========================================
# 9. MAIN EXECUTION
# ==========================================
def main():
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3232/3232704.png", width=100)
    st.sidebar.title("CornerMan AI")
    
    page = st.sidebar.radio("Navigate", ["Dashboard", "Training Timer", "Reaction Coach", "Video Analysis", "Fight Camp"])
    
    if page == "Dashboard": show_dashboard()
    elif page == "Training Timer": show_timer()
    elif page == "Reaction Coach": show_coach()
    elif page == "Video Analysis": show_video_room()
    elif page == "Fight Camp": show_camp()
    
    # Persistent Sidebar Log
    st.sidebar.divider()
    st.sidebar.subheader("Quick Log Session")
    with st.sidebar.form("quick_log"):
        l_rounds = st.number_input("Rounds", 1, 15, 3)
        l_punches = st.number_input("Punches Thrown", 0, 5000, 300)
        l_rpe = st.slider("Exertion (1-10)", 1, 10, 5)
        
        if st.form_submit_button("Save History"):
            # Intensity Formula: (Punches * RPE) / Rounds
            intensity = (l_punches * l_rpe) / l_rounds
            c = db.conn.cursor()
            c.execute("INSERT INTO training (date, type, rounds, punches, intensity) VALUES (?,?,?,?,?)",
                      (date.today().strftime("%Y-%m-%d"), "Workout", l_rounds, l_punches, intensity))
            db.conn.commit()
            st.sidebar.success("Logged!")

if __name__ == "__main__":
    main()