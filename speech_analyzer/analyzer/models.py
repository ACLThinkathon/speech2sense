from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=True)
    raw_text = Column(Text, nullable=False)

    utterances = relationship("Utterance", back_populates="conversation")

class Utterance(Base):
    __tablename__ = "utterances"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    speaker = Column(String, nullable=False)
    sentence = Column(Text, nullable=False)
    sentiment = Column(String, nullable=False)
    score = Column(Float, nullable=False)
    reason = Column(Text, nullable=False)

    conversation = relationship("Conversation", back_populates="utterances")
