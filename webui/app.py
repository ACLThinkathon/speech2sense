import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import json
from datetime import datetime
import numpy as np
import io

# Page configuration
st.set_page_config(
    page_title="Speech2Sense Analytics",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced styling matching the HTML theme with responsive font sizing
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Main theme colors from HTML */
    :root {
        --primary-gradient: linear-gradient(135deg, #00bcd4, #3f51b5);
        --background-gradient: linear-gradient(135deg, #f6f1f1, #d6e4f0, #e0f7fa);
        --card-bg: rgba(255, 255, 255, 0.5);
        --card-hover: rgba(255, 255, 255, 0.7);
        --text-primary: #333;
        --text-secondary: #555;
        --accent-color: #00bcd4;

        /* Responsive font size variables */
        --base-font-size: clamp(0.75rem, 1vw + 0.5rem, 1rem);
        --small-font-size: clamp(0.7rem, 0.8vw + 0.4rem, 0.9rem);
        --medium-font-size: clamp(0.8rem, 1.2vw + 0.6rem, 1.1rem);
        --large-font-size: clamp(1rem, 1.5vw + 0.8rem, 1.4rem);
        --xlarge-font-size: clamp(1.2rem, 2vw + 1rem, 2rem);
        --header-font-size: clamp(2rem, 4vw + 1rem, 4rem);
        --card-title-size: clamp(0.85rem, 1vw + 0.5rem, 1.1rem);
        --card-value-size: clamp(1rem, 1.5vw + 0.6rem, 1.6rem);
        --card-subtitle-size: clamp(0.8rem, 0.9vw + 0.4rem, 1rem);
        --card-description-size: clamp(0.7rem, 0.8vw + 0.3rem, 0.85rem);
    }

    /* Hide Streamlit header and footer */
    header[data-testid="stHeader"] {
        display: none !important;
    }

    .stAppHeader {
        display: none !important;
    }

    /* Remove top padding from main container */
    .stApp > div:first-child {
        padding-top: 0 !important;
    }

    .block-container {
        padding-top: 1rem !important;
    }

    /* Main background */
    .stApp {
        background: var(--background-gradient);
        font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-size: var(--base-font-size);
    }

    /* Header styling - moved to very top with responsive font sizing */
    .main-header {
        background: var(--primary-gradient);
        padding: clamp(2rem, 4vw, 4rem) clamp(1rem, 3vw, 3rem);
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        margin-top: -1rem !important;
        box-shadow: 0 10px 30px rgba(0, 188, 212, 0.3);
        position: relative;
        overflow: hidden;
    }

    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: shimmer 3s ease-in-out infinite;
    }

    @keyframes shimmer {
        0%, 100% { transform: translateX(-100%) translateY(-100%) rotate(0deg); }
        50% { transform: translateX(100%) translateY(100%) rotate(180deg); }
    }

    .main-header h1 {
        font-size: var(--header-font-size);
        font-weight: 400;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        position: relative;
        z-index: 1;
        line-height: 1.2;
    }

    .main-header p {
        font-size: var(--large-font-size);
        font-weight: 400;
        opacity: 0.95;
        position: relative;
        z-index: 1;
        line-height: 1.4;
        margin-bottom: 0.8rem;
    }

    /* Responsive spinner text styling - zoom-aware */
    .stSpinner > div {
        font-size: var(--medium-font-size) !important;
    }

    .stSpinner .stMarkdown {
        font-size: var(--medium-font-size) !important;
    }

    /* Alternative approach for spinner text */
    div[data-testid="stSpinner"] p {
        font-size: var(--medium-font-size) !important;
        font-weight: 500 !important;
    }

    /* Uniform card styling for all metric cards - RESPONSIVE SIZING */
    .uniform-card {
    overflow-y: auto;
    scrollbar-width: thin;
        background: linear-gradient(135deg, #d8c4f3, #c2e0f7);
        backdrop-filter: blur(10px);
        padding: clamp(0.5rem, 1.5vw, 1.2rem);
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        text-align: center;
        border: 1px solid rgba(255,255,255,0.2);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        height: clamp(180px, 20vw + 150px, 260px) !important;
        width: 100% !important;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        align-items: center;
        box-sizing: border-box;
    }

    /* Smooth shimmer animation (non-flickering) */
    .uniform-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.8s ease-in-out;
        z-index: 0;
    }

    /* Hover effect with smooth animation */
    .uniform-card:hover {
        transform: translateY(-8px);
        background: linear-gradient(135deg, #e2d4f5, #d3ecfb);
        box-shadow: 0 15px 40px rgba(0,0,0,0.15);
    }

    /* Shimmer effect on hover - smooth, no flickering */
    .uniform-card:hover::before {
        left: 100%;
    }

    /* Icon styling - responsive sizing */
    .uniform-card .feature-icon {
        font-size: clamp(1.8rem, 3vw, 2.5rem);
        margin-bottom: 0.5rem;
        background: var(--primary-gradient);
                z-index: 1;
        position: relative;
        flex-shrink: 0;
        height: clamp(40px, 6vw, 60px);
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background: none !important;
        box-shadow: none !important;
    }

    /* Card title - responsive text handling */
    .uniform-card h3 {
    word-break: break-word;
    white-space: normal;
    height: auto;
        font-size: var(--card-title-size);
        font-weight: 400;
        margin: 0.5rem 0;
        color: #333;
        z-index: 1;
        position: relative;
        line-height: 1.2;
        flex-shrink: 0;
        height: clamp(35px, 5vw, 50px);
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background: none !important;
        box-shadow: none !important;
        text-align: center;
        word-wrap: break-word;
        overflow: hidden;
        padding: 0 0.25rem;
    }

    /* Main value - responsive sizing */
    .uniform-card h1 {
    word-break: break-word;
    white-space: normal;
    height: auto;
        font-size: var(--card-value-size);
        font-weight: 400;
        margin: 0.5rem 0;
        color: #333;
        z-index: 1;
        position: relative;
        flex-shrink: 0;
        height: clamp(45px, 6vw, 65px);
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background: none !important;
        box-shadow: none !important;
        text-align: center;
        overflow: hidden;
        line-height: 1.1;
    }

    /* Subtitle - responsive text handling */
    .uniform-card h4 {
        font-size: var(--card-subtitle-size);
        font-weight: 400;
        margin: 0.3rem 0;
        color: #555;
        z-index: 1;
        position: relative;
        line-height: 1.2;
        flex-shrink: 0;
        height: auto !important;
        max-height: none !important;
        overflow: visible !important;
        text-overflow: unset !important;
        white-space: normal !important;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background: none !important;
        box-shadow: none !important;
        text-align: center;
        word-wrap: break-word;
        padding: 0 0.25rem;
    }

    /* Description text - flexible but contained with responsive sizing */
    .uniform-card p {
        font-size: var(--card-description-size);
        color: #666;
        margin: 0;
        z-index: 1;
        position: relative;
        line-height: 1.3;
        text-align: center;
        flex-grow: 1;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background: none !important;
        box-shadow: none !important;
        padding: 0 0.5rem;
        word-wrap: break-word;
        height: auto !important;
        max-height: none !important;
        overflow: visible !important;
        text-overflow: unset !important;
        white-space: normal !important;
    }

    /* Container query support for modern browsers */
    @container (max-width: 300px) {
        .uniform-card h1 {
    word-break: break-word;
    white-space: normal;
    height: auto;
            font-size: clamp(1.2rem, 4vw, 1.8rem);
        }
        .uniform-card h3 {
    word-break: break-word;
    white-space: normal;
    height: auto;
            font-size: clamp(0.75rem, 3vw, 1rem);
        }
        .uniform-card h4 {
            font-size: clamp(0.7rem, 2.5vw, 0.9rem);
        }
        .uniform-card p {
            font-size: clamp(0.65rem, 2vw, 0.8rem);
        }
    }

    /* Responsive design adjustments for different screen sizes and zoom levels */
    @media (max-width: 1400px) {
        :root {
            --card-value-size: clamp(1.3rem, 2.2vw + 0.8rem, 2.2rem);
            --card-title-size: clamp(0.8rem, 0.9vw + 0.4rem, 1rem);
        }
    }

    @media (max-width: 1200px) {
        :root {
            --card-value-size: clamp(1.2rem, 2vw + 0.7rem, 2rem);
            --card-title-size: clamp(0.75rem, 0.8vw + 0.4rem, 0.95rem);
        }

        .uniform-card {
    overflow-y: auto;
    scrollbar-width: thin;
            height: clamp(220px, 22vw + 180px, 280px) !important;
            padding: clamp(0.8rem, 1.5vw, 1.5rem);
        }
    }

    @media (max-width: 992px) {
        :root {
            --card-value-size: clamp(1.1rem, 1.8vw + 0.6rem, 1.8rem);
            --card-title-size: clamp(0.7rem, 0.7vw + 0.3rem, 0.9rem);
            --card-subtitle-size: clamp(0.7rem, 0.8vw + 0.3rem, 0.85rem);
        }
    }

    @media (max-width: 768px) {
        :root {
            --header-font-size: clamp(1.8rem, 6vw, 2.8rem);
            --card-value-size: clamp(1rem, 1.5vw + 0.5rem, 1.6rem);
            --card-title-size: clamp(0.65rem, 0.6vw + 0.3rem, 0.85rem);
        }

        .uniform-card {
    overflow-y: auto;
    scrollbar-width: thin;
            padding: clamp(0.7rem, 1.2vw, 1.2rem);
            height: clamp(200px, 20vw + 160px, 260px) !important;
        }

        .main-header h1 {
            font-size: var(--header-font-size);
        }

        .main-header p {
            font-size: var(--medium-font-size);
        }

        /* Mobile spinner text */
        .stSpinner > div {
            font-size: var(--small-font-size) !important;
        }

        div[data-testid="stSpinner"] p {
            font-size: var(--small-font-size) !important;
        }
    }

    @media (max-width: 576px) {
        :root {
            --card-value-size: clamp(0.9rem, 1.3vw + 0.4rem, 1.4rem);
            --card-title-size: clamp(0.6rem, 0.5vw + 0.25rem, 0.8rem);
            --card-subtitle-size: clamp(0.6rem, 0.6vw + 0.25rem, 0.75rem);
            --card-description-size: clamp(0.55rem, 0.5vw + 0.2rem, 0.7rem);
        }

        .uniform-card {
    overflow-y: auto;
    scrollbar-width: thin;
            height: clamp(180px, 18vw + 140px, 240px) !important;
        }
    }

    /* Zoom level specific adjustments using media queries for high DPI displays */
    @media (-webkit-device-pixel-ratio: 1.25), (device-pixel-ratio: 1.25) {
        :root {
            --base-font-size: clamp(0.8rem, 1.1vw + 0.5rem, 1.1rem);
            --card-value-size: clamp(1.3rem, 2.3vw + 0.9rem, 2.3rem);
        }
    }

    @media (-webkit-device-pixel-ratio: 1.5), (device-pixel-ratio: 1.5) {
        :root {
            --base-font-size: clamp(0.85rem, 1.2vw + 0.6rem, 1.2rem);
            --card-value-size: clamp(1.4rem, 2.5vw + 1rem, 2.5rem);
        }
    }

    @media (-webkit-device-pixel-ratio: 2), (device-pixel-ratio: 2) {
        :root {
            --base-font-size: clamp(0.9rem, 1.3vw + 0.7rem, 1.3rem);
            --card-value-size: clamp(1.5rem, 2.7vw + 1.1rem, 2.7rem);
        }
    }

    /* High zoom level support (browser zoom > 150%) */
    @media (max-resolution: 150dpi) and (max-width: 1920px) {
        .uniform-card h1 {
    word-break: break-word;
    white-space: normal;
    height: auto;
            font-size: clamp(1.6rem, 3vw + 1rem, 3rem) !important;
        }

        .uniform-card h3 {
    word-break: break-word;
    white-space: normal;
    height: auto;
            font-size: clamp(0.9rem, 1.2vw + 0.5rem, 1.3rem) !important;
        }
    }

    /* Transcription preview styling matching expandable section with responsive fonts */
    .transcription-preview {
        background: rgba(255, 255, 255, 0.5);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }

    .transcription-preview-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        cursor: pointer;
        margin-bottom: 0.5rem;
        font-size: var(--medium-font-size);
    }

    .transcription-preview-content {
        font-family: 'Courier New', monospace;
        font-size: var(--small-font-size);
        line-height: 1.4;
        color: #333;
        background: rgba(255,255,255,0.3);
        padding: 1rem;
        border-radius: 8px;
        white-space: pre-wrap;
        max-height: 150px;
        overflow-y: auto;
    }

    /* File type indicators with responsive text */
    .file-type-indicator {
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-size: var(--small-font-size);
        font-weight: 400;
        margin-left: 0.5rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        transition: all 0.3s ease;
    }

    .audio-file {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
    }

    .text-file {
        background: linear-gradient(135deg, #f093fb, #f5576c);
        color: white;
    }

    /* CSAT styling with modern gradients */
    .csat-excellent { 
        background: linear-gradient(135deg, #4facfe, #00f2fe);
        color: white;
        border: 2px solid rgba(79, 172, 254, 0.3);
    }
    .csat-good { 
        background: linear-gradient(135deg, #43e97b, #38f9d7);
        color: white;
        border: 2px solid rgba(67, 233, 123, 0.3);
    }
    .csat-satisfactory { 
        background: linear-gradient(135deg, #fa709a, #fee140);
        color: white;
        border: 2px solid rgba(250, 112, 154, 0.3);
    }
    .csat-poor { 
        background: linear-gradient(135deg, #ff9a9e, #fecfef);
        color: #333;
        border: 2px solid rgba(255, 154, 158, 0.3);
    }
    .csat-very-poor { 
        background: linear-gradient(135deg, #ff6b6b, #ee5a52);
        color: white;
        border: 2px solid rgba(255, 107, 107, 0.3);
    }

    /* Agent performance styling */
    .agent-excellent { 
        background: linear-gradient(135deg, #4facfe, #00f2fe);
        color: white;
    }
    .agent-good { 
        background: linear-gradient(135deg, #43e97b, #38f9d7);
        color: white;
    }
    .agent-satisfactory { 
        background: linear-gradient(135deg, #fa709a, #fee140);
        color: white;
    }
    .agent-needs-improvement { 
        background: linear-gradient(135deg, #ff9a9e, #fecfef);
        color: #333;
    }
    .agent-poor { 
        background: linear-gradient(135deg, #ff6b6b, #ee5a52);
        color: white;
    }

    /* Sidebar styling - moved to top with responsive fonts */
    .css-1d391kg {
        background: var(--card-bg);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255,255,255,0.2);
        padding-top: 0 !important;
        margin-top: -1rem !important;
        font-size: var(--base-font-size);
    }

    /* Alternative sidebar selectors for different Streamlit versions */
    .stSidebar {
        padding-top: 0 !important;
        margin-top: -1rem !important;
        font-size: var(--base-font-size);
    }

    .stSidebar > div {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }

    /* Sidebar content container */
    .css-1d391kg .block-container {
        padding-top: 0.5rem !important;
        margin-top: 0 !important;
    }

    /* Sidebar header spacing with responsive fonts */
    .stSidebar .stMarkdown h1,
    .stSidebar .stMarkdown h2,
    .stSidebar .stMarkdown h3 {
        margin-top: 0 !important;
        padding-top: 0 !important;
        font-size: var(--large-font-size);
    }

    /* Remove top spacing from first sidebar element */
    .stSidebar > div > div > div:first-child {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }

    /* Sidebar specific element spacing */
    .css-1d391kg > div:first-child {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }

    /* Button styling with responsive fonts */
    .stButton > button {
        background: var(--primary-gradient);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 400;
        font-size: var(--medium-font-size);
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 188, 212, 0.4);
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 188, 212, 0.6);
    }

    /* Tab styling with responsive fonts */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: var(--card-bg);
        backdrop-filter: blur(10px);
        border-radius: 12px;
        padding: 0.5rem;
    }

    .stTabs [data-baseweb="tab"] {
        height: 3rem;
        border-radius: 8px;
        color: var(--text-secondary);
        font-weight: 400;
        font-size: var(--base-font-size);
        transition: all 0.3s ease;
    }

    .stTabs [aria-selected="true"] {
        background: var(--primary-gradient);
        color: white;
        box-shadow: 0 4px 12px rgba(0, 188, 212, 0.3);
    }

    /* Metric styling with responsive fonts */
    .stMetric {
        background: var(--card-bg);
        backdrop-filter: blur(10px);
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.2);
        transition: all 0.3s ease;
        font-size: var(--base-font-size);
    }

    .stMetric:hover {
        transform: translateY(-4px);
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
    }

    /* Info boxes with responsive fonts */
    .stInfo {
        background: linear-gradient(135deg, rgba(0, 188, 212, 0.1), rgba(63, 81, 181, 0.1));
        border-left: 4px solid var(--accent-color);
        border-radius: 8px;
        font-size: var(--base-font-size);
    }

    .stSuccess {
        background: linear-gradient(135deg, rgba(67, 233, 123, 0.1), rgba(56, 249, 215, 0.1));
        border-left: 4px solid #43e97b;
        border-radius: 8px;
        font-size: var(--base-font-size);
    }

    /* DataFrame styling */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 6px 20px rgba(0,0,0,0.1);
        font-size: var(--small-font-size);
    }

    /* Plotly chart containers */
    .js-plotly-plot .plotly .modebar {
        background: var(--card-bg);
        backdrop-filter: blur(10px);
        border-radius: 8px;
    }

    /* File uploader with responsive fonts */
    .stFileUploader {
        background: var(--card-bg);
        backdrop-filter: blur(10px);
        border-radius: 12px;
        padding: 1rem;
        border: 2px dashed var(--accent-color);
        transition: all 0.3s ease;
        font-size: var(--base-font-size);
    }

    .stFileUploader:hover {
        border-color: #3f51b5;
        background: var(--card-hover);
    }

    /* Selectbox and other inputs with responsive fonts */
    .stSelectbox > div > div {
        background: var(--card-bg);
        backdrop-filter: blur(10px);
        border-radius: 8px;
        border: 1px solid rgba(255,255,255,0.2);
        font-size: var(--base-font-size);
    }

    /* Text area with responsive fonts */
    .stTextArea textarea {
        font-size: var(--small-font-size) !important;
    }

    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }

    ::-webkit-scrollbar-track {
        background: rgba(255,255,255,0.1);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb {
        background: var(--primary-gradient);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #3f51b5, #00bcd4);
    }

    /* Modern icons and emojis enhancement with responsive sizing */
    .feature-icon {
        font-size: clamp(2rem, 3.5vw, 3rem);
        margin-bottom: 0.5rem;
        background: var(--primary-gradient);
                z-index: 1;
        position: relative;
        flex-shrink: 0;
    }

    /* Additional responsive adjustments for very small screens */
    @media (max-width: 400px) {
        .uniform-card {
    overflow-y: auto;
    scrollbar-width: thin;
            height: clamp(160px, 16vw + 120px, 200px) !important;
            padding: clamp(0.5rem, 1vw, 1rem);
        }

        :root {
            --card-value-size: clamp(0.8rem, 1.1vw + 0.3rem, 1.2rem);
            --card-title-size: clamp(0.55rem, 0.4vw + 0.2rem, 0.7rem);
            --card-subtitle-size: clamp(0.55rem, 0.5vw + 0.2rem, 0.7rem);
            --card-description-size: clamp(0.5rem, 0.4vw + 0.15rem, 0.65rem);
        }
    }

    /* Print styles with appropriate font sizes */
    @media print {
        .uniform-card h1 {
    word-break: break-word;
    white-space: normal;
    height: auto;
            font-size: 14pt !important;
        }

        .uniform-card h3 {
    word-break: break-word;
    white-space: normal;
    height: auto;
            font-size: 10pt !important;
        }

        .uniform-card h4 {
            font-size: 9pt !important;
        }

        .uniform-card p {
            font-size: 8pt !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
API_URL = "http://localhost:8000"


def display_header():
    """Display the main header with modern styling at the very top"""
    st.markdown("""
    <div class="main-header">
        <h1>🎯 Speech2Sense Analytics</h1>
        <p>✨ Unlock sentimental AI-powered insights from customer feedback and agent interactions. 
        Fast, accurate, and easy to integrate. ✨</p>
        <p>📊 Upload Text Files | 🎙️ Upload Audio Files (WAV, MP3) | 🚀 Real-time Analysis</p>
    </div>
    """, unsafe_allow_html=True)


def display_file_type_indicator(file_type):
    """Display modern file type indicator"""
    if file_type == 'audio':
        return '<span class="file-type-indicator audio-file">🎙️ AUDIO</span>'
    else:
        return '<span class="file-type-indicator text-file">📄 TEXT</span>'


def display_csat_card(csat_data):
    """Display CSAT score with consistent styling"""
    score = csat_data.get('csat_score', 0)
    rating = csat_data.get('csat_rating', 'Unknown')

    # Choose emoji based on score
    if score >= 80:
        emoji = "😄"
    elif 60 <= score < 80:
        emoji = "🙂"
    elif 40 <= score < 60:
        emoji = "😐"
    elif 20 <= score < 40:
        emoji = "🙁"
    else:
        emoji = "😠"

    st.markdown(f"""
    <div class="metric-card uniform-card">
        <div class="feature-icon">{emoji}</div>
        <h3>Customer Satisfaction</h3>
        <h1>{score}/100</h1>
        <h4>{rating}</h4>
        <p>{csat_data.get('methodology', 'N/A')}</p>
    </div>
    """, unsafe_allow_html=True)


def display_agent_performance_card(agent_data):
    """Display agent performance with consistent styling"""
    if 'error' in agent_data:
        st.error(f"🚨 Agent Performance Error: {agent_data['error']}")
        return

    score = agent_data.get('overall_score', 0)
    rating = agent_data.get('rating', 'Unknown')

    st.markdown(f"""
    <div class="metric-card uniform-card">
        <div class="feature-icon">👤</div>
        <h3>Agent Performance</h3>
        <h1>{score}/100</h1>
        <h4>{rating}</h4>
        <p>Based on {agent_data.get('total_responses', 0)} responses</p>
    </div>
    """, unsafe_allow_html=True)


def display_total_utterances_card(total_utterances):
    """Display total utterances with consistent styling"""
    st.markdown(f"""
    <div class="metric-card uniform-card">
        <div class="feature-icon">💬</div>
        <h3>Total Utterances</h3>
        <h1>{total_utterances}</h1>
        <h4>Conversations</h4>
        <p>Total number of conversation exchanges</p>
    </div>
    """, unsafe_allow_html=True)


def display_primary_topic_card(topic_data):
    """Display primary topic with consistent styling"""
    primary_topic_raw = topic_data.get('primary_topic', 'Unknown')
    primary_topic = primary_topic_raw.replace('_', ' ').title()
    confidence = topic_data.get('confidence', 0)

    st.markdown(f"""
    <div class="metric-card uniform-card">
        <div class="feature-icon">🏷️</div>
        <h3>Primary Topic</h3>
        <h1>{primary_topic}</h1>
        <h4>Confidence: {confidence:.2f}</h4>
        <p>Main conversation topic identified by AI</p>
    </div>
    """, unsafe_allow_html=True)


def create_sentiment_distribution_chart(df):
    """Create enhanced sentiment distribution chart with vibrant pastel colors"""
    sentiment_counts = df['sentiment'].value_counts()

    # Vibrant pastel colors for sentiment
    colors = {
        'extreme positive': '#FF6B9D',  # Vibrant pink
        'positive': '#45B7D1',  # Sky blue
        'neutral': '#96CEB4',  # Mint green
        'negative': '#FECA57',  # Golden yellow
        'extreme negative': '#FF9FF3'  # Light magenta
    }

    fig = px.pie(
        values=sentiment_counts.values,
        names=sentiment_counts.index,
        title="💭 Sentiment Distribution",
        color=sentiment_counts.index,
        color_discrete_map=colors
    )

    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        textfont_size=12,
        marker=dict(line=dict(color='white', width=3))
    )

    fig.update_layout(
        height=400,
        font=dict(family="Inter, sans-serif", size=12),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        title_font_size=18,
        title_font_color='#333'
    )

    return fig


def create_intent_distribution_chart(df):
    """Create intent distribution chart with vibrant pastel colors and legend"""
    intent_counts = df['intent'].value_counts()

    # Vibrant pastel colors for different intents
    intent_colors = {
        'inquiry': '#FF6B9D',  # Vibrant pink
        'complaint': '#54A0FF',  # Bright blue
        'request': '#5F27CD',  # Purple
        'compliment': '#00D2D3',  # Cyan
        'information': '#FF9FF3',  # Light magenta
        'support': '#45B7D1',  # Sky blue
        'greeting': '#96CEB4',  # Mint green
        'closing': '#FECA57'  # Golden yellow
    }

    # Get colors for the intents in the data
    colors = [intent_colors.get(intent, '#FF6B9D') for intent in intent_counts.index]

    fig = px.bar(
        x=intent_counts.index,
        y=intent_counts.values,
        title="🎯 Intent Distribution",
        color=intent_counts.index,
        color_discrete_map=intent_colors
    )

    fig.update_traces(marker_line_color='white', marker_line_width=2)

    fig.update_layout(
        xaxis_title="Intent Category",
        yaxis_title="Count",
        height=400,
        font=dict(family="Inter, sans-serif", size=12),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        title_font_size=18,
        title_font_color='#333',
        showlegend=True,  # Enable legend
        legend=dict(
            bgcolor='rgba(255,255,255,0.9)',
            bordercolor='rgba(0,0,0,0.2)',
            borderwidth=1,
            font=dict(size=10),
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        )
    )

    return fig


def create_topic_analysis_chart(topic_data):
    """Create modern topic analysis visualization"""
    topics = topic_data.get('topics', [])
    primary_topic = topic_data.get('primary_topic', 'Unknown')
    confidence = topic_data.get('confidence', 0)

    # Create a simple bar chart for topics
    fig = go.Figure(data=[
        go.Bar(
            x=topics,
            y=[1] * len(topics),
            text=[f"🎯 Primary: {topic}" if topic == primary_topic else f"📌 {topic}" for topic in topics],
            textposition='auto',
            marker_color=['#FF6B9D' if topic == primary_topic else '#45B7D1' for topic in topics],
            marker_line_color='white',
            marker_line_width=2
        )
    ])

    fig.update_layout(
        title=f"🏷️ Topic Analysis (Confidence: {confidence:.2f})",
        xaxis_title="Topics",
        yaxis_title="Relevance",
        height=300,
        font=dict(family="Inter, sans-serif", size=12),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        title_font_size=18,
        title_font_color='#333'
    )

    return fig


def create_conversation_flow_chart(df):
    """Create modern conversation flow visualization"""
    # Prepare data for conversation flow
    df_sorted = df.sort_values('utterance_id')

    fig = go.Figure()

    # Customer sentiment line with modern styling
    customer_data = df_sorted[df_sorted['speaker'] == 'Customer']
    if not customer_data.empty:
        fig.add_trace(go.Scatter(
            x=customer_data['utterance_id'],
            y=customer_data['score'],
            mode='lines+markers',
            name='👤 Customer Sentiment',
            line=dict(color='#FF6B9D', width=3, shape='spline'),
            marker=dict(size=8, line=dict(width=2, color='white'))
        ))

    # Agent sentiment line with modern styling
    agent_data = df_sorted[df_sorted['speaker'] == 'Agent']
    if not agent_data.empty:
        fig.add_trace(go.Scatter(
            x=agent_data['utterance_id'],
            y=agent_data['score'],
            mode='lines+markers',
            name='🎧 Agent Sentiment',
            line=dict(color='#45B7D1', width=3, shape='spline'),
            marker=dict(size=8, line=dict(width=2, color='white'))
        ))

    fig.update_layout(
        title="📈 Conversation Sentiment Flow",
        xaxis_title="Utterance Sequence",
        yaxis_title="Sentiment Score (0-1)",
        height=400,
        hovermode='x unified',
        font=dict(family="Inter, sans-serif", size=12),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        title_font_size=18,
        title_font_color='#333',
        legend=dict(
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='rgba(0,0,0,0.2)',
            borderwidth=1
        )
    )

    return fig


def create_detailed_metrics_table(df):
    """Create detailed metrics table"""
    # Calculate detailed metrics
    metrics = {
        'Total Utterances': len(df),
        'Unique Speakers': df['speaker'].nunique(),
        'Avg Sentiment Score': f"{df['score'].mean():.3f}",
        'Most Common Intent': df['intent'].mode().iloc[0] if not df['intent'].mode().empty else 'N/A',
        'Positive Utterances': len(df[df['sentiment'].isin(['positive', 'extreme positive'])]),
        'Negative Utterances': len(df[df['sentiment'].isin(['negative', 'extreme negative'])]),
        'High Confidence Predictions': len(df[df['sentiment_confidence'] > 0.8]),
        'Customer Utterances': len(df[df['speaker'] == 'Customer']),
        'Agent Utterances': len(df[df['speaker'] == 'Agent'])
    }

    metrics_df = pd.DataFrame(list(metrics.items()), columns=['📊 Metric', '📈 Value'])
    return metrics_df


def display_transcription_preview(transcription_text):
    """Display transcription preview with expandable functionality and matching styling"""
    st.subheader("🎙️ Audio Transcription")

    # Full transcription expandable section
    with st.expander("📝 View Full Transcription", expanded=False):
        st.text_area(
            "Transcribed Content:",
            value=transcription_text,
            height=200,
            disabled=True
        )

    # Expandable preview section with same styling
    lines = transcription_text.split('\n')
    preview_lines = lines[:5]
    preview = '\n'.join(preview_lines)
    ellipsis = '...' if len(lines) > 5 else ''

    # Initialize session state for preview expansion
    if 'preview_expanded' not in st.session_state:
        st.session_state.preview_expanded = False

    # Expandable preview section
    with st.expander("📋 Transcription Preview (first 5 lines)", expanded=False):
        st.markdown(f"""
        <div class="transcription-preview-content">
{preview}

{ellipsis}
        </div>
        """, unsafe_allow_html=True)


def display_analysis_results(data):
    """Display comprehensive analysis results with modern UI"""
    if 'error' in data:
        st.error(f"🚨 Analysis Error: {data['error']}")
        return

    utterances = data.get('utterances', [])
    if not utterances:
        st.warning("⚠️ No utterances found in the analysis results.")
        return

    df = pd.DataFrame(utterances)
    file_type = data.get('file_type', 'text')

    # File type indicator and analysis header
    file_indicator = display_file_type_indicator(file_type)
    st.markdown(f"""
    ### 📊 Analysis Results {file_indicator}
    **📁 File:** {data.get('original_filename', 'Unknown')} | **⚙️ Processing Type:** {file_type.title()}
    """, unsafe_allow_html=True)

    # Show transcription for audio files
    if file_type == 'audio' and data.get('raw_text'):
        display_transcription_preview(data.get('raw_text'))

    # Main metrics row with fixed size cards
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        display_csat_card(data.get('csat_analysis', {}))

    with col2:
        display_agent_performance_card(data.get('agent_performance', {}))

    with col3:
        display_total_utterances_card(data.get('total_utterances', 0))

    with col4:
        topic_data = data.get('topic_analysis', {})
        display_primary_topic_card(topic_data)

    # Detailed analysis tabs with modern icons
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Overview", "💬 Conversation Flow", "🏷️ Topic Analysis",
        "📈 Performance Metrics", "📋 Detailed Data", "⚙️ Processing Info"
    ])

    with tab1:
        col1, col2 = st.columns(2)

        with col1:
            st.plotly_chart(create_sentiment_distribution_chart(df), use_container_width=True)

        with col2:
            st.plotly_chart(create_intent_distribution_chart(df), use_container_width=True)

        # Summary metrics
        st.subheader("📊 Key Metrics Summary")
        metrics_df = create_detailed_metrics_table(df)

        col1, col2 = st.columns(2)
        with col1:
            st.dataframe(metrics_df.iloc[:len(metrics_df) // 2], use_container_width=True)
        with col2:
            st.dataframe(metrics_df.iloc[len(metrics_df) // 2:], use_container_width=True)

    with tab2:
        st.plotly_chart(create_conversation_flow_chart(df), use_container_width=True)

        # Conversation insights
        st.subheader("🔍 Conversation Insights")

        if len(df) > 0:
            customer_df = df[df['speaker'] == 'Customer']
            agent_df = df[df['speaker'] == 'Agent']

            col1, col2 = st.columns(2)

            with col1:
                if not customer_df.empty:
                    st.info(f"""
                    **👤 Customer Journey:**
                    - 🚀 Started with sentiment: {customer_df.iloc[0]['sentiment']}
                    - 🏁 Ended with sentiment: {customer_df.iloc[-1]['sentiment']}
                    - 📊 Average sentiment: {customer_df['score'].mean():.2f}
                    """)

            with col2:
                if not agent_df.empty:
                    st.info(f"""
                    **🎧 Agent Performance:**
                    - 📈 Maintained sentiment: {agent_df['score'].mean():.2f}
                    - 🎯 Most common intent handled: {agent_df['intent'].mode().iloc[0] if not agent_df['intent'].mode().empty else 'N/A'}
                    - 🔄 Response consistency: {agent_df['score'].std():.2f} (lower = more consistent)
                    """)

    with tab3:
        topic_data = data.get('topic_analysis', {})

        if topic_data and topic_data.get('topics'):
            st.plotly_chart(create_topic_analysis_chart(topic_data), use_container_width=True)

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("🏷️ Identified Topics")
                for topic in topic_data.get('topics', []):
                    is_primary = topic == topic_data.get('primary_topic')
                    st.write(f"{'🎯' if is_primary else '📌'} {topic.replace('_', ' ').title()}")

            with col2:
                st.subheader("🧠 AI Reasoning")
                st.write(topic_data.get('reasoning', 'No reasoning provided'))

                st.metric(
                    "🎯 Topic Detection Confidence",
                    f"{topic_data.get('confidence', 0):.2%}",
                    help="AI confidence in topic classification"
                )
        else:
            st.warning("⚠️ No topic analysis data available.")

    with tab4:
        agent_perf = data.get('agent_performance', {})

        if 'error' not in agent_perf:
            # Agent performance breakdown
            st.subheader("👨‍💼 Agent Performance Breakdown")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "🎯 Sentiment Consistency",
                    f"{agent_perf.get('agent_sentiment_avg', 0):.2f}",
                    help="Average sentiment score of agent responses"
                )

            with col2:
                st.metric(
                    "💼 Professionalism Score",
                    f"{agent_perf.get('professionalism_score', 0):.1f}%",
                    help="Percentage of responses containing professional language"
                )

            with col3:
                st.metric(
                    "📈 Customer Improvement",
                    f"{agent_perf.get('customer_sentiment_improvement', 0):+.1f}%",
                    help="Change in customer sentiment throughout conversation"
                )

            # Performance visualization with modern colors
            perf_metrics = {
                'Overall Score': agent_perf.get('overall_score', 0),
                'Sentiment Avg': agent_perf.get('agent_sentiment_avg', 0) * 100,
                'Professionalism': agent_perf.get('professionalism_score', 0),
                'Customer Impact': max(0, 50 + agent_perf.get('customer_sentiment_improvement', 0))
            }

            fig = go.Figure(data=go.Scatterpolar(
                r=list(perf_metrics.values()),
                theta=list(perf_metrics.keys()),
                fill='toself',
                name='Agent Performance',
                line_color='#FF6B9D',
                fillcolor='rgba(255, 107, 157, 0.3)'
            ))

            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100],
                        gridcolor='rgba(255, 107, 157, 0.3)'
                    ),
                    angularaxis=dict(
                        gridcolor='rgba(255, 107, 157, 0.3)'
                    )
                ),
                showlegend=False,
                title="🎯 Agent Performance Radar",
                height=400,
                font=dict(family="Inter, sans-serif", size=12),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                title_font_size=18,
                title_font_color='#333'
            )

            st.plotly_chart(fig, use_container_width=True)

        # CSAT breakdown
        csat_data = data.get('csat_analysis', {})
        if csat_data:
            st.subheader("😊 Customer Satisfaction Analysis")

            col1, col2 = st.columns(2)

            with col1:
                st.info(f"""
                **📊 CSAT Score:** {csat_data.get('csat_score', 0)}/100

                **⭐ Rating:** {csat_data.get('csat_rating', 'Unknown')}

                **🔬 Methodology:** {csat_data.get('methodology', 'N/A')}
                """)

            with col2:
                # CSAT score gauge with modern styling
                fig = go.Figure(go.Indicator(
                    mode="gauge+number+delta",
                    value=csat_data.get('csat_score', 0),
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "CSAT Score"},
                    delta={'reference': 70, 'increasing': {'color': "#96CEB4"}},
                    gauge={
                        'axis': {'range': [None, 100]},
                        'bar': {'color': "#FF6B9D"},
                        'steps': [
                            {'range': [0, 40], 'color': "rgba(255, 159, 243, 0.3)"},
                            {'range': [40, 70], 'color': "rgba(254, 202, 87, 0.3)"},
                            {'range': [70, 100], 'color': "rgba(150, 206, 180, 0.3)"}
                        ],
                        'threshold': {
                            'line': {'color': "#45B7D1", 'width': 4},
                            'thickness': 0.75,
                            'value': 80
                        }
                    }
                ))

                fig.update_layout(
                    height=300,
                    font=dict(family="Inter, sans-serif", size=12),
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig, use_container_width=True)

    with tab5:
        st.subheader("📋 Detailed Utterance Analysis")

        # Add filters with modern styling
        col1, col2, col3 = st.columns(3)

        with col1:
            speaker_filter = st.selectbox(
                "🎭 Filter by Speaker",
                options=["All"] + list(df['speaker'].unique())
            )

        with col2:
            sentiment_filter = st.selectbox(
                "💭 Filter by Sentiment",
                options=["All"] + list(df['sentiment'].unique())
            )

        with col3:
            intent_filter = st.selectbox(
                "🎯 Filter by Intent",
                options=["All"] + list(df['intent'].unique())
            )

        # Apply filters
        filtered_df = df.copy()

        if speaker_filter != "All":
            filtered_df = filtered_df[filtered_df['speaker'] == speaker_filter]

        if sentiment_filter != "All":
            filtered_df = filtered_df[filtered_df['sentiment'] == sentiment_filter]

        if intent_filter != "All":
            filtered_df = filtered_df[filtered_df['intent'] == intent_filter]

        # Display filtered data
        display_columns = ['utterance_id', 'speaker', 'sentence', 'sentiment', 'score',
                           'intent', 'sentiment_confidence', 'intent_confidence']

        if not filtered_df.empty:
            st.dataframe(
                filtered_df[display_columns],
                use_container_width=True,
                height=400
            )

            # Export functionality
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Filtered Data as CSV",
                data=csv,
                file_name=f"conversation_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.warning("⚠️ No data matches the selected filters.")

    with tab6:
        st.subheader("⚙️ Processing Information")

        col1, col2 = st.columns(2)

        with col1:
            st.info(f"""
            **📁 File Processing Details:**
            - **📄 Original Filename:** {data.get('original_filename', 'Unknown')}
            - **🔧 File Type:** {file_type.title()}
            - **⚙️ Processing Method:** {'🎙️ Audio Transcription + Diarization' if file_type == 'audio' else '📝 Text Parsing'}
            - **🔖 Analysis Version:** {data.get('analysis_version', '2.1.0')}
            - **⏰ Processing Time:** {data.get('analysis_timestamp', 'Unknown')}
            """)

        with col2:
            if file_type == 'audio':
                st.success("""
                **🎙️ Audio Processing Pipeline:**
                1. 🎵 Audio file upload
                2. 🔄 Format conversion (if needed)
                3. 🎙️ Speech-to-text transcription
                4. 👥 Speaker diarization
                5. 🔗 Transcript-speaker alignment
                6. 🏷️ Role mapping (Agent/Customer)
                7. 🧠 AI sentiment & intent analysis
                """)
            else:
                st.success("""
                **📝 Text Processing Pipeline:**
                1. 📁 Text file upload
                2. 📝 Format validation
                3. 🧹 Text preprocessing
                4. 👥 Speaker extraction
                5. 🧠 AI sentiment & intent analysis
                6. 📊 Performance metrics calculation
                """)

        # Raw data preview
        if st.checkbox("🔍 Show Raw Analysis Data", help="Display the complete analysis JSON"):
            with st.expander("📋 Raw Analysis JSON", expanded=False):
                st.json(data)


def check_api_health():
    """Check if the API is healthy"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            return True, health_data.get('supported_formats', [])
        return False, []
    except:
        return False, []


def transcribe_audio_only(uploaded_file):
    """Transcribe audio file without full analysis"""
    try:
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}

        response = requests.post(
            f"{API_URL}/transcribe/",
            files=files,
            timeout=120
        )

        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                return result.get('transcription', ''), None
            else:
                return None, "Transcription failed"
        else:
            error_detail = response.json().get('detail', 'Unknown error')
            return None, f"Transcription error: {error_detail}"

    except requests.exceptions.Timeout:
        return None, "Transcription timed out. File might be too large."
    except requests.exceptions.ConnectionError:
        return None, "Connection error. Please ensure API server is running."
    except Exception as e:
        return None, f"Unexpected error: {str(e)}"


# Main application
def main():
    # Display header at the very top
    display_header()

    # API health check
    api_healthy, supported_formats = check_api_health()

    if not api_healthy:
        st.error("""
        🚨 **API Connection Error**

        The Speech2Sense API is not responding. Please ensure:
        1. 🖥️ The API server is running on localhost:8000
        2. ▶️ Run: `python main.py` or `uvicorn main:app --host 0.0.0.0 --port 8000`
        3. 📋 Check the API logs for errors
        """)
        st.stop()

    # Display supported formats
    if supported_formats:
        st.success(f"✅ API Connected")

    # Sidebar configuration with modern styling
    with st.sidebar:
        st.header("📁 File Upload")

        # File type selection
        file_type_option = st.radio(
            "🎯 Choose File Type:",
            options=["📄 Text File (.txt)", "🎙️ Audio File (.wav, .mp3)"],
            help="Select whether you want to upload a text conversation or audio recording"
        )

        is_audio_upload = "🎙️ Audio" in file_type_option

        if is_audio_upload:
            uploaded_file = st.file_uploader(
                "🎙️ Choose an audio file",
                type=['wav', 'mp3'],
                help="Upload an audio recording of a conversation between Agent and Customer"
            )

            # Audio-specific options
            st.subheader("🎙️ Audio Processing Options")

            transcribe_only = st.checkbox(
                "📝 Transcribe Only",
                help="Only transcribe audio to text without full analysis"
            )

            if transcribe_only:
                st.info("💡 Transcription will show the conversation text without sentiment analysis")

        else:
            uploaded_file = st.file_uploader(
                "📄 Choose a conversation file",
                type=['txt'],
                help="Upload a .txt file with conversation in 'Speaker: Message' format"
            )

        # Domain selection (for analysis)
        if not (is_audio_upload and transcribe_only):
            st.subheader("🏷️ Analysis Configuration")
            domain = st.selectbox(
                "🎯 Select Domain",
                options=["general", "ecommerce", "healthcare", "real_estate", "customer_support", "technical_support"],
                help="Choose the domain for specialized analysis"
            )

            st.subheader("⚙️ Analysis Settings")
            show_confidence = st.checkbox("📊 Show Confidence Scores", value=True)
            show_keywords = st.checkbox("🔍 Show Sentiment Keywords", value=False)
            show_reasoning = st.checkbox("🧠 Show AI Reasoning", value=False)

        st.subheader("📊 Export Options")
        export_format = st.selectbox(
            "💾 Export Format",
            options=["CSV", "JSON", "Excel"],
            help="Choose format for data export"
        )

        # Processing info
        if is_audio_upload:
            st.subheader("ℹ️ Audio Processing Info")
            st.info("""
            **🎙️ Audio Processing:**
            - 🎵 Supports WAV or MP3 formats
            - 👥 Automatic speaker diarization
            - 🤖 AI-powered role mapping
            - 📝 Speech-to-text transcription
            - ⏱️ Processing time: 30s-5min depending on file size
            """)

    # Main content area
    if uploaded_file:

        # Handle transcription-only for audio files
        if is_audio_upload and transcribe_only:
            if st.button("🎙️ Transcribe Audio", type="primary"):
                with st.spinner("🎵 Transcribing your audio file..."):
                    transcription, error = transcribe_audio_only(uploaded_file)

                    if transcription:
                        st.success("✅ Transcription completed successfully!")

                        # Display transcription
                        st.subheader("📝 Audio Transcription")
                        st.text_area(
                            "Transcribed Content:",
                            value=transcription,
                            height=300,
                            help="Copy this text to analyze separately or save for later use"
                        )

                        # Download transcription
                        st.download_button(
                            label="📥 Download Transcription",
                            data=transcription,
                            file_name=f"transcription_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                            mime="text/plain"
                        )

                        # Option to analyze transcription
                        if st.button("🔍 Analyze This Transcription"):
                            st.session_state['transcription_to_analyze'] = transcription
                            st.rerun()

                    else:
                        st.error(f"❌ Transcription failed: {error}")

        # Handle full analysis
        else:
            # Check if we have transcription to analyze
            analyze_transcription = st.session_state.get('transcription_to_analyze', None)

            if analyze_transcription:
                if st.button("🔍 Analyze Transcription", type="primary"):
                    with st.spinner("🤖 AI is analyzing the transcription..."):
                        try:
                            # Create a temporary text file from transcription
                            temp_file_content = analyze_transcription.encode('utf-8')
                            files = {"file": ("transcription.txt", temp_file_content, "text/plain")}
                            data = {"domain": domain}

                            # Make API request
                            response = requests.post(
                                f"{API_URL}/analyze/",
                                files=files,
                                data=data,
                                timeout=360
                            )

                            if response.status_code == 200:
                                result = response.json()
                                if result.get('status') == 'success':
                                    st.success("✅ Analysis completed successfully!")
                                    st.session_state['analysis_results'] = result.get('data')
                                    st.session_state['analysis_timestamp'] = datetime.now()
                                    # Clear the transcription from session state
                                    del st.session_state['transcription_to_analyze']
                                else:
                                    st.error("❌ Analysis failed.")
                            else:
                                error_detail = response.json().get('detail', 'Unknown error')
                                st.error(f"❌ Analysis Error: {error_detail}")

                        except Exception as e:
                            st.error(f"❌ Unexpected error: {str(e)}")

            # Regular file analysis
            elif st.button("🔍 Analyze " + ("Audio" if is_audio_upload else " Conversation"), type="primary"):

                processing_message = "🎵 AI is processing and analyzing your audio file..." if is_audio_upload else "🤖 AI is analyzing your conversation..."

                with st.spinner(processing_message):
                    try:
                        # Prepare files and data for API call
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                        data = {"domain": domain}

                        # Make API request with longer timeout for audio files
                        timeout = 480 if is_audio_upload else 60
                        response = requests.post(
                            f"{API_URL}/analyze/",
                            files=files,
                            data=data,
                            timeout=timeout
                        )

                        if response.status_code == 200:
                            result = response.json()

                            if result.get('status') == 'success':
                                st.success("✅ Analysis completed successfully!")

                                # Store results in session state
                                st.session_state['analysis_results'] = result.get('data')
                                st.session_state['analysis_timestamp'] = datetime.now()

                            else:
                                st.error("❌ Analysis failed. Please check your file format.")

                        elif response.status_code == 400:
                            error_detail = response.json().get('detail', 'Unknown error')
                            st.error(f"❌ Bad Request: {error_detail}")

                        elif response.status_code == 500:
                            error_detail = response.json().get('detail', 'Internal server error')
                            st.error(f"❌ Server Error: {error_detail}")

                        else:
                            st.error(f"❌ Unexpected error: HTTP {response.status_code}")

                    except requests.exceptions.Timeout:
                        timeout_msg = "⏱️ Audio processing timed out. The file might be too large." if is_audio_upload else "⏱️ Request timed out."
                        st.error(timeout_msg)

                    except requests.exceptions.ConnectionError:
                        st.error("🔌 Connection error. Please ensure the API server is running.")

                    except Exception as e:
                        st.error(f"❌ Unexpected error: {str(e)}")

    # Display results if available
    if 'analysis_results' in st.session_state:
        st.markdown("---")

        # Results header
        timestamp = st.session_state.get('analysis_timestamp', datetime.now())
        st.subheader(f"📈 Analysis Generated On: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")

        # Display the comprehensive analysis
        display_analysis_results(st.session_state['analysis_results'])

    else:
        # Show sample data/instructions when no file is uploaded
        st.markdown("---")
        st.subheader("📖 Getting Started")

        col1, col2 = st.columns(2)

        with col1:
            st.info("""
            **📄 Text File Format:**

            Upload a .txt file with conversations:
            ```
            Customer: I'm having trouble with my order
            Agent: I'd be happy to help you with that
            Customer: Thank you, I appreciate it
            ```

            **🎙️ Audio File Support:**
            - 🎵 Upload WAV or MP3 files
            - 🤖 Automatic speech-to-text transcription
            - 👥 Speaker diarization (Agent/Customer)
            - 📞 Works with phone calls, meetings, interviews

            **✅ Supported Features:**
            - 👥 Multi-speaker conversations
            - 💭 Sentiment analysis (5 levels)
            - 🎯 Intent detection (6 categories)
            - 🏷️ Topic classification
            - 😊 CSAT scoring
            - 📈 Agent performance metrics
            """)

        with col2:
            st.success("""
            **🎯 What You'll Get:**

            - **⚡ Real-time Analysis**: AI-powered insights
            - **😊 CSAT Scores**: Customer satisfaction metrics
            - **👨‍💼 Agent Performance**: Comprehensive evaluation
            - **🏷️ Topic Detection**: Automatic categorization
            - **📊 Visual Analytics**: Interactive charts
            - **💾 Export Options**: CSV, JSON, Excel formats
            - **🎙️ Audio Processing**: Speech-to-text + analysis

            **🚀 Powered by:**
            - 🤖 Groq LLaMA 3 AI Models
            - 🎙️ Whisper Speech Recognition
            - 👥 PyAnnote Speaker Diarization
            - 🧠 Advanced NLP Processing
            - ⚡ Real-time Analytics Engine
            """)

        # Audio processing demo
        st.markdown("---")
        st.subheader("🎙️ Audio Processing Demo")

        col1, col2 = st.columns(2)

        with col1:
            st.info("""
            **🎙️ Audio Processing Pipeline:**

            1. **📤 Upload** - WAV, MP3 files
            2. **🔄 Convert** - Standardize audio format
            3. **📝 Transcribe** - Speech-to-text using Whisper
            4. **👥 Diarize** - Identify different speakers
            5. **🔗 Align** - Match text with speakers
            6. **🏷️ Map** - Assign Agent/Customer roles
            7. **🧠 Analyze** - Sentiment & intent analysis
            8. **📊 Report** - Generate comprehensive insights
            """)

        with col2:
            st.warning("""
            **🎙️ Audio File Requirements:**

            - **📁 Format**: WAV, MP3
            - **🎤 Quality**: Clear speech, minimal background noise
            - **⏱️ Duration**: Up to 60 minutes recommended
            - **👥 Speakers**: 2-3 speakers work best
            - **🌍 Language**: English (primary support)
            - **📊 File Size**: Up to 100MB

            **💡 Tips for Best Results:**
            - 🎧 Use headset/microphone recordings
            - 🚫 Avoid overlapping speech
            - ✅ Ensure clear audio quality
            """)

        # Sample files section
        st.markdown("---")
        st.subheader("📋 Sample Files")

        # Create sample text file
        sample_conversation = """Customer: Hi, I'm calling about my recent order. I haven't received it yet and it's been over a week.
Agent: I'm sorry to hear about the delay with your order. Let me look into this for you right away. Can you please provide me with your order number?
Customer: Yes, it's ORDER-12345. I placed it last Monday and was told it would arrive within 3-5 business days.
Agent: Thank you for providing that information. I can see your order here in our system. It looks like there was a delay at our distribution center. I sincerely apologize for this inconvenience.
Customer: This is really frustrating. I needed these items for an event this weekend.
Agent: I completely understand your frustration, and I want to make this right for you. Let me see what options we have. I can expedite your shipment at no extra cost and provide you with tracking information.
Customer: That would be helpful. When can I expect to receive it?
Agent: With expedited shipping, you should receive your order by tomorrow afternoon. I'm also applying a 20% discount to your account for the inconvenience caused.
Customer: Thank you, I appreciate you taking care of this so quickly.
Agent: You're very welcome! Is there anything else I can help you with today?
Customer: No, that covers everything. Thank you for your help.
Agent: My pleasure! Have a great day and thank you for your patience."""

        col1, col2 = st.columns(2)

        with col1:
            st.download_button(
                label="📥 Download Sample Text File",
                data=sample_conversation,
                file_name="sample_conversation.txt",
                mime="text/plain",
                help="Download a sample conversation file to test the system"
            )

        with col2:
            st.info("""
            **📋 Sample File Contains:**
            - 🛒 Customer service interaction
            - 💭 Multiple sentiment shifts
            - 🔧 Problem resolution scenario
            - 👨‍💼 Agent performance examples
            - 🎯 Various intent categories
            """)


if __name__ == "__main__":
    main()