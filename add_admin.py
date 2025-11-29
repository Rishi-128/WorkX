from flask import Flask
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb+srv://Rishi:Rishi%4012@cluster0.i2x9iiu.mongodb.net/workxDB?appName=Cluster0"

mongo = PyMongo(app)
db = mongo.db

# Admin data from users.json
admin_data = {
    "username": "admin",
    "password": "scrypt:32768:8:1$KNVR34ycZ4H5GPWq$f3be87a22a8d50d5e2122d5447039f070ddb2cd4c22e930e295bbb808329690dd87b7fc309588b839e24eca6d3502e5ce1dbcfebd4a48b891af1f509de8d7609",
    "email": "admin@workx.com"
}

with app.app_context():
    # Check if admin exists
    existing = db.admin.find_one({'username': 'admin'})
    
    if existing:
        print("Admin already exists!")
    else:
        db.admin.insert_one(admin_data)
        print("✓ Admin added successfully!")
        print("Username: admin")
        print("Password: admin123")
