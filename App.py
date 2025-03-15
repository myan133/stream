import streamlit as st
import numpy as np
import time
import json
import random
from streamlit_webrtc import webrtc_streamer
import plotly.graph_objects as go

# Set page configuration
st.set_page_config(
    page_title="Chinese Museum Virtual Guide",
    page_icon="🏛️",
    layout="wide"
)

# Define CSS for styling
st.markdown("""
<style>
    .main {
        background-color: #f5f5f5;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
    }
    .chat-message.user {
        background-color: #2b313e;
        color: #fff;
    }
    .chat-message.bot {
        background-color: #475063;
        color: #fff;
    }
    .chat-message .avatar {
        width: 20%;
    }
    .chat-message .avatar img {
        max-width: 78px;
        max-height: 78px;
        border-radius: 50%;
        object-fit: cover;
    }
    .chat-message .message {
        width: 80%;
        padding: 0 1.5rem;
    }
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1533856493584-0c6ca8ca9ce3?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1470&q=80");
        background-size: cover;
    }
    .model-container {
        border: 2px solid #8B0000;
        border-radius: 10px;
        padding: 10px;
        background-color: rgba(255, 255, 255, 0.8);
    }
    .chinese-heading {
        font-family: 'Ma Shan Zheng', cursive;
        color: #8B0000;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state variables
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'speaking' not in st.session_state:
    st.session_state.speaking = False
if 'lip_sync_frames' not in st.session_state:
    st.session_state.lip_sync_frames = []
if 'current_frame' not in st.session_state:
    st.session_state.current_frame = 0
if 'last_update_time' not in st.session_state:
    st.session_state.last_update_time = time.time()

# Title
st.markdown("<h1 class='chinese-heading'>故宫智能导览 - Imperial Palace AI Guide</h1>", unsafe_allow_html=True)

# Create two columns for layout
col1, col2 = st.columns([3, 2])

# Chinese Museum knowledge base (simplified)
museum_data = {
    "terracotta warriors": "The Terracotta Army is a collection of terracotta sculptures depicting the armies of Qin Shi Huang, the first Emperor of China. Dating from approximately the late third century BCE, they were discovered in 1974 by local farmers.",
    "jade burial suit": "Jade burial suits were ceremonial suits made of pieces of jade in which nobles of the Han dynasty were buried. They were thought to protect the body from decay.",
    "bronze vessels": "Ancient Chinese bronze vessels are some of the most impressive artifacts from China's bronze age. These vessels were used in religious ceremonies to make food and wine offerings to ancestors.",
    "forbidden city": "The Forbidden City is a palace complex in central Beijing. It houses the Palace Museum and was the former Chinese imperial palace from the Ming dynasty to the end of the Qing dynasty.",
    "ming vase": "Ming vases are Chinese porcelain vases made during the Ming Dynasty. They are known for their distinctive blue and white designs and are highly valued by collectors.",
    "chinese calligraphy": "Chinese calligraphy is the writing of Chinese characters as an art form. It has been widely practiced in China and has been valued above all other visual arts.",
    "default": "I'm your virtual guide to the Chinese museum. Ask me about exhibits like the Terracotta Warriors, jade burial suits, bronze vessels, the Forbidden City, Ming vases, or Chinese calligraphy."
}

# Function to generate 3D model with lip sync
def generate_3d_model(speaking=False, frame=0):
    # Create a simplified face model with adjustable mouth
    mouth_open = 0.1
    
    if speaking:
        # Simulate lip movement
        lip_positions = [0.1, 0.2, 0.3, 0.2, 0.1, 0.3, 0.2]
        mouth_open = lip_positions[frame % len(lip_positions)]
    
    # Face outline
    u = np.linspace(0, 2*np.pi, 100)
    v = np.linspace(0, np.pi, 100)
    x = 1 * np.outer(np.cos(u), np.sin(v))
    y = 1 * np.outer(np.sin(u), np.sin(v))
    z = 1 * np.outer(np.ones(np.size(u)), np.cos(v))
    
    # Eyes (simplified)
    eye_x = [-0.4, 0.4]
    eye_y = [0.3, 0.3]
    eye_z = [0.85, 0.85]
    
    # Mouth (adjustable)
    mouth_u = np.linspace(0.3*np.pi, 0.7*np.pi, 20)
    mouth_x = 0.5 * np.cos(mouth_u)
    mouth_y = -0.3 + mouth_open * np.sin(mouth_u) * 0.5
    mouth_z = np.ones_like(mouth_u) * 0.87

    # Create the 3D figure
    fig = go.Figure()
    
    # Add the face
    fig.add_trace(go.Surface(x=x, y=y, z=z, colorscale='Reds', showscale=False, opacity=0.7))
    
    # Add eyes
    for i in range(2):
        fig.add_trace(go.Scatter3d(x=[eye_x[i]], y=[eye_y[i]], z=[eye_z[i]], 
                                  mode='markers', marker=dict(size=10, color='black')))
    
    # Add mouth
    fig.add_trace(go.Scatter3d(x=mouth_x, y=mouth_y, z=mouth_z, 
                              mode='lines', line=dict(color='black', width=5)))
    
    # Add traditional Chinese hat/decoration
    hat_x = np.linspace(-0.8, 0.8, 20)
    hat_y = np.ones_like(hat_x) * 0.1
    hat_z = 1.2 + 0.5 * np.exp(-(hat_x**2)/0.3)
    fig.add_trace(go.Scatter3d(x=hat_x, y=hat_y, z=hat_z, 
                              mode='lines', line=dict(color='red', width=5)))
    
    # Set layout
    fig.update_layout(
        autosize=True,
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            aspectmode='data'
        ),
        margin=dict(l=0, r=0, b=0, t=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

# Function to get response from museum knowledge base
def get_museum_response(query):
    query = query.lower()
    for key in museum_data:
        if key in query:
            return museum_data[key]
    return museum_data["default"]

# Generate frames for lip syncing
def generate_lip_sync_frames(text):
    # Simple algorithm: one frame per character with some randomness
    frames = []
    for _ in range(len(text) * 2):
        frames.append(random.randint(0, 6))
    return frames

# Create our virtual guide in column 1
with col1:
    st.markdown("<div class='model-container'>", unsafe_allow_html=True)
    st.subheader("Virtual Museum Guide - 博物馆虚拟导游")
    
    # Display the 3D model
    if st.session_state.speaking:
        # Update frame for lip sync animation
        current_time = time.time()
        if current_time - st.session_state.last_update_time > 0.1:  # Update every 100ms
            st.session_state.current_frame = (st.session_state.current_frame + 1) % len(st.session_state.lip_sync_frames)
            st.session_state.last_update_time = current_time
        
        model_fig = generate_3d_model(speaking=True, frame=st.session_state.lip_sync_frames[st.session_state.current_frame])
    else:
        model_fig = generate_3d_model(speaking=False)
    
    st.plotly_chart(model_fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Add cultural artifacts display
    st.subheader("Featured Artifacts - 特色文物")
    
    # Create three columns for artifacts
    art1, art2, art3 = st.columns(3)
    
    with art1:
        st.image("https://media.istockphoto.com/photos/terracotta-warriors-picture-id155384939", 
                 caption="Terracotta Warriors - 兵马俑")
    
    with art2:
        st.image("https://media.istockphoto.com/photos/ancient-chinese-jade-burial-suit-picture-id1093153314", 
                 caption="Jade Burial Suit - 玉衣")
        
    with art3:
        st.image("https://media.istockphoto.com/photos/ancient-chinese-bronze-ware-picture-id1175143560", 
                 caption="Bronze Vessel - 青铜器")

# Chat interface in column 2
with col2:
    st.markdown("<div class='model-container'>", unsafe_allow_html=True)
    st.subheader("Chat with the Museum Guide - 与导游对话")
    
    # Display chat messages
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"""
            <div class="chat-message user">
                <div class="message">{message["content"]}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message bot">
                <div class="message">{message["content"]}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Chat input
    user_input = st.text_input("Ask about Chinese artifacts:", placeholder="e.g., Tell me about the Terracotta Warriors")
    
    if user_input:
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Get response
        response = get_museum_response(user_input)
        
        # Trigger lip sync
        st.session_state.speaking = True
        st.session_state.lip_sync_frames = generate_lip_sync_frames(response)
        st.session_state.current_frame = 0
        
        # Add bot response to chat
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Force a rerun to update the UI
        st.experimental_rerun()
    
    # Stop speaking after 5 seconds of no new messages
    if st.session_state.speaking and time.time() - st.session_state.last_update_time > 5:
        st.session_state.speaking = False
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Language options
    st.subheader("Language - 语言")
    lang_option = st.selectbox("Select Language", ["English", "中文 (Chinese)"])

# Footer
st.markdown("""
<div style="text-align: center; margin-top: 30px; padding: 20px; background-color: rgba(139, 0, 0, 0.1);">
    <p>© 2025 Imperial Palace Museum Virtual Guide</p>
    <p>故宫博物院虚拟导览系统</p>
</div>
""", unsafe_allow_html=True)

# Add information about the app
with st.expander("About this Application"):
    st.write("""
    This application demonstrates a virtual museum guide for a Chinese museum with the following features:
    
    - 3D animated character with lip-syncing capabilities
    - Interactive chatbot with knowledge about Chinese artifacts
    - Dynamic visual responses to user queries
    - Bilingual support (English/Chinese)
    
    Note: This is a demonstration prototype. In a production environment, this would be enhanced with:
    - More sophisticated 3D models using three.js or Unity WebGL
    - Advanced lip-syncing using audio processing
    - Integration with a comprehensive museum database
    - Full natural language processing capabilities
    """)