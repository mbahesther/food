from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
import redis

import MySQLdb.cursors
import mysql.connector
import MySQLdb.cursors

from flask_jwt_extended import (JWTManager, create_access_token, get_jwt_identity,
                                 jwt_required, get_jwt)


ACCESS_EXPIRES = timedelta(hours=1)

app = Flask(__name__)

app.config['SECRET_KEY'] = '1892434ad187b9bb4fd163fbaa6f0ec7'
app.config['SQLALCHEMY_DATABASE_URI']= 'mysql+pymysql://root:''@localhost/food'
allowed_extensions = ['jpg', 'png', 'jpeg']

# app.config['JWT_ACCESS_TOKEN_EXPIRES'] =timedelta(hours=2)
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = ACCESS_EXPIRES
#app.config['JWT_ACCESS_TOKEN_EXPIRES'] =timedelta(minutes=2)

jwt = JWTManager(app)

#blacklist = set()
jwt_redis_blocklist = redis.StrictRedis(
    host="localhost", port=6379, db=0, decode_responses=True
)

mydb = mysql.connector.connect(
    host='localhost',
    user ='root',
    password ='',
    database ='food',
    )

my_cursor =mydb.cursor()   