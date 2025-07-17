from bertopic import BERTopic
import hdbscan
import logging
import numpy as np

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure HDBSCAN for small datasets and stability
hdbscan_model = hdbscan.HDBSCAN(min_cluster_size=2, min_samples=1, prediction_data=False)

# Create the BERTopic model
topic_model = BERTopic(hdbscan_model=hdbscan_model)

def get_topic_distribution(texts):
    logger.info("Received %d raw texts", len(texts))

    # Clean and filter texts
    texts = [t.strip() for t in texts if isinstance(t, str) and t.strip()]
    logger.info("Valid texts after cleaning: %d", len(texts))
    if len(texts) < 3:
        logger.warning("Not enough valid texts to run topic modeling. Skipping.")
        return []

    try:
        # Optionally check embeddings (use this only if you suspect collapsing embeddings)
        # embeddings = topic_model.embedding_model.embed(texts)
        # logger.info("Embedding shape: %s", np.array(embeddings).shape)

        # Fit and transform texts
        topics, _ = topic_model.fit_transform(texts)
        logger.info("BERTopic clustering complete. Found %d topics.", len(set(topics)))

        topic_info = topic_model.get_topic_info()
        top_topics = topic_info.head(10)
        result = []
        for _, row in top_topics.iterrows():
            if row.Topic == -1:
                logger.debug("Skipping outlier topic: %s", row.Name)
                continue
            result.append({
                "topic": row.Name,
                "count": int(row.Count)
            })

        logger.info("Returning %d topics.", len(result))
        return result

    except Exception as e:
        logger.error("Topic modeling failed: %s", str(e), exc_info=True)
        return []
