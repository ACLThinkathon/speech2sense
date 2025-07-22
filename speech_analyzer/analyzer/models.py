from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Conversation(Base):
    __tablename__ = 'conversations'
    id = Column(Integer, primary_key=True, index=True)
    raw_text = Column(String)
    utterances = relationship("Utterance", back_populates="conversation")


class Utterance(Base):
    __tablename__ = 'utterances'
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id'))
    speaker = Column(String)
    sentence = Column(String)
    sentiment = Column(String)
    score = Column(Float)
    reason = Column(String)
    intent = Column(String, default="unknown")
    intent_reason = Column(String, default="")
    conversation = relationship("Conversation", back_populates="utterances")
