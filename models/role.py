#!/usr/bin/env python
from flask import Flask, jsonify, request
from config import db
import yaml
import os
import enum

class Role(db.Model):
    ''' The data model'''
    # table name
    __tablename__ = 'roles'
    role = db.Column(db.String(255), primary_key=True)
    level = db.Column(db.Float(), nullable=True)
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}
