#!/usr/bin/env python
from flask import Flask, jsonify, request
from config import db
from sqlalchemy.orm import relationship

class UserSession(db.Model):
    ''' The data model'''
    # table name
    __tablename__ = 'user_sessions'
    id = db.Column(db.String(255), primary_key=True)
    user_id = db.Column(db.String(255), db.ForeignKey("users.id"), nullable=False)
    expire_timestamp = db.Column(db.DateTime(), nullable=False)
    user = relationship("User", back_populates="user_session")
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}
