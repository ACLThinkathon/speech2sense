from sqlalchemy import MetaData, Table, Column, Integer, String, TIMESTAMP, Text, ForeignKey
from databases import Database

metadata = MetaData()

conversations = Table(
    "conversations",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("timestamp", TIMESTAMP, nullable=False),
    Column("agent_id", String(50)),
    Column("customer_id", String(50)),
    Column("summary", Text),
    Column("topics", Text),
)

messages = Table(
    "messages",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("conversation_id", Integer, ForeignKey("conversations.id")),
    Column("sender", String(50)),
    Column("text", Text),
    Column("intent", String(50)),
    Column("sentiment", String(50)),
    Column("created_at", TIMESTAMP),
)

intents = Table(
    "intents",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(50)),
    Column("description", String(200)),
)

sentiments = Table(
    "sentiments",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("type", String(50)),
    Column("score_range", String(20)),
)

database = Database("postgresql://user:password@db:5432/callcenter")
