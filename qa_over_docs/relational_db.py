from qa_over_docs import r_db
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime

class Question(r_db.Model):
    id = Column(Integer, primary_key=True)
    question = Column(String, nullable=False)
    count = Column(Integer, default=1)

class Answer(r_db.Model):
    id = Column(Integer, primary_key=True)
    answer = Column(String, nullable=False)

class Response(r_db.Model):
    id = Column(Integer, primary_key=True)
    question = Column(Integer, ForeignKey("question.id"), nullable=False)
    answer = Column(Integer, ForeignKey("answer.id"), nullable=False)
    likes = Column(Integer, default=0)
    dislikes = Column(Integer, default=0)
    timestamp = Column(DateTime, default=datetime.utcnow)