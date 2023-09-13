from flask import Flask, jsonify, request 
from flask_api import status
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from utils import *
from settings import *

app = Flask(__name__)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["1/second"]
)

init_db()

@app.route("/deploy", methods=['GET'])
def deploy():
    SERVICE_PARAM_KEY = "service"
    
    req_param = request.args.to_dict()
    param_verify_result = verify_parameters([SERVICE_PARAM_KEY], req_param.keys())
    if param_verify_result != None:
        return param_verify_result
    
    service_name = req_param[SERVICE_PARAM_KEY]
    
    # Connect to DB  
    connect = sqlite3.connect(DATABASE, isolation_level=None)
    cursor = connect.cursor()
    
    # Get the service info
    cursor.execute("SELECT repo, deployed_commit, port_info, volumes FROM service WHERE name=?", (service_name,))
    s = cursor.fetchone()
    if s == None:
        return {RES_STATUS_KEY: status.HTTP_404_NOT_FOUND, RES_ERROR_MESSAGE: "service not exists"}, status.HTTP_404_NOT_FOUND
    repo, deployed_commit, port_info, volume_string = s
    
    # Verify volume String
    volumes = parse_volumes(volume_string)
    volumes_verify_result = verify_volumes(volumes)
    if volumes_verify_result != None:
        return volumes_verify_result
    volume_arg = map_volume_to_local_dir(service_name, volumes)
    
    # Clone or pull repo
    subprocess.call(["bash", "./update_repo.sh", CWD, service_name, repo])
    
    # Parse commit id
    last_commit_id = subprocess.run(["git", "log", '--format="%H"', "-n", "1"], capture_output=True, cwd=service_name).stdout.decode()
    
    # Verify commit
    if last_commit_id == deployed_commit:
        return {RES_STATUS_KEY: status.HTTP_400_BAD_REQUEST, RES_ERROR_MESSAGE: "{}@{} already deployed".format(service_name, deployed_commit)}, status.HTTP_400_BAD_REQUEST 
    
    # Update latest commit 
    cursor.execute("UPDATE service SET deployed_commit=? WHERE name=?", (last_commit_id, service_name))
    connect.commit()
    
    # Deploy as a docker container (subprocess)
    subprocess.call(["bash", "./deploy_repo.sh", CWD, service_name, port_info, volume_arg])
    
    res = {}
    res[RES_STATUS_KEY] = status.HTTP_200_OK
    res[RES_DATA_KEY] = "Deployed the service {} successfully!".format(service_name)
    return res, status.HTTP_200_OK



# Enroll project
@app.route("/enroll", methods=['POST'])
def enroll():
    ACCESS_TOKEN_HEADER_KEY = "Access-Token"
    SERVICE_NAME_PARAM_KEY = "service"
    SERVICE_REPO_PARAM_KEY = "repo"
    SERVICE_PORT_INFO_PARAM_KEY = "port_info"
    SERVICE_VOLUMES_PARAM_KEY = "volumes"
    
    req_header = request.headers
    req_param = request.form

    # Verification
    header_verify_result = verify_parameters([ACCESS_TOKEN_HEADER_KEY], req_header.keys(), is_header=True)
    if header_verify_result != None:
        return header_verify_result
    if req_header[ACCESS_TOKEN_HEADER_KEY] != ACCESS_TOKEN:
        return {RES_STATUS_KEY: status.HTTP_403_FORBIDDEN, RES_ERROR_MESSAGE: "invalid access token"}, status.HTTP_403_FORBIDDEN
    param_verify_result = verify_parameters([SERVICE_NAME_PARAM_KEY, SERVICE_REPO_PARAM_KEY, SERVICE_PORT_INFO_PARAM_KEY, SERVICE_VOLUMES_PARAM_KEY], req_param.keys())
    if param_verify_result != None:
        return param_verify_result
    
    service = req_param[SERVICE_NAME_PARAM_KEY]
    repo = req_param[SERVICE_REPO_PARAM_KEY]
    port_info = req_param[SERVICE_PORT_INFO_PARAM_KEY]
    volumes = req_param[SERVICE_VOLUMES_PARAM_KEY]
    
    # Connect to DB
    connect = sqlite3.connect(DATABASE, isolation_level=None)
    cursor = connect.cursor()
    
    # INSERT the service into DB
    cursor.execute('SELECT * FROM service WHERE name=?', (service,))
    s = cursor.fetchall()
    if(len(s)==0): # New Service
        cursor.execute("INSERT INTO service(name, repo, deployed_commit, port_info, volumes) VALUES (?, ?, ?, ?, ?)", (service, repo, "NO_DEPLOYMENT_YET", port_info, volumes))
    cursor.execute('UPDATE service SET repo=? WHERE name=?', (repo, service,))
    
    res = {}
    res[RES_STATUS_KEY] = status.HTTP_200_OK
    res[RES_DATA_KEY] = "The service {} was successfully created".format(service)
    return jsonify(res)

# app.run(host="localhost",port=5050)