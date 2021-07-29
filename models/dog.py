#!/usr/bin/env python
from flask import Flask, jsonify, request
from sqlalchemy.orm import relationship
from config import db
import yaml
import os
import enum

class Gender(str, enum.Enum):
    M = 'M'
    F = 'F'


class Dog(db.Model):
    ''' The data model'''
    # table name
    __tablename__ = 'dogs'
    tag = db.Column(db.String(255), nullable=False, primary_key=True)
    avatar = db.Column(db.String(255), nullable=True)
    gender = db.Column(db.Enum(Gender), nullable=False)
    age_category = db.Column(db.String(255), nullable=True)
    color = db.Column(db.String(255), nullable=True)
    weight = db.Column(db.Integer(), nullable=True)
    additional_info = db.Column(db.Text(), nullable=True)
    pickup_lat = db.Column(db.Float(), nullable=True)
    pickup_long = db.Column(db.Float(), nullable=True)
    pickup_time = db.Column(db.DateTime(), nullable=True)
    pickup_by = db.Column(db.Integer(), nullable=True)
    pickup_photo = db.Column(db.String(255), nullable=False)
    dropoff_lat = db.Column(db.Float(), nullable=True)
    dropoff_long = db.Column(db.Float(), nullable=True)
    dropoff_time = db.Column(db.DateTime(), nullable=True)
    dropoff_by = db.Column(db.Integer(), nullable=True)
    dropoff_photo = db.Column(db.String(255), nullable=False)
    created_timestamp = db.Column(db.DateTime(), nullable=False)
    last_modified_timestamp = db.Column(db.DateTime(), nullable=False)
    is_active = db.Column(db.Boolean(), default=True)
    statuses = relationship("DogStatus", back_populates="dog")
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}
