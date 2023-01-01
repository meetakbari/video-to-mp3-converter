import os, gridfs, pika, json
from flask import Flask, request
from flask_pymongo import PyMongo
from auth import validate
from auth_svc import access
from storage import util

server = Flask(__name__)
#host.minikube help us to connect with internal local mongodb database from container 
# & videos: collection name to store video files
server.config["MONGO_URI"] = "mongodb://host.minikube.internal:27017/videos" 

mongo = PyMongo(server)

fs = gridfs.GridFS(mongo.db)

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host="rabbitmq")
)
channel = connection.channel()

# declaring a video queue to the rabbitmq
# channel.queue_declare(queue='video', durable=True)
# channel.queue_declare(queue='mp3', durable=True)

@server.route("/login", methods=["POST"])
def login():
    token, err = access.login(request)

    if not err:
        return token
    else:
        print("came to the gateway's server file entry point --------------")
        return err

@server.route("/upload", methods=["POST"])
def upload():
    access, err = validate.token(request)

    if not err:
        access = json.loads(access)

        if access["admin"]:
            if len(request.files) > 1:
                return "More than 1 file is not allowed!", 400
            if len(request.files) < 1:
                return "File is missing!", 400
            
            for _, f in request.files.items():
                err = util.upload(f, fs, channel, access)

                if err:
                    return err
            
            return "File uploaded successfully!", 200
        else:
            return "not authorized", 401 
    else:
        return err

@server.route("/download", methods=["GET"])
def download():
    pass

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8080, debug=True)