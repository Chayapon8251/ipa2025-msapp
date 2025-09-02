import os
from flask import Flask, request, render_template, redirect
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__)

mongo_uri = os.environ.get("MONGO_URI")
db_name = os.environ.get("DB_NAME")

client = MongoClient(mongo_uri)
db = client[db_name]
routers = db["routers"]
interface_status = db["interface_status"]

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", routers=list(routers.find()))

@app.route("/add", methods=["POST"])
def add_router():
    ip = request.form.get("ip")
    username = request.form.get("username")
    password = request.form.get("password")

    if ip and username and password:
        routers.insert_one({
            "ip": ip,
            "username": username,
            "password": password
        })
    return redirect("/")

@app.route("/delete/<id>", methods=["POST"])
def delete_router(id):
    routers.delete_one({"_id": ObjectId(id)})
    return redirect("/")

@app.route("/router/<ip_address>", methods=["GET"])
def router_detail(ip_address):
    # Find the last 3 status records for the given IP, sorted by timestamp
    statuses = list(interface_status.find(
        {"router_ip": ip_address},
        sort=[("timestamp", -1)]
    ).limit(3))
    return render_template("router_detail.html", router_ip=ip_address, statuses=statuses)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
