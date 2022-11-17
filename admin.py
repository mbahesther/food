# from flask import Flask, request, jsonify
# app = Flask(__name__)
from run import app, request, jsonify, mydb, MySQLdb
from run import (allowed_extensions, create_access_token, jwt_required, get_jwt_identity, jwt,
                  jwt_redis_blocklist, get_jwt, ACCESS_EXPIRES)
from passlib.hash import pbkdf2_sha256 as sha256
from werkzeug.utils import secure_filename
import os
import cloudinary
import cloudinary.uploader
import cloudinary.api


@app.route('/adminreg', methods=['POST'])
def adminreg():
    data = request.json
    email = data['email']
    password = data['password']
    confirm = data['confirm']
    my_cursor = mydb.cursor(MySQLdb.cursors.DictCursor)
    my_cursor.execute('''SELECT * FROM  admin WHERE email =%s''', [email])
    user = my_cursor.fetchone()
    if user:
        return jsonify('email exist')
    else:
        if password == confirm:
            hashed = sha256.hash(password)
            my_cursor.execute('INSERT INTO admin(email, password) VALUES(%s, %s)', [ email, hashed])
            mydb.commit()
            return jsonify('you can login to the Admin dashboard')    
        else:
            return jsonify('password didn\'t match')  



@app.route('/adminlogin', methods=['POST'])
def adminlogin():
    data = request.json
    email = data['email']
    password = data['password']
    my_cursor = mydb.cursor(MySQLdb.cursors.DictCursor)
    my_cursor.execute('''SELECT * FROM  admin WHERE email =%s''', [email])
    user = my_cursor.fetchone()
    if user and sha256.verify(password, user[2]):
        access_token = create_access_token(identity=user)
        return jsonify(access_token=access_token)
    else:
        return jsonify('incorrect email or password') 







#allowed extension to be pictures
def check_file_extension(filename):
   return filename.split('.')[-1] in allowed_extensions


@app.route('/upload', methods= ['POST'])
@jwt_required()
def upload():
   
    app.logger.info('in upload route')

    cloudinary.config(cloud_name = os.getenv('CLOUD_NAME'), api_key=os.getenv('API_KEY'), 
      api_secret=os.getenv('API_SECRET'))
    upload_result = None
    if request.method == 'POST':
        file_to_upload = request.files['file']
        app.logger.info('%s file_to_upload', file_to_upload)
        if file_to_upload:
            upload_result = cloudinary.uploader.upload(file_to_upload, folder='food')
            #image = app.logger.info(upload_result)
            image = upload_result['secure_url']

            my_cursor = mydb.cursor(MySQLdb.cursors.DictCursor)
            my_cursor.execute('INSERT INTO image(image) VALUES (%s)', [image])
            mydb.commit()
    return jsonify('image uploaded successfully'),200      


@app.route('/menu', methods= ['POST'])
@jwt_required()
def menu():
        data = request.json
        food_name = data['food_name']
        description = data['description']
        price = data['price']
        category = data['category']
        my_cursor = mydb.cursor(MySQLdb.cursors.DictCursor)
        my_cursor.execute('INSERT INTO menu(name, descr, price, category) VALUES (%s, %s, %s, %s)', [food_name, description, price, category ])
        mydb.commit()
        return jsonify('menu added successfully'), 200



#update menu
@app.route('/menu/<int:menu_id>', methods= ['PUT'])
@jwt_required()
def update_menu(menu_id):
   
    my_cursor = mydb.cursor(MySQLdb.cursors.DictCursor)
    my_cursor.execute('SELECT * FROM menu WHERE id =%s', [menu_id])
    query =my_cursor.fetchone()
    data = request.json
    food_name = data['food_name']
    description = data['description']
    price = data['price']
    category = data['category']
    my_cursor = mydb.cursor(MySQLdb.cursors.DictCursor)
    my_cursor.execute('UPDATE menu SET name=%s, descr=%s, price=%s, category=%s WHERE id=%s', [food_name, description, price, category, menu_id ])
    mydb.commit()
    return jsonify('menu updated sucessfully'), 200
       

@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload: dict):
    jti = jwt_payload["jti"]
    token_in_redis = jwt_redis_blocklist.get(jti)
    return token_in_redis is not None



@app.route('/logout', methods=['DELETE'])
@jwt_required()
def logout():
     jti = get_jwt()["jti"]
     jwt_redis_blocklist.set(jti, "", ex=ACCESS_EXPIRES)
     return jsonify(msg="Access token revoked")


    #  jti = get_jwt_identity()
    #  j = ''.join(map(str, jti))
    #  blacklist.add(j)
    #  return jsonify({"msg": "Successfully logged out"}), 200


        # current_user = get_jwt_identity()
        # user_id = current_user[0]
        # return jsonify({'success': True})