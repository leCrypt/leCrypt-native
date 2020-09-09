#!/usr/bin/python3
import json
from os import getenv
from sys import platform
from pathlib import Path
from flask import Flask, request, jsonify

app = Flask(__name__)


def user_data_dir(file_name):
    """
    Get data directory depending upon their kernel
    """

    if platform.startswith("win"):
        os_path = getenv("LOCALAPPDATA")
    elif platform.startswith("darwin"):
        os_path = "~/Library/Application Support"
    else:
        os_path = getenv("XDG_DATA_HOME", "~/.local/share")

    path = Path(os_path) / "leCrypt"

    return path.expanduser() / file_name


user_data_dir('...').parent.mkdir(parents=True, exist_ok=True)


token_of_the_server = json.dumps({
    "token": ""
})


@app.route('/api')
def index():
    res = ' '.join(['/api/update/passes\n', '/api/update/notes\n', '/api/read/passes\n', '/api/read/notes\n'])
    return res


@app.route('/api/update/passes', methods=['POST'])
def update_passes():
    """
    Used to update data in passes.json
    """

    data = jsonify(request.get_json(force=True))
    passes = json.dumps(data.response[0].decode('utf-8'))
    with open(user_data_dir("passes.json"), "w") as file:
        file.write(passes)
    return "done with passes"


@app.route('/api/update/notes', methods=['POST'])
def update_notes():
    """
    Used to update data in notes.json
    """

    data = jsonify(request.get_json(force=True))
    notes = json.dumps(data.response[0].decode('utf-8'))
    with open(user_data_dir("notes.json"), "w") as file:
        file.write(notes)
    return "done with notes"


@app.route('/api/update/hash', methods=['POST'])
def update_hash():
    """
    Used to update the hash
    """
    data = jsonify(request.get_json(force=True))
    hash = json.dumps(data.response[0].decode('utf-8'))
    with open(user_data_dir("hash.json"), "w") as file:
        file.write(hash)
    return "done with hash"


@app.route('/api/read/passes', methods=['GET'])
def get_passes():
    """
    Used to get data saved in passes.json
    """
    with open(user_data_dir("passes.json"), "r") as file:
        dat = file.read()
        return dat


@app.route('/api/read/notes', methods=['GET'])
def get_notes():
    """
    Used to get data saved in notes.json
    """
    with open(user_data_dir("notes.json"), "r") as file:
        dat = file.read()
        return dat


@app.route('/api/read/hash', methods=['GET'])
def get_hash():
    """
    Used to get the hash of user
    """
    with open(user_data_dir("hash.json"), "r") as file:
        hash = file.read()
        return hash


@app.route('/api/getToken', methods=['GET'])
def get_token():
    """
    Used to get current token on server
    """
    global token_of_the_server
    res = token_of_the_server
    token_of_the_server = json.dumps({
        "token": ""
    })
    return res


@app.route('/api/qr_output', methods=['GET'])
def get_lecrypt_devices():
    """
    Used to return a json object with a user, key token and leCrypt devices for refreshing
    """
    import socket
    import string
    import secrets
    import base64
    import pyqrcode
    from errno import ENETUNREACH

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("1.1.1.1", 80))
        ip = s.getsockname()[0]
        s.close()
        alphabet = string.ascii_letters + string.digits
        token = ''.join(secrets.choice(alphabet) for i in range(5))
        global token_of_the_server
        token_of_the_server = json.dumps({
            "token": token
        })
        jso = json.dumps({
            "ip": ip,
            "token": token
        })
        qr = pyqrcode.create(jso.encode('utf-8'))
        qr.png(user_data_dir('data.png'), scale=6)
        with open(user_data_dir('data.png'), "rb") as img_file:
            data = base64.b64encode(img_file.read())
            res = json.dumps({
                "ip": ip,
                "token": token,
                "base64qr": data.decode('utf-8')
            })
            return res

    except IOError as e:
        # an IOError exception occurred (socket.error is a subclass)
        if e.errno == ENETUNREACH:
            return "unreachable"
        else:
            raise
