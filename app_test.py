from flask import Flask
from flask_pymongo import PyMongo

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb+srv://Rishi:Rishi%4012@cluster0.i2x9iiu.mongodb.net/testDB?appName=Cluster0"

mongo = PyMongo(app)
db = mongo.db

@app.route("/")
def home():
    return "MongoDB Connected!"

@app.route("/add-test")
def add_test():
    db.test.insert_one({"name": "Rishi", "project": "Assignment Platform"})
    return "Inserted!"


if __name__ == "__main__":
    app.run(debug=True)
