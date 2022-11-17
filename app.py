from run import *

from passlib.hash import pbkdf2_sha256 as sha256





@app.route('/')
def home():
    return "hello welcome to food API "

#user regisration
@app.route('/register', methods= ['POST'])
def register():
    data = request.json
    firstname = data['firstname']
    lastname = data['lastname']
    email = data['email']
    phone_no = data['phone_no']
    password = data['password']
    c_password = data['c_password']
    my_cursor = mydb.cursor(MySQLdb.cursors.DictCursor)
    my_cursor.execute('''SELECT * FROM  registration WHERE email =%s''', [email])
    user = my_cursor.fetchone()
    if user:
        return jsonify("Email already taken, use another email")
    else:
        if len(phone_no) !=11:
            return jsonify('Your phone number is incomplete')
        else:

            if password == c_password:
                hash_password = sha256.hash(password)     
                my_cursor.execute('INSERT INTO registration(first, last, email, phone, password) VALUES(%s, %s, %s, %s, %s )', [firstname, lastname, email, phone_no, hash_password])
                mydb.commit()
                return jsonify('Thanks for registering you can login now')
            else:
               return jsonify('Your password don\'t match ')


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data['email']
    password = data['password']
    my_cursor = mydb.cursor(MySQLdb.cursors.DictCursor)
    my_cursor.execute('''SELECT * FROM  registration WHERE email =%s''', [email])
    user = my_cursor.fetchone()
    if user and sha256.verify(password, user[5]):
        access_token = create_access_token(identity=user)
        return jsonify(access_token=access_token)
    else:
        return jsonify('incorrect password or email')    






   


#adminroute
from admin import *

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)