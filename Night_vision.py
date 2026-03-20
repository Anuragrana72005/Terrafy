import streamlit as st
import cv2
import time
import numpy as np
import base64
import os
import psutil
import pandas as pd
from datetime import datetime
from collections import defaultdict, deque
from ultralytics import YOLO
import math

# ==========================================
# ⚙️ CONFIGURATION & CSS STYLING
# ==========================================
st.set_page_config(page_title="Terrafy | AI Sentinel V3", page_icon="🛡️", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Inter:wght@300;400;600&display=swap');
    .stApp { background: radial-gradient(circle at top, #0a0e0b 0%, #000000 100%); color: #f0f4f1; font-family: 'Inter', sans-serif; }
    h1, h2, h3 { font-family: 'Playfair Display', serif !important; color: #d4af37 !important; letter-spacing: 1px; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {background: transparent !important;}
    [data-testid="stMetricValue"] { color: #d4af37 !important; font-size: 2.2rem !important; font-family: 'Playfair Display', serif !important; }
    .threat-log { background: rgba(10, 14, 11, 0.9); border: 1px solid rgba(212, 175, 55, 0.3); border-radius: 8px; padding: 15px; height: 350px; overflow-y: auto; font-family: 'Courier New', Courier, monospace; font-size: 0.9rem; color: #4CAF50; }
    @keyframes flash-critical { 0% { background-color: rgba(255, 0, 0, 0.2); border: 2px solid #ff4c4c; box-shadow: 0 0 20px rgba(255,0,0,0.5); } 50% { background-color: rgba(255, 0, 0, 0.6); border: 2px solid #ff0000; box-shadow: 0 0 40px rgba(255,0,0,0.8); } 100% { background-color: rgba(255, 0, 0, 0.2); border: 2px solid #ff4c4c; box-shadow: 0 0 20px rgba(255,0,0,0.5); } }
    .alert-critical { animation: flash-critical 1s infinite; padding: 20px; border-radius: 12px; text-align: center; color: white; font-weight: 900; font-size: 1.5rem; letter-spacing: 2px; }
    @keyframes flash-warning { 0% { background-color: rgba(255, 204, 0, 0.2); border: 2px solid #ffcc00; box-shadow: 0 0 20px rgba(255,204,0,0.3); } 50% { background-color: rgba(255, 204, 0, 0.5); border: 2px solid #ffcc00; box-shadow: 0 0 30px rgba(255,204,0,0.6); } 100% { background-color: rgba(255, 204, 0, 0.2); border: 2px solid #ffcc00; box-shadow: 0 0 20px rgba(255,204,0,0.3); } }
    .alert-warning { animation: flash-warning 1.5s infinite; padding: 20px; border-radius: 12px; text-align: center; color: white; font-weight: 800; font-size: 1.3rem; letter-spacing: 1px; }
    .alert-clear { background: rgba(76, 175, 80, 0.1); border: 1px solid #4CAF50; padding: 20px; border-radius: 12px; text-align: center; color: #4CAF50; font-weight: 600; font-size: 1.2rem; }
    </style>
    """, unsafe_allow_html=True)

# Create Snapshot Directory
os.makedirs("snapshots", exist_ok=True)

# ==========================================
# 🧠 AI & STATE INITIALIZATION
# ==========================================
@st.cache_resource
def load_model():
    return YOLO("yolov8s.pt")

model = load_model()
HUMAN_CLASSES = [0]
ANIMAL_CLASSES = [15, 16, 17, 18, 19, 20, 21, 22, 23, 24]
TARGET_CLASSES = HUMAN_CLASSES + ANIMAL_CLASSES

if "system_armed" not in st.session_state: st.session_state.system_armed = False
if "incident_log" not in st.session_state: st.session_state.incident_log = []
if "trajectories" not in st.session_state: st.session_state.trajectories = defaultdict(lambda: deque(maxlen=20))
if "last_human_alarm" not in st.session_state: st.session_state.last_human_alarm = 0
if "last_animal_alarm" not in st.session_state: st.session_state.last_animal_alarm = 0
if "last_snapshot" not in st.session_state: st.session_state.last_snapshot = 0
# Initialize an empty heatmap canvas
if "heatmap_layer" not in st.session_state: st.session_state.heatmap_layer = np.zeros((600, 800), dtype=np.float32)

# ==========================================
# 🎨 HUD & AUDIO FUNCTIONS
# ==========================================
def trigger_audio(threat_type, audio_placeholder):
    now = time.time()
    b64 = ""
    if threat_type == "HUMAN" and (now - st.session_state.last_human_alarm > 10):
        try:
            with open("human_sound.mp3", "rb") as f: b64 = base64.b64encode(f.read()).decode()
            st.session_state.last_human_alarm = now
        except: pass
    elif threat_type == "ANIMAL" and (now - st.session_state.last_animal_alarm > 10):
        try:
            with open("animal_sound.mp3", "rb") as f: b64 = base64.b64encode(f.read()).decode()
            st.session_state.last_animal_alarm = now
        except: pass

    if b64:
        audio_placeholder.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>', unsafe_allow_html=True)

def draw_hud_target(img, x1, y1, x2, y2, color, label, track_id, speed_status):
    thickness = 2
    length = 25
    cv2.line(img, (x1, y1), (x1 + length, y1), color, thickness)
    cv2.line(img, (x1, y1), (x1, y1 + length), color, thickness)
    cv2.line(img, (x2, y1), (x2 - length, y1), color, thickness)
    cv2.line(img, (x2, y1), (x2, y1 + length), color, thickness)
    cv2.line(img, (x1, y2), (x1 + length, y2), color, thickness)
    cv2.line(img, (x1, y2), (x1, y2 - length), color, thickness)
    cv2.line(img, (x2, y2), (x2 - length, y2), color, thickness)
    cv2.line(img, (x2, y2), (x2, y2 - length), color, thickness)
    
    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
    cv2.drawMarker(img, (cx, cy), color, markerType=cv2.MARKER_CROSS, markerSize=15, thickness=1)
    
    display_text = f"ID:{track_id} {label} [{speed_status}]"
    cv2.rectangle(img, (x1, y1 - 25), (x1 + len(display_text)*8, y1), color, -1)
    cv2.putText(img, display_text, (x1 + 5, y1 - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 2)

# ==========================================
# 📱 UI DASHBOARD & SIDEBAR
# ==========================================
with st.sidebar:
    st.markdown("<h2>🛡️ Sentinel Command</h2>", unsafe_allow_html=True)
    camera_url = st.text_input("Camera Uplink URL/IP", value="http://10.40.226.171:8080/video")
    st.markdown("---")
    st.markdown("### 🎛️ Matrix Settings")
    conf_threshold = st.slider("Neural Confidence", 0.1, 1.0, 0.35)
    optics_mode = st.selectbox("Optics Filter", ["Standard RGB", "Thermal (FLIR)", "Night Vision (Green)"])
    
    # NEW V3 TOGGLES
    show_heatmap = st.toggle("🔥 Enable Spatial Heatmap")
    privacy_mode = st.toggle("👤 Compliance Masking (Blur Humans)")
    
    st.markdown("---")
    st.markdown("### 📊 System Telemetry")
    sys_col1, sys_col2 = st.columns(2)
    cpu_metric = sys_col1.empty()
    ram_metric = sys_col2.empty()
    st.markdown("---")
    col_start, col_stop = st.columns(2)
    if col_start.button("🟢 ARM MATRIX"): st.session_state.system_armed = True
    if col_stop.button("🔴 DISARM"): st.session_state.system_armed = False
    
    st.markdown("---")
    # Data Export Feature
    if st.session_state.incident_log:
        df = pd.DataFrame({"Event Log": st.session_state.incident_log})
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(label="📥 Download Forensic CSV", data=csv, file_name="terrafy_threat_log.csv", mime="text/csv")

st.markdown("<h1>Advanced Perimeter Defense V3</h1>", unsafe_allow_html=True)
st.caption("MULTI-TIER GEOFENCING • TRAJECTORY ANALYTICS • HEATMAPS • PRIVACY COMPLIANCE")
st.markdown("---")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Defense Status", "ARMED 🟢" if st.session_state.system_armed else "OFFLINE 🔴")
m2.metric("Camera Feed", "ACTIVE" if st.session_state.system_armed else "STANDBY")
m3.metric("Current Optics", optics_mode)
m4.metric("Logged Incidents", len(st.session_state.incident_log))

feed_col, log_col = st.columns([2, 1])
with feed_col:
    frame_placeholder = st.empty()
    audio_placeholder = st.empty()
with log_col:
    st.markdown("### 🚨 Matrix Status")
    alert_placeholder = st.empty()
    if not st.session_state.system_armed:
        alert_placeholder.markdown("<div class='alert-clear'>SYSTEM OFFLINE</div>", unsafe_allow_html=True)
    st.markdown("### 📋 Event Forensics")
    log_placeholder = st.empty()

# ==========================================
# 🚀 CORE PROCESSING LOOP
# ==========================================
if st.session_state.system_armed:
    cap = cv2.VideoCapture(camera_url)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1) 
    
    counter = 0
    prev_time = time.time()

    # Reset heatmap on arming if dimensions mismatch (safety check)
    st.session_state.heatmap_layer = np.zeros((600, 800), dtype=np.float32)

    while st.session_state.system_armed:
        ret, frame = cap.read()
        if not ret:
            frame_placeholder.error("Uplink lost. Retrying...")
            time.sleep(1)
            continue

        frame = cv2.resize(frame, (800, 600))
        h, w, _ = frame.shape
        counter += 1
        
        # Telemetry
        current_time = time.time()
        fps = int(1 / (current_time - prev_time + 0.001))
        prev_time = current_time
        
        if counter % 10 == 0:
            cpu_metric.metric("CPU Load", f"{psutil.cpu_percent()}%")
            ram_metric.metric("RAM Load", f"{psutil.virtual_memory().percent}%")

        # Geofence Dimensions
        w_margin_x, w_margin_y = int(w * 0.10), int(h * 0.10)
        wx1, wy1, wx2, wy2 = w_margin_x, w_margin_y, w - w_margin_x, h - w_margin_y
        
        c_margin_x, c_margin_y = int(w * 0.25), int(h * 0.25)
        cx1, cy1, cx2, cy2 = c_margin_x, c_margin_y, w - c_margin_x, h - c_margin_y

        clean_ai_frame = frame.copy()

        # Optics
        if optics_mode == "Thermal (FLIR)":
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frame = cv2.applyColorMap(gray, cv2.COLORMAP_INFERNO)
        elif optics_mode == "Night Vision (Green)":
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            zeros = np.zeros_like(gray)
            frame = cv2.merge([zeros, gray, zeros])

        highest_threat = "CLEAR"
        detected_label = ""

        # Tracking
        results = model.track(clean_ai_frame, conf=conf_threshold, classes=TARGET_CLASSES, imgsz=640, persist=True, verbose=False)
        
        current_ids = []
        if results[0].boxes is not None and len(results[0].boxes) > 0:
            for box in results[0].boxes:
                cls_id = int(box.cls[0])
                bx1, by1, bx2, by2 = map(int, box.xyxy[0])
                track_id = int(box.id[0]) if box.id is not None else 0
                current_ids.append(track_id)
                
                obj_cx, obj_cy = (bx1 + bx2) // 2, (by1 + by2) // 2
                st.session_state.trajectories[track_id].append((obj_cx, obj_cy))
                
                # Update Heatmap Array
                if show_heatmap:
                    st.session_state.heatmap_layer[by1:by2, bx1:bx2] += 0.05
                
                speed_status = "STATIC"
                pts = st.session_state.trajectories[track_id]
                if len(pts) > 5:
                    dist = math.hypot(pts[-1][0] - pts[0][0], pts[-1][1] - pts[0][1])
                    if dist > 40: speed_status = "FAST"
                    elif dist > 15: speed_status = "MOVING"

                for i in range(1, len(pts)):
                    cv2.line(frame, pts[i-1], pts[i], (255, 255, 255), 2)

                in_critical = (bx1 < cx2 and bx2 > cx1 and by1 < cy2 and by2 > cy1)
                in_warning = (bx1 < wx2 and bx2 > wx1 and by1 < wy2 and by2 > wy1)

                is_human = cls_id in HUMAN_CLASSES
                target_label = "HUMAN" if is_human else "WILDLIFE"

                # Privacy Masking Logic (Blur humans outside critical zone)
                if privacy_mode and is_human and not in_critical:
                    roi = frame[by1:by2, bx1:bx2]
                    if roi.size > 0:
                        frame[by1:by2, bx1:bx2] = cv2.blur(roi, (35, 35))

                if in_critical:
                    highest_threat = "CRITICAL"
                    detected_label = target_label
                    draw_hud_target(frame, bx1, by1, bx2, by2, (0, 0, 255), target_label, track_id, speed_status)
                elif in_warning:
                    if highest_threat != "CRITICAL": highest_threat = "WARNING"
                    detected_label = target_label
                    draw_hud_target(frame, bx1, by1, bx2, by2, (0, 215, 255), target_label, track_id, speed_status)
                else:
                    draw_hud_target(frame, bx1, by1, bx2, by2, (150, 150, 150), "APPROACHING", track_id, speed_status)

        # Render Heatmap Overlay
        if show_heatmap:
            # Normalize and apply colormap
            norm_heatmap = cv2.normalize(st.session_state.heatmap_layer, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
            heatmap_color = cv2.applyColorMap(norm_heatmap, cv2.COLORMAP_JET)
            # Create a mask to only overlay where there is heat
            mask = norm_heatmap > 10
            frame[mask] = cv2.addWeighted(frame, 0.5, heatmap_color, 0.5, 0)[mask]

        st.session_state.trajectories = defaultdict(lambda: deque(maxlen=20), {k: v for k, v in st.session_state.trajectories.items() if k in current_ids})

        cv2.rectangle(frame, (wx1, wy1), (wx2, wy2), (0, 215, 255) if highest_threat == "WARNING" else (255, 255, 0), 1)
        cv2.putText(frame, "WARNING ZONE", (wx1 + 5, wy1 + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 215, 255), 1)
        
        cv2.rectangle(frame, (cx1, cy1), (cx2, cy2), (0, 0, 255) if highest_threat == "CRITICAL" else (0, 0, 255), 2)
        cv2.putText(frame, "CRITICAL ZONE", (cx1 + 5, cy1 + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(frame, f"FPS: {fps} | OPTICS: {optics_mode}", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        frame_placeholder.image(frame, channels="BGR", use_container_width=True)

        # --- EVENT HANDLING ---
        if highest_threat == "CRITICAL":
            trigger_audio("HUMAN" if detected_label == "HUMAN" else "ANIMAL", audio_placeholder)
            if current_time - st.session_state.last_snapshot > 5:
                snap_path = f"snapshots/breach_{datetime.now().strftime('%H%M%S')}.jpg"
                cv2.imwrite(snap_path, clean_ai_frame) 
                st.session_state.last_snapshot = current_time
            
            alert_placeholder.markdown(f"<div class='alert-critical'>🚨 CRITICAL BREACH<br><small>{detected_label} in Inner Perimeter!</small></div>", unsafe_allow_html=True)
            log_entry = f"[{datetime.now().strftime('%H:%M:%S')}] CRITICAL: {detected_label} inside Core Zone. Snapshot Saved."
            
        elif highest_threat == "WARNING":
            alert_placeholder.markdown(f"<div class='alert-warning'>⚠️ WARNING<br><small>{detected_label} entered Outer Perimeter</small></div>", unsafe_allow_html=True)
            log_entry = f"[{datetime.now().strftime('%H:%M:%S')}] WARNING: {detected_label} loitering in Outer Zone."
            
        else:
            alert_placeholder.markdown("<div class='alert-clear'>🟢 SECURE<br><small>All nodes reporting normal</small></div>", unsafe_allow_html=True)
            audio_placeholder.empty()
            log_entry = None

        if log_entry and (not st.session_state.incident_log or st.session_state.incident_log[0] != log_entry):
            st.session_state.incident_log.insert(0, log_entry)

        log_html = "<div class='threat-log'>" + "<br>".join(st.session_state.incident_log[:20]) + "</div>"
        log_placeholder.markdown(log_html, unsafe_allow_html=True)

    cap.release()

# ==========================================
# 📂 OFFLINE FORENSIC GALLERY
# ==========================================
else:
    # Render the offline state UI
    log_html = "<div class='threat-log'>" + "<br>".join(st.session_state.incident_log[:20]) + "</div>"
    log_placeholder.markdown(log_html, unsafe_allow_html=True)
    
    with feed_col:
        st.info("ℹ️ System is currently Disarmed. Displaying Forensic Archives.")
        st.markdown("### 📸 Critical Breach Snapshots")
        
        # Load images from the snapshots folder
        snapshot_files = [f for f in os.listdir("snapshots") if f.endswith('.jpg')]
        snapshot_files.sort(reverse=True) # Show newest first
        
        if snapshot_files:
            # Create a grid for images
            cols = st.columns(3)
            for idx, file in enumerate(snapshot_files[:9]): # Display up to 9 recent images
                with cols[idx % 3]:
                    img_path = os.path.join("snapshots", file)
                    st.image(img_path, caption=file, use_container_width=True)
        else:
            st.warning("No breach snapshots found in the archive.")