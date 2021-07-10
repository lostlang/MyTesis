from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import psycopg2

from face_rec import json_face_to_numpy_face, face_compare, load
from db_post import get_info
from config import database_setting
import naming

server_app = Flask(__name__)
cors = CORS(server_app, resource={
    r"/*": {
        "origins": "*"
    }
})

connection = psycopg2.connect(
    database=database_setting[naming.name],
    user=database_setting[naming.user],
    password=database_setting[naming.password],
    host=database_setting[naming.host],
    port=database_setting[naming.port]
)
loaded_face = load(connection)


@server_app.route("/", methods=['GET'])
def get_test():
    return jsonify("test_data")


@server_app.route("/", methods=['POST'])
def get_face():
    face_json = json.loads(request.data)
    face_np = json_face_to_numpy_face(face_json)
    user_id = face_compare(loaded_face, face_np)
    out = get_info(connection, user_id)
    print(out)
    return jsonify(out)


if __name__ == '__main__':
    server_app.run()
