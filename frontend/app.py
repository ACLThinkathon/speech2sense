import streamlit as st
import requests
import plotly.express as px

st.title("Customer Call Center Sentiment & Intent Analysis")

uploaded_file = st.file_uploader("Upload call transcript TXT file", type=['txt'])

if uploaded_file:
    content = uploaded_file.read().decode("utf-8")  # Read bytes -> string

    messages = []
    for line in content.splitlines():
        if ':' not in line:
            continue
        sender, text = line.split(':', 1)
        sender = sender.strip()
        text = text.strip()
        if sender and text:
            messages.append({"sender": sender, "text": text})

    if not messages:
        st.error("No valid 'sender: message' lines found in file.")
    else:
        payload = {"messages": messages}
        with st.spinner("Analyzing..."):
            try:
                res = requests.post("http://localhost:8000/analyze/", json=payload)
                res.raise_for_status()
                result = res.json()

                st.subheader("Conversation Summary")
                st.write(result.get("summary"))

                st.subheader("Intent Distribution")
                intent_dist = result.get("intent_distribution", {})
                fig_intent = px.pie(
                    names=list(intent_dist.keys()),
                    values=list(intent_dist.values()),
                    title="Intents"
                )
                st.plotly_chart(fig_intent)

                st.subheader("Sentiment Distribution")
                sentiment_dist = result.get("sentiment_distribution", {})
                fig_sentiment = px.pie(
                    names=list(sentiment_dist.keys()),
                    values=list(sentiment_dist.values()),
                    title="Sentiment"
                )
                st.plotly_chart(fig_sentiment)

                st.subheader("Topic Distribution")
                topic_dist = result.get("topic_distribution", [])
                if topic_dist:
                    fig_topic = px.bar(
                        x=[t['topic'] for t in topic_dist],
                        y=[t['count'] for t in topic_dist],
                        title="Topic Distribution"
                    )
                    st.plotly_chart(fig_topic)
                else:
                    st.write("No topics detected.")

                st.subheader("Detailed Messages")
                for msg in result.get("analysis", []):
                    st.markdown(
                        f"**{msg['sender']}**: {msg['text']}  \nIntent: {msg['intent']}  \nSentiment: {msg['sentiment']}"
                    )
                    st.markdown("---")

            except Exception as e:
                st.error(f"Error during analysis: {e}")
