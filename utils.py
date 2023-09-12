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
        (name PRIMARY KEY, repo text, deployed_commit text, port_info text, volumes text)")


# Parse volumes
def parse_volumes(volume_string):
    return volume_string.split(VOLUME_SEPARATOR)

# Verify volumes
def verify_volumes(volumes):
    res = {}
    for volume in volumes:
        if len(volume) > VOLUME_MAX_LENGTH:
            res[RES_STATUS_KEY] = status.HTTP_400_BAD_REQUEST
            res[RES_ERROR_MESSAGE] = "volume {} path is too long".format(volume)
            return jsonify(res), status.HTTP_400_BAD_REQUEST
        if len(volume) == 0 or volume[0] != "/":
            res[RES_STATUS_KEY] = status.HTTP_400_BAD_REQUEST
            res[RES_ERROR_MESSAGE] = "volume {} has invalid format (must be full path)".format(volume)
            return jsonify(res), status.HTTP_400_BAD_REQUEST

# Convert volumes into single directory
def map_volume_to_local_dir(service_name, volumes):
    top_dir = CWD + "/" + service_name
    for i in range(len(volumes)): 
        local_dir = volumes[i][1:] # assert volumes[i][0] == "/"
        local_dir.replace("/", "-")
        local_dir = top_dir + "/" + local_dir
        volumes[i] = "-v {}:{}".format(local_dir, volumes[i])
    volumes.append("-v {}/keys:/keys".format(top_dir))
    return " ".join(volumes)

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

