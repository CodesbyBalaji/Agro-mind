"""
AgroMind+ Streamlit Dashboard
Interactive web interface for farmers
"""

import streamlit as st
import numpy as np
import pandas as pd
import sys
import os
import plotly.express as px
import plotly.graph_objects as go

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from integrated_system import AgroMindIntegratedSystem

# Page configuration
st.set_page_config(
    page_title="AgroMind+ | Smart Crop Advisory",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Glassmorphism & Theme
def apply_custom_css(dark_mode):
    if dark_mode:
        bg_color = "#0e1117"
        card_bg = "rgba(30, 41, 59, 0.7)"
        text_color = "#f8fafc"
        border_color = "rgba(255, 255, 255, 0.1)"
        glass_overlay = "rgba(17, 25, 40, 0.75)"
    else:
        bg_color = "#f0f2f6"
        card_bg = "rgba(255, 255, 255, 0.6)"
        text_color = "#1e293b"
        border_color = "rgba(0, 0, 0, 0.1)"
        glass_overlay = "rgba(255, 255, 255, 0.7)"

    st.markdown(f"""
    <style>
        .stApp {{
            background: linear-gradient({glass_overlay}, {glass_overlay}), 
                        url("https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=1920&q=80");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        @keyframes fadeInSlide {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        @keyframes pulseGlow {{
            0% {{ box-shadow: 0 0 5px rgba(76, 175, 80, 0.2); }}
            50% {{ box-shadow: 0 0 20px rgba(76, 175, 80, 0.6); }}
            100% {{ box-shadow: 0 0 5px rgba(76, 175, 80, 0.2); }}
        }}
        @keyframes skeletonPulse {{
            0% {{ background-color: rgba(255, 255, 255, 0.05); }}
            50% {{ background-color: rgba(255, 255, 255, 0.15); }}
            100% {{ background-color: rgba(255, 255, 255, 0.05); }}
        }}
        @keyframes iconSway {{
            0% {{ transform: rotate(-10deg); }}
            50% {{ transform: rotate(10deg); }}
            100% {{ transform: rotate(-10deg); }}
        }}
        
        .skeleton {{
            height: 20px;
            width: 100%;
            border-radius: 10px;
            animation: skeletonPulse 1.5s infinite ease-in-out;
            margin: 10px 0;
        }}
        
        .animated-icon {{
            display: inline-block;
            animation: iconSway 3s infinite ease-in-out;
            font-size: 2rem;
        }}
        
        .main-header {{
            font-size: clamp(1.5rem, 5vw, 2.8rem);
            color: #fff;
            text-align: center;
            font-weight: 800;
            padding: 1.2rem;
            background: linear-gradient(135deg, #1b4332, #2d6a4f);
            border-radius: 15px;
            animation: fadeInSlide 1s ease-out, pulseGlow 3s infinite;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            margin-bottom: 1.5rem;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
        
        [data-testid="stMetricValue"] {{
            animation: fadeInSlide 1s ease-out backwards;
        }}
        
        .glass-card {{
            background: {card_bg};
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border-radius: 20px;
            border: 1px solid {border_color};
            padding: clamp(1rem, 3vw, 2rem);
            margin-bottom: 1rem;
            color: {text_color};
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15);
            animation: fadeInSlide 0.8s ease-out backwards;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            overflow-x: hidden;
        }}
        
        .glass-card:hover {{
            transform: translateY(-5px);
            border-color: #4CAF50;
            box-shadow: 0 12px 40px 0 rgba(76, 175, 80, 0.25);
        }}
        
        /* Circular Progress Styling */
        .progress-ring {{
            display: flex;
            justify-content: center;
            align-items: center;
            position: relative;
        }}
        
        /* Mobile specific adjustments */
        @media (max-width: 768px) {{
            .main-header {{
                padding: 1rem;
                margin-bottom: 1rem;
            }}
            .glass-card {{
                padding: 1rem;
            }}
            .stMetric {{
                padding: 5px;
            }}
            [data-testid="column"] {{
                width: 100% !important;
                flex: 1 1 100% !important;
            }}
        }}

        .stMetric {{
            background: rgba(255, 255, 255, 0.05);
            padding: 10px;
            border-radius: 10px;
            animation: fadeInSlide 1s ease-out backwards;
        }}
        /* Modern Sidebar */
        [data-testid="stSidebar"] {{
            background-color: {glass_overlay} !important;
            backdrop-filter: blur(15px);
        }}
        /* Navigation styling */
        .nav-item {{
            padding: 10px 15px;
            border-radius: 10px;
            margin: 5px 0;
            cursor: pointer;
            transition: all 0.2s;
        }}
        .nav-item:hover {{
            background: rgba(76, 175, 80, 0.1);
        }}
    </style>
    """, unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'system' not in st.session_state:
        st.session_state.system = None
    if 'recommendations' not in st.session_state:
        st.session_state.recommendations = None
    if 'selected_crop' not in st.session_state:
        st.session_state.selected_crop = None
    if 'advisory_report' not in st.session_state:
        st.session_state.advisory_report = None
    if 'messages' not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "How can I help you with your farm today?"}]

def render_ai_chat():
    st.markdown("### 🤖 Ask AgroMind AI")
    
    # Prebuilt questions buttons
    cols = st.columns(2)
    if cols[0].button("Rice vs Wheat?", use_container_width=True):
        st.session_state.messages.append({"role": "user", "content": "Why is rice better than wheat?"})
        st.session_state.messages.append({"role": "assistant", "content": "Rice thrives in high moisture and clay-rich soil. Given the current agriculture indices, Rice is more suitable for water-heavy segments, leading to higher PSI scores in your analysis."})
    if cols[1].button("Yield Boost?", use_container_width=True):
        st.session_state.messages.append({"role": "user", "content": "How can I increase my yield?"})
        st.session_state.messages.append({"role": "assistant", "content": "To increase yield: 1. Optimize NPK based on the Advisory Report. 2. Monitor soil moisture during critical stages. 3. Consider crop rotation with legumes next season."})

    # Chat history
    chat_container = st.container(height=300)
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

    # User input
    if prompt := st.chat_input("Ask me something..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with chat_container:
            with st.chat_message("user"):
                st.write(prompt)
        
        # Simple Logic Response
        response = "Analyzing your farm data... I recommend checking your moisture levels as they seem to have the highest contribution to your current recommendations."
        if "rice" in prompt.lower():
            response = "Rice is currently prioritized because your rainfall data supports anaerobic soil conditions."
        elif "yield" in prompt.lower():
            response = "For yield growth, focusing on precise Potassium application during Week 4 is critical for your current crop selection."
            
        st.session_state.messages.append({"role": "assistant", "content": response})
        with chat_container:
            with st.chat_message("assistant"):
                st.write(response)

def main():
    """Main dashboard function"""
    initialize_session_state()
    
    # Sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/plasticine/400/farm.png", 
                use_container_width=True)
        
        st.markdown("### 🌓 UI Settings")
        dark_mode = st.toggle("🌙 Dark Mode", value=True)
        apply_custom_css(dark_mode)
        
        st.markdown("---")
        st.markdown("## 🧭 Navigation")
        nav_selection = st.radio("", ["📊 Data Input", "🌾 Crop Recommendations", 
                                       "💡 Advisory Report", "📈 Analytics"])
        
        st.markdown("---")
        st.markdown("## 📍 Farm Details")
        farm_id = st.text_input("Farm ID", value="FARM_001")
        farm_size = st.number_input("Farm Size (hectares)", min_value=0.1, 
                                    max_value=100.0, value=2.0, step=0.1)
        region = st.selectbox("Region", ["North", "South", "East", "West", "Central"])
        
        st.markdown("---")
        st.markdown("### 🔄 System Configuration")
        if st.button("🚀 Initialize AI Engines", type="primary", use_container_width=True):
            with st.spinner("Calibrating LSTM model..."):
                try:
                    st.session_state.system = AgroMindIntegratedSystem()
                    st.success("✅ AI Engine Ready!")
                except Exception as e:
                    st.error(f"⚠️ Initialization Error: {e}")
        
        st.markdown("---")
        render_ai_chat()

    # Header
    st.markdown('<div class="main-header">🌾 AgroMind+ | AI Smart Crop Advisory</div>', 
                unsafe_allow_html=True)
    
    # Logic for navigation
    if nav_selection == "📊 Data Input":
        render_data_input()
    elif nav_selection == "🌾 Crop Recommendations":
        render_recommendations(farm_size)
    elif nav_selection == "💡 Advisory Report":
        render_advisory_report(farm_size)
    elif nav_selection == "📈 Analytics":
        render_analytics()

def render_skeleton():
    """Renders a skeleton loading UI"""
    for _ in range(3):
        st.markdown('<div class="skeleton" style="width: 80%"></div>', unsafe_allow_html=True)
        st.markdown('<div class="skeleton" style="width: 100%"></div>', unsafe_allow_html=True)
        st.markdown('<div class="skeleton" style="width: 60%"></div>', unsafe_allow_html=True)
        st.markdown('<br>', unsafe_allow_html=True)

def render_data_input():
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("## 📝 Environmental Data Entry")
    st.markdown("Input 4-week history for high-fidelity AI analysis")
    
    col1, col2 = st.columns(2)
    
    weeks_data = []
    with col1:
        for week in range(1, 5):
            with st.expander(f"📅 Week {week} Data", expanded=(week==4)):
                c1, c2, c3 = st.columns(3)
                n = c1.number_input(f"N (kg/ha)", 0.0, 350.0, 120.0-week*3, key=f"n_{week}")
                p = c2.number_input(f"P (kg/ha)", 0.0, 70.0, 40.0-week*1, key=f"p_{week}")
                k = c3.number_input(f"K (kg/ha)", 0.0, 70.0, 42.0-week*1, key=f"k_{week}")
                
                ph = c1.number_input(f"pH", 4.0, 9.0, 6.8, key=f"ph_{week}")
                temp = c2.number_input(f"Temp (°C)", 10.0, 45.0, 26.0+week*0.5, key=f"t_{week}")
                hum = c3.number_input(f"Hum (%)", 20.0, 100.0, 72.0+week*2, key=f"h_{week}")
                
                moist = c1.number_input(f"Moist (%)", 20.0, 100.0, 65.0+week*2, key=f"m_{week}")
                rain = c2.number_input(f"Rain (mm)", 0.0, 300.0, 80.0+week*5, key=f"r_{week}")
                sun = c3.number_input(f"Sun (hr)", 0.0, 14.0, 6.5-week*0.2, key=f"s_{week}")
                weeks_data.append([n, p, k, ph, temp, hum, moist, rain, sun])
    
    with col2:
        st.markdown("### 📊 Live Trend Monitor")
        df = pd.DataFrame(weeks_data, columns=['N','P','K','pH','Temp','Hum','Moist','Rain','Sun'])
        st.line_chart(df[['N','P','K']])
        st.line_chart(df[['Temp','Hum','Moist']])
        
    if st.button("🔮 Pulse AI Analysis", type="primary", use_container_width=True):
        if st.session_state.system:
            # Use skeleton while processing
            placeholder = st.empty()
            with placeholder.container():
                render_skeleton()
                
            with st.spinner(""): # Hidden since we have skeleton
                seq = np.array(weeks_data)
                st.session_state.recommendations = st.session_state.system.predict_top_crops(seq, 4)
                st.session_state.last_input = weeks_data
            
            placeholder.empty()
            st.success("Analysis Complete!")
            st.balloons()
        else:
            st.warning("Please initialize AI in sidebar.")
    st.markdown("</div>", unsafe_allow_html=True)

def render_recommendations(farm_size):
    st.markdown("## 🌾 AI Personalized Recommendations")
    
    if not st.session_state.recommendations:
        st.info("No data found. Please complete 'Data Input' first.")
        return

    # HERO AI INTERPRETABILITY SECTION
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### 🔥 AI Reasoning & Confidence Visualization")
    
    recs = st.session_state.recommendations
    crops = [r['crop'] for r in recs]
    confidences = [float(r['confidence'].strip('%')) for r in recs]
    
    fig = go.Figure(go.Bar(
        x=confidences,
        y=crops,
        orientation='h',
        marker=dict(color=['#FFD700', '#C0C0C0', '#CD7F32', '#8BC34A']),
        text=[f"{c}%" for c in confidences],
        textposition='auto',
    ))
    fig.update_layout(
        title="LSTM Model Decision Confidence",
        xaxis_title="Confidence Probability (%)",
        yaxis_autorange="reversed",
        height=300,
        margin=dict(l=0, r=0, t=30, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#fff')
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

    # Detailed Cards
    icon_map = {"Rice": "🌾", "Wheat": "🌾", "Maize": "🌽", "Corn": "🌽", "Cotton": "🌱", "Jute": "🌱"}
    
    for i, rec in enumerate(recs):
        st.markdown(f"<div class='crop-card rank-{i+1}'>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([2, 2, 1])
        with c1:
            icon = icon_map.get(rec['crop'], "🌱")
            st.markdown(f'### <span class="animated-icon">{icon}</span> {rec["crop"]}', unsafe_allow_html=True)
            st.write(f"**Sustainability Index:** {rec['psi_percentage']:.1f}%")
        with c2:
            # Animated Progress Ring using Plotly Pie Donut
            fig_ring = go.Figure(go.Pie(
                values=[confidences[i], 100-confidences[i]],
                hole=0.7,
                marker=dict(colors=['#4CAF50', 'rgba(255,255,255,0.1)']),
                textinfo='none'
            ))
            fig_ring.update_layout(
                showlegend=False, height=100, width=100,
                margin=dict(l=0, r=0, t=0, b=0),
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_ring, config={'displayModeBar': False}, use_container_width=False)
            st.caption(f"Confidence: {rec['confidence']}")
        with c3:
            if st.button(f"Generate Plan", key=f"sel_{i}"):
                st.session_state.selected_crop = rec
                # Generate advisory
                if st.session_state.system and hasattr(st.session_state, 'last_input'):
                    seq = np.array(st.session_state.last_input)
                    curr = {
                        'N': seq[-1, 0], 'P': seq[-1, 1], 'K': seq[-1, 2],
                        'pH': seq[-1, 3], 'Temperature': seq[-1, 4], 'Humidity': seq[-1, 5],
                        'Moisture': seq[-1, 6], 'Rainfall': seq[-1, 7], 'Sunlight': seq[-1, 8]
                    }
                    with st.spinner(" "): # Skeleton loader would be better here too but let's keep it simple
                        st.session_state.advisory_report = st.session_state.system.generate_adaptive_advisory(rec, curr, farm_size)
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

def render_advisory_report(farm_size):
    if not st.session_state.advisory_report:
        st.info("Select a crop in 'Recommendations' to view the manual.")
        return
        
    report = st.session_state.advisory_report
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown(f"## 💡 Advisory: {st.session_state.selected_crop['crop']}")
    st.info(report['narrative'])
    
    st.markdown("### 🌿 Precision Fertilizer Plan")
    for fert in report['fertilizer_plan']['fertilizers']:
        with st.expander(f"{fert['name']} - {fert['quantity_kg']}kg", expanded=True):
            st.write(fert['application'])
            st.caption(f"Rationale: {fert['deficit_addressed']}")
            
    st.markdown("### 💧 Smart Irrigation")
    irr = report['irrigation_plan']
    col1, col2, col3 = st.columns(3)
    col1.metric("Method", irr['recommended_type'])
    col2.metric("Frequency", irr['frequency'])
    col3.metric("Goal", f"{irr['total_water_required_mm']}mm")
    
    st.markdown("</div>", unsafe_allow_html=True)

def render_analytics():
    # Reuse previous analytics functionality but inside glass container
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("## 📊 Farm Analytics Dashboard")
    
    years = ['2020', '2021', '2022', '2023', '2024']
    yield_data = [3.2, 3.8, 4.1, 3.9, 4.5]
    profit_data = [12000, 15000, 18500, 16000, 22000]
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📈 Historical Yield")
        fig = px.line(x=years, y=yield_data, markers=True)
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        st.markdown("### 💰 Profit Projection")
        fig2 = px.area(x=years, y=profit_data)
        fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig2, use_container_width=True)
        
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        🌾 AgroMind+ | LSTM-Based Smart Crop Advisory System<br>
        Empowering Farmers with AI & Edge Computing
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()