
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "True"
os.environ["STREAMLIT_WATCHER_TYPE"] = "none"

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
import pdfkit
from intent_sentiment import analyze_message

st.set_page_config(page_title="Intent & Sentiment Dashboard", layout="wide")
st.title("Intent, Sentiment, CSAT & Agent Performance Analysis")

st.info("📤 Upload a conversation TXT file with lines like: 'Agent: ...' and 'Customer: ...'")

uploaded_file = st.file_uploader("Upload conversation .txt", type=["txt"])

def infer_customer_satisfaction(convo_df):
    customer_msgs = convo_df[convo_df["Speaker"].str.lower() == "customer"]
    sentiments = customer_msgs["Sentiment"].tolist()
    if not sentiments:
        return "Unknown"
    if sentiments[-1] == "positive":
        return "High"
    elif sentiments[-1] == "neutral" and "negative" not in sentiments:
        return "Medium"
    else:
        return "Low"

def evaluate_agent_performance(convo_df):
    agent_msgs = convo_df[convo_df["Speaker"].str.lower() == "agent"]
    sentiment_counts = agent_msgs["Sentiment"].value_counts().to_dict()
    if sentiment_counts.get("positive", 0) >= len(agent_msgs) * 0.6:
        return "Excellent"
    elif sentiment_counts.get("negative", 0) > 0:
        return "Needs Improvement"
    else:
        return "Good"

def convert_df_to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Analysis")
    return output.getvalue()

def generate_html_report(df, csat, agent_score):
    html = f"""
    <h2>Conversation Analysis Report</h2>
    <p><strong>Customer Satisfaction:</strong> {csat}</p>
    <p><strong>Agent Performance:</strong> {agent_score}</p>
    {df.to_html(index=False)}
    """
    return html

def convert_html_to_pdf(html_content):
    with open("report.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    pdfkit.from_file("report.html", "conversation_report.pdf")
    with open("conversation_report.pdf", "rb") as f:
        return f.read()

if uploaded_file:
    st.success("✅ File uploaded. Analyzing conversation...")
    try:
        content = uploaded_file.read().decode("utf-8")
        messages = []
        conversation_id = 1

        for line in content.splitlines():
            line = line.strip()
            if not line or ":" not in line:
                continue
            speaker, message = line.split(":", 1)
            messages.append({
                "conversation_id": conversation_id,
                "speaker": speaker.strip(),
                "message": message.strip()
            })

        df = pd.DataFrame(messages)
        results = []
        for _, row in df.iterrows():
            result = analyze_message(row["message"])
            results.append({
                "Conversation ID": row["conversation_id"],
                "Speaker": row["speaker"],
                "Message": row["message"],
                "Top Intent": max(result["intents"], key=result["intents"].get),
                "Sentiment": result["sentiment"]["label"]
            })

        result_df = pd.DataFrame(results)
        st.dataframe(result_df)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.subheader("Intent Distribution")
            st.bar_chart(result_df["Top Intent"].value_counts())

        with col2:
            st.subheader("Sentiment Distribution")
            st.bar_chart(result_df["Sentiment"].value_counts())

        with col3:
            st.subheader("Overall Conversation Sentiment (Pie)")
            sentiment_counts = result_df["Sentiment"].value_counts()
            fig, ax = plt.subplots()
            ax.pie(sentiment_counts, labels=sentiment_counts.index, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')
            st.pyplot(fig)

        st.divider()
        col4, col5 = st.columns(2)
        with col4:
            csat = infer_customer_satisfaction(result_df)
            st.metric("🧍 Customer Satisfaction Level", csat)
        with col5:
            agent_score = evaluate_agent_performance(result_df)
            st.metric("👨‍💼 Agent Performance Rating", agent_score)

        # NEW: Add summaries
        csat_summaries = {
            "High": "🟢 The customer seems satisfied by the end of the conversation.",
            "Medium": "🟡 The conversation was neutral or mixed, but did not end negatively.",
            "Low": "🔴 The customer still expressed dissatisfaction at the end.",
            "Unknown": "⚪️ Not enough customer data to infer satisfaction."
        }

        agent_summaries = {
            "Excellent": "🟢 The agent maintained a mostly positive tone throughout the conversation.",
            "Good": "🟡 The agent performed adequately with a mostly neutral tone.",
            "Needs Improvement": "🔴 The agent had negative responses or lacked empathy."
        }

        st.write("**CSAT Summary:**", csat_summaries.get(csat, "No summary available."))
        st.write("**Agent Summary:**", agent_summaries.get(agent_score, "No summary available."))


        st.subheader("📤 Export Reports")
        excel_data = convert_df_to_excel(result_df)
        st.download_button(
            label="📥 Download Excel Report",
            data=excel_data,
            file_name="conversation_analysis.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        if st.button("📄 Generate & Download PDF Report"):
            html_report = generate_html_report(result_df, csat, agent_score)
            pdf_data = convert_html_to_pdf(html_report)
            st.download_button(
                label="📥 Download PDF Report",
                data=pdf_data,
                file_name="conversation_report.pdf",
                mime="application/pdf"
            )

    except Exception as e:
        st.error(f"⚠️ Error: {e}")
