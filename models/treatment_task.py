#!/usr/bin/env python
from flask import Flask, jsonify, request
from sqlalchemy.sql.expression import null
from config import db
import yaml
import os
import enum

class ResponseType(str, enum.Enum):
    TEXT = 'TEXT'
    BINARY = 'BINARY'
    COUNTER = 'COUNTER'
    GEO_PHOTO = 'GEO_PHOTO'
    TIMESTAMP = 'TIMESTAMP'

class TreatmentTask(db.Model):
    ''' The data model'''
    # table name
    __tablename__ = 'treatment_tasks'
    id = db.Column(db.Integer(), primary_key=True, auto_increment=True)
    tag = db.Column(db.String(255), db.ForeignKey("dogs.tag"), nullable=False)
    status = db.Column(db.String(255), db.ForeignKey("statuses.status"), nullable=False)
    assigned_role = db.Column(db.String(255), db.ForeignKey("roles.role"), nullable=False)
    task = db.Column(db.Text(), nullable=False)
    response_type = db.Column(db.Enum(ResponseType), nullable=False)
    is_completed = db.Column(db.Boolean())
    is_required = db.Column(db.Boolean())
    last_modified_timestamp = db.Column(db.DateTime())
    last_modified_by = db.Column(db.String(255), nullable=False)
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}
