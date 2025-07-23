import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Speech2Sense - Call Sentiment Analyzer", layout="wide")

st.markdown("""
<div style='display: flex; align-items: center;'>
    <img src='https://upload.wikimedia.org/wikipedia/commons/8/89/HD_transparent_picture.png' height='70' style='margin-right: 20px;'>
    <h1 style='color: #3a86ff;'>Speech2Sense - Call Sentiment Analyzer</h1>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("📄 Upload a conversation (.txt)", type="txt")
domain = st.text_input("Domain (optional)", help="E.g., ecommerce, healthcare")

if uploaded_file and st.button("🔍 Analyze"):

    with st.spinner("Uploading and analyzing..."):
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/plain")}
        data = {"domain": domain} if domain else {}
        try:
            response = requests.post(f"{API_URL}/analyze/", files=files, data=data)
            response.raise_for_status()
        except requests.RequestException as e:
            st.error(f"Error: {str(e)}")
            st.stop()

        resp_json = response.json()
        results = resp_json.get("results", [])

    if results:
        # Normalize testdata into DataFrame
        df = pd.DataFrame(results)

        # Rename backend keys for frontend consistency
        df.rename(columns={
            "score": "score_sentiment",
            "reason": "reason_sentiment",
            "intent_reason": "reason_intent"  # Rename to match column usage
        }, inplace=True)

        # Define which columns to display safely
        columns_to_display = ["speaker", "sentence", "intent", "sentiment", "score_sentiment"]

        if "reason_intent" in df.columns:
            columns_to_display.append("reason_intent")
        if "reason_sentiment" in df.columns:
            columns_to_display.append("reason_sentiment")

        st.subheader("🧾 Utterance-Level Sentiment & Intent Table")
        st.dataframe(df[columns_to_display])

        # Pie Chart - Sentiment
        st.subheader("📊 Sentiment Distribution (Pie Chart)")
        sentiment_counts = df["sentiment"].value_counts()
        fig1, ax1 = plt.subplots()
        color_map = {
            "extreme positive": "#00ff00",
            "positive": "#7CFC00",
            "neutral": "gray",
            "negative": "orange",
            "extreme negative": "red"
        }
        colors = [color_map.get(s, 'blue') for s in sentiment_counts.index]
        ax1.pie(sentiment_counts, labels=sentiment_counts.index, autopct='%1.1f%%',
                colors=colors, startangle=90, counterclock=False)
        ax1.axis('equal')
        st.pyplot(fig1)

        # Bar Chart - Intent
        st.subheader("🏷️ Intent Distribution")
        intent_counts = df["intent"].value_counts()
        fig2, ax2 = plt.subplots()
        ax2.bar(intent_counts.index, intent_counts.values, color="#3a86ff")
        ax2.set_ylabel("Count")
        ax2.set_title("Intent Distribution")
        st.pyplot(fig2)

        # Sentiment Summary
        st.subheader("😊 Overall Sentiment Summary")


        def average_and_mood(sub_df):
            if sub_df.empty:
                return 0.0, "❔"
            avg = sub_df["score_sentiment"].mean()
            if avg >= 0.7:
                return avg, "😃"
            elif avg >= 0.4:
                return avg, "😐"
            else:
                return avg, "😞"


        agent_df = df[df["speaker"].str.lower().str.contains("agent")]
        customer_df = df[df["speaker"].str.lower().str.contains("customer")]

        agent_score, agent_face = average_and_mood(agent_df)
        cust_score, cust_face = average_and_mood(customer_df)

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Agent Sentiment", f"{agent_score:.2f} {agent_face}")
        with col2:
            st.metric("Customer Sentiment", f"{cust_score:.2f} {cust_face}")
