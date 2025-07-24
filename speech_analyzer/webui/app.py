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
    page_title="Speech2Sense Analytics Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    .file-type-indicator {
        padding: 0.25rem 0.75rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
        margin-left: 0.5rem;
    }
    .audio-file {
        background-color: #e3f2fd;
        color: #1976d2;
    }
    .text-file {
        background-color: #f3e5f5;
        color: #7b1fa2;
    }
    .csat-excellent { background-color: #00ff00; color: black; }
    .csat-good { background-color: #7CFC00; color: black; }
    .csat-satisfactory { background-color: #FFD700; color: black; }
    .csat-poor { background-color: #FFA500; color: black; }
    .csat-very-poor { background-color: #FF0000; color: white; }
    .agent-excellent { background-color: #00ff00; color: black; }
    .agent-good { background-color: #7CFC00; color: black; }
    .agent-satisfactory { background-color: #FFD700; color: black; }
    .agent-needs-improvement { background-color: #FFA500; color: black; }
    .agent-poor { background-color: #FF0000; color: white; }
    .st-emotion-cache-q3uqly:hover{ background: #0d99ff; border-color: #0d99ff;}
    .st-emotion-cache-q3uqly{background: #0d68aa; border-color: #0d68aa;}
</style>
""", unsafe_allow_html=True)

# API Configuration
API_URL = "http://localhost:8000"


def display_header():
    """Display the main header"""
    st.markdown("""
    <div class="main-header">
        <h1>🎯 Speech2Sense Analytics Dashboard</h1>
        <p>Advanced Conversation Analytics with AI-Powered Insights</p>
        <p>📁 Upload Text Files | 🎵 Upload Audio Files (WAV, MP3, MP4)</p>
    </div>
    """, unsafe_allow_html=True)


def display_file_type_indicator(file_type):
    """Display file type indicator"""
    if file_type == 'audio':
        return '<span class="file-type-indicator audio-file">🎵 AUDIO</span>'
    else:
        return '<span class="file-type-indicator text-file">📁 TEXT</span>'


def display_csat_card(csat_data):
    """Display CSAT score with color coding"""
    score = csat_data.get('csat_score', 0)
    rating = csat_data.get('csat_rating', 'Unknown')

    css_class = {
        'Excellent': 'csat-excellent',
        'Good': 'csat-good',
        'Satisfactory': 'csat-satisfactory',
        'Poor': 'csat-poor',
        'Very Poor': 'csat-very-poor'
    }.get(rating, 'csat-satisfactory')

    st.markdown(f"""
    <div class="metric-card {css_class}">
        <h3>Customer Satisfaction (CSAT)</h3>
        <h1>{score}/100</h1>
        <h4>{rating}</h4>
        <p>{csat_data.get('methodology', 'N/A')}</p>
    </div>
    """, unsafe_allow_html=True)


def display_agent_performance_card(agent_data):
    """Display agent performance with color coding"""
    if 'error' in agent_data:
        st.error(f"Agent Performance Error: {agent_data['error']}")
        return

    score = agent_data.get('overall_score', 0)
    rating = agent_data.get('rating', 'Unknown')

    css_class = {
        'Excellent': 'agent-excellent',
        'Good': 'agent-good',
        'Satisfactory': 'agent-satisfactory',
        'Needs Improvement': 'agent-needs-improvement',
        'Poor': 'agent-poor'
    }.get(rating, 'agent-satisfactory')

    st.markdown(f"""
    <div class="metric-card {css_class}">
        <h3>Agent Performance</h3>
        <h1>{score}/100</h1>
        <h4>{rating}</h4>
        <p>Based on {agent_data.get('total_responses', 0)} responses</p>
    </div>
    """, unsafe_allow_html=True)


def create_sentiment_distribution_chart(df):
    """Create enhanced sentiment distribution chart"""
    sentiment_counts = df['sentiment'].value_counts()

    colors = {
        'extreme positive': '#00ff00',
        'positive': '#7CFC00',
        'neutral': '#FFD700',
        'negative': '#FFA500',
        'extreme negative': '#FF0000'
    }

    fig = px.pie(
        values=sentiment_counts.values,
        names=sentiment_counts.index,
        title="Sentiment Distribution",
        color=sentiment_counts.index,
        color_discrete_map=colors
    )

    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=400)

    return fig


def create_intent_distribution_chart(df):
    """Create intent distribution chart"""
    intent_counts = df['intent'].value_counts()

    fig = px.bar(
        x=intent_counts.index,
        y=intent_counts.values,
        title="Intent Distribution",
        color=intent_counts.values,
        color_continuous_scale="viridis"
    )

    fig.update_layout(
        xaxis_title="Intent Category",
        yaxis_title="Count",
        height=400
    )

    return fig


def create_topic_analysis_chart(topic_data):
    """Create topic analysis visualization"""
    topics = topic_data.get('topics', [])
    primary_topic = topic_data.get('primary_topic', 'Unknown')
    confidence = topic_data.get('confidence', 0)

    # Create a simple bar chart for topics
    fig = go.Figure(data=[
        go.Bar(
            x=topics,
            y=[1] * len(topics),
            text=[f"Primary: {topic}" if topic == primary_topic else topic for topic in topics],
            textposition='auto',
            marker_color=['#FF6B6B' if topic == primary_topic else '#4ECDC4' for topic in topics]
        )
    ])

    fig.update_layout(
        title=f"Topic Analysis (Confidence: {confidence:.2f})",
        xaxis_title="Topics",
        yaxis_title="Relevance",
        height=300
    )

    return fig


def create_conversation_flow_chart(df):
    """Create conversation flow visualization"""
    # Prepare data for conversation flow
    df_sorted = df.sort_values('utterance_id')

    fig = go.Figure()

    # Customer sentiment line
    customer_data = df_sorted[df_sorted['speaker'] == 'Customer']
    if not customer_data.empty:
        fig.add_trace(go.Scatter(
            x=customer_data['utterance_id'],
            y=customer_data['score'],
            mode='lines+markers',
            name='Customer Sentiment',
            line=dict(color='#FF6B6B', width=3),
            marker=dict(size=8)
        ))

    # Agent sentiment line
    agent_data = df_sorted[df_sorted['speaker'] == 'Agent']
    if not agent_data.empty:
        fig.add_trace(go.Scatter(
            x=agent_data['utterance_id'],
            y=agent_data['score'],
            mode='lines+markers',
            name='Agent Sentiment',
            line=dict(color='#4ECDC4', width=3),
            marker=dict(size=8)
        ))

    fig.update_layout(
        title="Conversation Sentiment Flow",
        xaxis_title="Utterance Sequence",
        yaxis_title="Sentiment Score (0-1)",
        height=400,
        hovermode='x unified'
    )

    return fig


def create_detailed_metrics_table(df):
    """Create detailed metrics table"""
    # Calculate detailed metrics
    metrics = {
        'Total Utterances': len(df),
        'Unique Speakers': df['speaker'].nunique(),
        'Avg Sentiment Score': df['score'].mean(),
        'Most Common Intent': df['intent'].mode().iloc[0] if not df['intent'].mode().empty else 'N/A',
        'Positive Utterances': len(df[df['sentiment'].isin(['positive', 'extreme positive'])]),
        'Negative Utterances': len(df[df['sentiment'].isin(['negative', 'extreme negative'])]),
        'High Confidence Predictions': len(df[df['sentiment_confidence'] > 0.8]),
        'Customer Utterances': len(df[df['speaker'] == 'Customer']),
        'Agent Utterances': len(df[df['speaker'] == 'Agent'])
    }

    metrics_df = pd.DataFrame(list(metrics.items()), columns=['Metric', 'Value'])
    return metrics_df


def display_transcription_preview(transcription_text):
    """Display transcription preview with formatting"""
    st.subheader("🎵 Audio Transcription")

    # Create expandable transcription view
    with st.expander("📝 View Full Transcription", expanded=False):
        st.text_area(
            "Transcribed Content:",
            value=transcription_text,
            height=200,
            disabled=True
        )

    # Show first few lines as preview
    lines = transcription_text.split('\n')[:5]
    preview = '\n'.join(lines)

    ellipsis = '...' if len(transcription_text.split('\n')) > 5 else ''

    st.info(f"""
        **Transcription Preview (first 5 lines):**

        {preview}

        {ellipsis}
        """)


def display_analysis_results(data):
    """Display comprehensive analysis results"""
    if 'error' in data:
        st.error(f"Analysis Error: {data['error']}")
        return

    utterances = data.get('utterances', [])
    if not utterances:
        st.warning("No utterances found in the analysis results.")
        return

    df = pd.DataFrame(utterances)
    file_type = data.get('file_type', 'text')

    # File type indicator and analysis header
    file_indicator = display_file_type_indicator(file_type)
    st.markdown(f"""
    ### 📊 Analysis Results {file_indicator}
    **File:** {data.get('original_filename', 'Unknown')} | **Processing Type:** {file_type.title()}
    """, unsafe_allow_html=True)

    # Show transcription for audio files
    if file_type == 'audio' and data.get('raw_text'):
        display_transcription_preview(data.get('raw_text'))

    # Main metrics row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        display_csat_card(data.get('csat_analysis', {}))

    with col2:
        display_agent_performance_card(data.get('agent_performance', {}))

    with col3:
        st.metric(
            "Total Utterances",
            data.get('total_utterances', 0),
            help="Total number of conversation exchanges"
        )

    with col4:
        topic_data = data.get('topic_analysis', {})
        st.metric(
            "Primary Topic",
            topic_data.get('primary_topic', 'Unknown'),
            f"Confidence: {topic_data.get('confidence', 0):.2f}",
            help="Main conversation topic identified by AI"
        )

    # Detailed analysis tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Overview", "💬 Conversation Flow", "🎯 Topic Analysis",
        "📈 Performance Metrics", "📋 Detailed Data", "🔧 Processing Info"
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
                    **Customer Journey:**
                    - Started with sentiment: {customer_df.iloc[0]['sentiment']}
                    - Ended with sentiment: {customer_df.iloc[-1]['sentiment']}
                    - Average sentiment: {customer_df['score'].mean():.2f}
                    """)

            with col2:
                if not agent_df.empty:
                    st.info(f"""
                    **Agent Performance:**
                    - Maintained sentiment: {agent_df['score'].mean():.2f}
                    - Most common intent handled: {agent_df['intent'].mode().iloc[0] if not agent_df['intent'].mode().empty else 'N/A'}
                    - Response consistency: {agent_df['score'].std():.2f} (lower = more consistent)
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
                    st.write(f"{'🔥' if is_primary else '•'} {topic.replace('_', ' ').title()}")

            with col2:
                st.subheader("🧠 AI Reasoning")
                st.write(topic_data.get('reasoning', 'No reasoning provided'))

                st.metric(
                    "Topic Detection Confidence",
                    f"{topic_data.get('confidence', 0):.2%}",
                    help="AI confidence in topic classification"
                )
        else:
            st.warning("No topic analysis data available.")

    with tab4:
        agent_perf = data.get('agent_performance', {})

        if 'error' not in agent_perf:
            # Agent performance breakdown
            st.subheader("👨‍💼 Agent Performance Breakdown")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Sentiment Consistency",
                    f"{agent_perf.get('agent_sentiment_avg', 0):.2f}",
                    help="Average sentiment score of agent responses"
                )

            with col2:
                st.metric(
                    "Professionalism Score",
                    f"{agent_perf.get('professionalism_score', 0):.1f}%",
                    help="Percentage of responses containing professional language"
                )

            with col3:
                st.metric(
                    "Customer Improvement",
                    f"{agent_perf.get('customer_sentiment_improvement', 0):+.1f}%",
                    help="Change in customer sentiment throughout conversation"
                )

            # Performance visualization
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
                name='Agent Performance'
            ))

            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100]
                    )),
                showlegend=False,
                title="Agent Performance Radar",
                height=400
            )

            st.plotly_chart(fig, use_container_width=True)

        # CSAT breakdown
        csat_data = data.get('csat_analysis', {})
        if csat_data:
            st.subheader("😊 Customer Satisfaction Analysis")

            col1, col2 = st.columns(2)

            with col1:
                st.info(f"""
                **CSAT Score:** {csat_data.get('csat_score', 0)}/100

                **Rating:** {csat_data.get('csat_rating', 'Unknown')}

                **Methodology:** {csat_data.get('methodology', 'N/A')}
                """)

            with col2:
                # CSAT score gauge
                fig = go.Figure(go.Indicator(
                    mode="gauge+number+delta",
                    value=csat_data.get('csat_score', 0),
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "CSAT Score"},
                    delta={'reference': 70, 'increasing': {'color': "green"}},
                    gauge={
                        'axis': {'range': [None, 100]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [0, 40], 'color': "lightgray"},
                            {'range': [40, 70], 'color': "gray"},
                            {'range': [70, 100], 'color': "lightgreen"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 80
                        }
                    }
                ))

                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)

    with tab5:
        st.subheader("📋 Detailed Utterance Analysis")

        # Add filters
        col1, col2, col3 = st.columns(3)

        with col1:
            speaker_filter = st.selectbox(
                "Filter by Speaker",
                options=["All"] + list(df['speaker'].unique())
            )

        with col2:
            sentiment_filter = st.selectbox(
                "Filter by Sentiment",
                options=["All"] + list(df['sentiment'].unique())
            )

        with col3:
            intent_filter = st.selectbox(
                "Filter by Intent",
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
            st.warning("No data matches the selected filters.")

    with tab6:
        st.subheader("🔧 Processing Information")

        col1, col2 = st.columns(2)

        with col1:
            st.info(f"""
            **File Processing Details:**
            - **Original Filename:** {data.get('original_filename', 'Unknown')}
            - **File Type:** {file_type.title()}
            - **Processing Method:** {'Audio Transcription + Diarization' if file_type == 'audio' else 'Text Parsing'}
            - **Analysis Version:** {data.get('analysis_version', '2.1.0')}
            - **Processing Time:** {data.get('analysis_timestamp', 'Unknown')}
            """)

        with col2:
            if file_type == 'audio':
                st.success("""
                **Audio Processing Pipeline:**
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
                **Text Processing Pipeline:**
                1. 📁 Text file upload
                2. 📝 Format validation
                3. 🧹 Text preprocessing
                4. 👥 Speaker extraction
                5. 🧠 AI sentiment & intent analysis
                6. 📊 Performance metrics calculation
                """)

        # Raw data preview
        if st.checkbox("Show Raw Analysis Data", help="Display the complete analysis JSON"):
            with st.expander("Raw Analysis JSON", expanded=False):
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
    display_header()

    # API health check
    api_healthy, supported_formats = check_api_health()

    if not api_healthy:
        st.error("""
        🚨 **API Connection Error**

        The Speech2Sense API is not responding. Please ensure:
        1. The API server is running on localhost:8000
        2. Run: `python main.py` or `uvicorn main:app --host 0.0.0.0 --port 8000`
        3. Check the API logs for errors
        """)
        st.stop()

    # Display supported formats
    if supported_formats:
        st.success(f"✅ API Connected | Supported formats: {', '.join(supported_formats)}")

    # Sidebar configuration
    with st.sidebar:
        st.header("📁 File Upload")

        # File type selection
        file_type_option = st.radio(
            "Choose File Type:",
            options=["📁 Text File (.txt)", "🎵 Audio File (.wav, .mp3, .mp4)"],
            help="Select whether you want to upload a text conversation or audio recording"
        )

        is_audio_upload = "🎵 Audio" in file_type_option

        if is_audio_upload:
            uploaded_file = st.file_uploader(
                "Choose an audio file",
                type=['wav', 'mp3', 'mp4', 'm4a'],
                help="Upload an audio recording of a conversation between Agent and Customer"
            )

            # Audio-specific options
            st.subheader("🎵 Audio Processing Options")

            transcribe_only = st.checkbox(
                "Transcribe Only",
                help="Only transcribe audio to text without full analysis"
            )

            if transcribe_only:
                st.info("💡 Transcription will show the conversation text without sentiment analysis")

        else:
            uploaded_file = st.file_uploader(
                "Choose a conversation file",
                type=['txt'],
                help="Upload a .txt file with conversation in 'Speaker: Message' format"
            )

        # Domain selection (for analysis)
        if not (is_audio_upload and transcribe_only):
            st.subheader("🏷️ Analysis Configuration")
            domain = st.selectbox(
                "Select Domain",
                options=["general", "ecommerce", "healthcare", "real_estate", "customer_support", "technical_support"],
                help="Choose the domain for specialized analysis"
            )

            st.subheader("⚙️ Analysis Settings")
            show_confidence = st.checkbox("Show Confidence Scores", value=True)
            show_keywords = st.checkbox("Show Sentiment Keywords", value=False)
            show_reasoning = st.checkbox("Show AI Reasoning", value=False)

        st.subheader("📊 Export Options")
        export_format = st.selectbox(
            "Export Format",
            options=["CSV", "JSON", "Excel"],
            help="Choose format for data export"
        )

        # Processing info
        if is_audio_upload:
            st.subheader("ℹ️ Audio Processing Info")
            st.info("""
            **Audio Processing:**
            - Supports WAV, MP3, MP4 formats
            - Automatic speaker diarization
            - AI-powered role mapping
            - Speech-to-text transcription
            - Processing time: 30s-2min depending on file size
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
                                timeout=60
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
            elif st.button("🔍 Analyze " + ("Audio" if is_audio_upload else "Conversation"), type="primary"):

                processing_message = "🎵 Processing your audio file..." if is_audio_upload else "🤖 AI is analyzing your conversation..."

                with st.spinner(processing_message):
                    try:
                        # Prepare files and data for API call
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                        data = {"domain": domain}

                        # Make API request with longer timeout for audio files
                        timeout = 120 if is_audio_upload else 60
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
                        timeout_msg = "Audio processing timed out. The file might be too large." if is_audio_upload else "Request timed out."
                        st.error(f"⏱️ {timeout_msg}")

                    except requests.exceptions.ConnectionError:
                        st.error("🔌 Connection error. Please ensure the API server is running.")

                    except Exception as e:
                        st.error(f"❌ Unexpected error: {str(e)}")

    # Display results if available
    if 'analysis_results' in st.session_state:
        st.markdown("---")

        # Results header
        timestamp = st.session_state.get('analysis_timestamp', datetime.now())
        st.subheader(f"📈 Analysis Results (Generated: {timestamp.strftime('%Y-%m-%d %H:%M:%S')})")

        # Display the comprehensive analysis
        display_analysis_results(st.session_state['analysis_results'])

    else:
        # Show sample data/instructions when no file is uploaded
        st.markdown("---")
        st.subheader("📖 How to Use Speech2Sense")

        col1, col2 = st.columns(2)

        with col1:
            st.info("""
            **📁 Text File Format:**

            Upload a .txt file with conversations:
            ```
            Customer: I'm having trouble with my order
            Agent: I'd be happy to help you with that
            Customer: Thank you, I appreciate it
            ```

            **🎵 Audio File Support:**
            - Upload WAV, MP3, or MP4 files
            - Automatic speech-to-text transcription
            - Speaker diarization (Agent/Customer)
            - Works with phone calls, meetings, interviews

            **✅ Supported Features:**
            - Multi-speaker conversations
            - Sentiment analysis (5 levels)
            - Intent detection (6 categories)
            - Topic classification
            - CSAT scoring
            - Agent performance metrics
            """)

        with col2:
            st.success("""
            **🎯 What You'll Get:**

            - **Real-time Analysis**: AI-powered insights
            - **CSAT Scores**: Customer satisfaction metrics
            - **Agent Performance**: Comprehensive evaluation
            - **Topic Detection**: Automatic categorization
            - **Visual Analytics**: Interactive charts
            - **Export Options**: CSV, JSON, Excel formats
            - **Audio Processing**: Speech-to-text + analysis

            **🚀 Powered by:**
            - Groq LLaMA 3 AI Models
            - Whisper Speech Recognition
            - PyAnnote Speaker Diarization
            - Advanced NLP Processing
            - Real-time Analytics Engine
            """)

        # Audio processing demo
        st.markdown("---")
        st.subheader("🎵 Audio Processing Demo")

        col1, col2 = st.columns(2)

        with col1:
            st.info("""
            **Audio Processing Pipeline:**

            1. **Upload** - WAV, MP3, MP4 files
            2. **Convert** - Standardize audio format
            3. **Transcribe** - Speech-to-text using Whisper
            4. **Diarize** - Identify different speakers
            5. **Align** - Match text with speakers
            6. **Map** - Assign Agent/Customer roles
            7. **Analyze** - Sentiment & intent analysis
            8. **Report** - Generate comprehensive insights
            """)

        with col2:
            st.warning("""
            **Audio File Requirements:**

            - **Format**: WAV, MP3, MP4, M4A
            - **Quality**: Clear speech, minimal background noise
            - **Duration**: Up to 60 minutes recommended
            - **Speakers**: 2-3 speakers work best
            - **Language**: English (primary support)
            - **File Size**: Up to 100MB

            **Tips for Best Results:**
            - Use headset/microphone recordings
            - Avoid overlapping speech
            - Ensure clear audio quality
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
            **Sample File Contains:**
            - Customer service interaction
            - Multiple sentiment shifts
            - Problem resolution scenario
            - Agent performance examples
            - Various intent categories
            """)


if __name__ == "__main__":
    main()