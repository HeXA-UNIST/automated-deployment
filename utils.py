from settings import *
import sqlite3
from flask_api import status
from flask import Flask, jsonify, request 
import subprocess

connect = sqlite3.connect(DATABASE, isolation_level=None)

def init_db():
    cursor = connect.cursor()

    # User info 테이블 생성
    cursor.execute("CREATE TABLE IF NOT EXISTS service \
        (name PRIMARY KEY, repo text, deployed_commit text, port_info text)")
    
# json에 key가 존재하는지 확인
def json_has_key(json, key):
    try:
        buf = json[key]
    except KeyError:
        return False

    return True

# Verify parameters and return 400 and error message if some parameters were missing
def verify_parameters(req_params, actual_params, is_header=False):
    req_params = set(req_params)
    actual_params = set(actual_params)
    diff = req_params - actual_params
    if len(diff) > 0:
        res = {}
        res[RES_STATUS_KEY] = status.HTTP_400_BAD_REQUEST
        res[RES_ERROR_MESSAGE] = "required {} not exists: ".format("header" if is_header else "parameter") + ", ".join(diff) 
        return jsonify(res), status.HTTP_400_BAD_REQUEST
    
    return None

