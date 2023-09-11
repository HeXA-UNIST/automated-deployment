from dotenv import dotenv_values
import os
import sys

CWD = os.path.dirname(os.path.abspath(sys.argv[0]))

server_secure_config = dotenv_values(".env") 

DATABASE = "services.db"

RES_STATUS_KEY = "status"
RES_DATA_KEY = "data"
RES_ERROR_MESSAGE = "error_message"
ACCESS_TOKEN = server_secure_config["ACCESS_TOKEN"]