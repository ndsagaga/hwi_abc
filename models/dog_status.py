#!/usr/bin/env python
from flask import Flask, jsonify, request
from sqlalchemy.orm import relationship
from config import db
import yaml
import os
import enum

class DogStatus(db.Model):
    ''' The data model'''
    # table name
    __tablename__ = 'dog_status'
    tag = db.Column(db.String(255), db.ForeignKey("dogs.tag"), primary_key=True)
    status = db.Column(db.String(255), db.ForeignKey("statuses.status"), primary_key=True)
    timestamp = db.Column(db.DateTime(), nullable=False)
    by = db.Column(db.String(255), db.ForeignKey("users.id"), nullable=False)
    dog = relationship("Dog", back_populates="statuses")
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}
