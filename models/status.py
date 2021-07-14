#!/usr/bin/env python
from flask import Flask, jsonify, request
from sqlalchemy.orm import relationship
from config import db
import yaml
import os
import enum

class Status(db.Model):
    ''' The data model'''
    # table name
    __tablename__ = 'statuses'
    status = db.Column(db.String(255), nullable=False, primary_key=True)
    order = db.Column(db.Float(), nullable=False)
    description = db.Column(db.Text(), nullable=True)
    alert_after_days = db.Column(db.Integer(), nullable=True)
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}
