#!/usr/bin/env python
from flask import Flask, jsonify, request
from config import db
from models.role import Role
from sqlalchemy.orm import relationship
import enum

class Gender(str, enum.Enum):
    M = 'M'
    F = 'F'


class User(db.Model):
    ''' The data model'''
    # table name
    __tablename__ = 'users'
    id = db.Column(db.String(255), primary_key=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    gender = db.Column(db.Enum(Gender), nullable=False)
    phone_number = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(255), db.ForeignKey(Role.role), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean(), nullable=False)
    user_session = relationship("UserSession", back_populates = "user")
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}
