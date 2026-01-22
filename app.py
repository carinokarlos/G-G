import streamlit as st
import pandas as pd
import sqlite3
import time
import random
import base64
import plotly.express as px
from datetime import datetime, date
from gtts import gTTS
from io import BytesIO

# --- 1. SETUP & CSS LOADER ---
st.set_page_config(page_title="G&G Pro", page_icon="🥊", layout="wide")

def load_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"CSS file not found: {file_name}")

load_css("assets/style.css")

# --- 2. DATABASE MANAGER ---
class DatabaseManager:
    def __init__(self, db_name='gloves_graph.db'):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        c = self.conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS training (id INTEGER PRIMARY KEY, date TEXT, type TEXT, rounds INTEGER, punches INTEGER, intensity REAL, stance TEXT)')
        self.conn.commit()

    def log_session(self, rounds, punches, rpe, stance="Orthodox"):
        intensity = (punches * rpe) / rounds if rounds > 0 else 0
        c = self.conn.cursor()
        c.execute("INSERT INTO training (date, type, rounds, punches, intensity, stance) VALUES (?,?,?,?,?,?)",
                  (date.today().strftime("%Y-%m-%d"), "Workout", rounds, punches, intensity, stance))
        self.conn.commit()
        return intensity

    def get_best_score(self):
        df = pd.read_sql_query("SELECT MAX(intensity) as best FROM training", self.conn)
        return df['best'].iloc[0] if not df.empty and df['best'].iloc[0] is not None else 0

db = DatabaseManager()

# --- 3. AUDIO UTILITIES ---
def play_audio_bytes(data):
    b64 = base64.b64encode(data).decode()
    st.markdown(f'<audio autoplay="true" style="display:none;"><source src="data:audio/mp3;base64,{b64}"></audio>', unsafe_allow_html=True)

def speak(text):
    try:
        tts = gTTS(text=text, lang='en', tld='ie')
        fp = BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        play_audio_bytes(fp.read())
    except: pass

def bell():
    try:
        with open("sounds/bell.mp3", "rb") as f: play_audio_bytes(f.read())
    except: pass

# --- 4. NEW FEATURE LOGIC ---
def get_preset(name):
    # Returns (Mins, Rounds)
    presets = {
        "Custom": (3, 6),
        "Pro Fight": (3, 12),
        "Amateur Bout": (2, 3),
        "HIIT / Tabata": (1, 8),
        "Marathon": (4, 4)
    }
    return presets.get(name, (3, 6))

def get_opponent_combos(style, stance):
    # Tailored combos based on opponent style
    basic = ["1-2", "1-2-3", "Double Jab"]
    
    if style == "The Swarmer (Pressure)":
        # Focus on uppercuts, pivots, and check hooks to stop pressure
        return basic + ["Check Hook", "Rear Uppercut-Hook", "Pivot-2", "3-4-3", "Step Back-2"]
    elif style == "The Sniper (Tall/Fast)":
        # Focus on head movement and doubling up to close distance
        return basic + ["Double Jab-Cross", "Slip-Slip-2", "Body-Head-Hook", "Roll-2-3", "Feint-1-2"]
    else: # Balanced
        return basic + ["1-2-Slip-2", "Pull-2", "Jab-Hook-Cross", "1-1-2"]

# --- 5. MODULES (PAGES) ---
def timer_ui():
    st.title("⏱️ Pro Timer")
    
    # NEW: Quick Start Presets
    preset_name = st.selectbox("Training Mode", ["Custom", "Pro Fight", "Amateur Bout", "HIIT / Tabata", "Marathon"])
    default_m, default_r = get_preset(preset_name)
    
    c1, c2 = st.columns(2)
    mins = c1.number_input("Minutes", 1, 10, default_m)
    rounds = c2.number_input("Rounds", 1, 15, default_r)
    
    if st.button("🔔 START SESSION", type="primary", use_container_width=True):
        placeholder = st.empty()
        for r in range(1, rounds + 1):
            bell()
            t = mins * 60
            while t > 0:
                m, s = divmod(t, 60)
                placeholder.markdown(f"""
                <div class="timer-card">
                    <div class="timer-display">{m:02d}:{s:02d}</div>
                    <h3 style="margin-top:10px;">ROUND {r}/{rounds}</h3>
                </div>
                """, unsafe_allow_html=True)
                
                # Audio: 30s Warning
                if t == 30: speak("30 seconds! Pick it up!")
                time.sleep(1)
                t -= 1
            
            bell()
            if r < rounds:
                rest = 60
                while rest > 0:
                    placeholder.markdown(f"""
                    <div class="timer-card" style="border-color:#00cc66;">
                        <div class="timer-display rest-display">{rest}</div>
                        <h3 style="color:#00cc66;">RECOVER</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    time.sleep(1)
                    rest -= 1
        st.balloons()

def coach_ui():
    st.title("⚡ Opponent Sim")
    
    # NEW: Opponent Style Selector
    c1, c2 = st.columns(2)
    stance = c1.radio("Your Stance", ["Orthodox", "Southpaw"])
    style = c2.selectbox("Opponent Style", ["Balanced", "The Swarmer (Pressure)", "The Sniper (Tall/Fast)"])
    
    pace = st.select_slider("Pace", ["Slow", "Fast", "War"])
    delay = {"Slow": 5, "Fast": 3, "War": 2}[pace]
    
    # Get smart combos
    target_combos = get_opponent_combos(style, stance)
    
    if st.button(f"🥊 FIGHT: {style.split(' ')[0]}", type="primary", use_container_width=True):
        ph = st.empty()
        while True:
            c = random.choice(target_combos)
            ph.markdown(f'<div class="combo-box"><p class="combo-text">{c}</p></div>', unsafe_allow_html=True)
            speak(c)
            time.sleep(delay)

def stats_ui():
    st.title("📊 Data Hub")
    df = pd.read_sql_query("SELECT * FROM training", db.conn)
    
    if not df.empty:
        # NEW: Ghost Mode (Best vs Current)
        best = db.get_best_score()
        last = df['intensity'].iloc[-1]
        
        c1, c2 = st.columns(2)
        c1.metric("Last Score", f"{last:.0f}")
        c2.metric("All-Time Best", f"{best:.0f}", delta=f"{last-best:.0f}")
        
        fig = px.bar(df, x='date', y='intensity', title="Work Rate History")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white")
        fig.update_traces(marker_color='#ff4b4b')
        st.plotly_chart(fig, use_container_width=True)
        
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Export CSV", csv, "data.csv", "text/csv", use_container_width=True)
    else:
        st.info("Log a session to see data.")

# --- 6. NAVIGATION ---
nav = st.radio("Nav", ["Timer", "Coach", "Stats"], horizontal=True, label_visibility="collapsed")

if nav == "Timer": timer_ui()
elif nav == "Coach": coach_ui()
elif nav == "Stats": stats_ui()

# --- 7. QUICK LOG ---
with st.expander("📝 Quick Log Session"):
    with st.form("log"):
        r = st.number_input("Rounds", 1, 15, 6)
        p = st.number_input("Punches", 0, 2000, 300)
        i = st.slider("Intensity (RPE)", 1, 10, 7)
        if st.form_submit_button("Save Log", use_container_width=True):
            score = db.log_session(r, p, i)
            st.success(f"Saved! Intensity Score: {score:.0f}")