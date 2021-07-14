#!/usr/bin/env python
from flask import Flask, jsonify, request
from config import db
import yaml
import os
import enum

class TreatmentTaskAction(db.Model):
    ''' The data model'''
    # table name
    __tablename__ = 'treatment_task_actions'
    treatment_task_id = db.Column(db.Integer(), db.ForeignKey("treatment_tasks.id"), nullable=False)
    action_performed = db.Column(db.Text(), nullable=False)
    action_photo = db.Column(db.String(255), nullable=True)
    timestamp = db.Column(db.Timestamp(), nullable=False)
    by = db.Column(db.String(255), db.ForeignKey("users.id"), nullable=False)
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}
