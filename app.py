# A very simple Bottle Hello World app for you to get started with...
import hashlib
import json
import os, string, random
from bottle import default_app, route, run, redirect, request, response, template, get, post
from cryptography.fernet import Fernet

def to_bytes(s):
    return s.encode("utf-8")

def to_string(b):
    return b.decode("utf-8")

def encrypt(s, key):
    f = Fernet(to_bytes(key))
    return to_string(f.encrypt(to_bytes(s)))

def decrypt(s, key):
    f = Fernet(to_bytes(key))
    return to_string(f.decrypt(to_bytes(s)))

def hash_password(password, n=1):
    word = password
    for i in range(0,n):
        password_bytes = word.encode('utf-8')
        sha256 = hashlib.sha256()
        sha256.update(password_bytes)
        word = sha256.hexdigest()
    return word

def random_string(n):
    chars=string.ascii_letters + string.digits
    choices = random.choices(chars, k=n)
    result = ''.join(choices)
    return result

@route('/')
def get_index():
    redirect('/public')

@route('/public')
def get_public():
    return 'This public message should be shown to absolutely everyone!'

@get('/secret')
def get_secret():
    user = request.cookies.get("user","-")

    if user == "-":
        return 'You need to log in to enter a secret!'
    with open(f'data/{user}-profile.json',"r") as f:
        profile = json.load(f)
        key = profile['key']
    try:
        with open(f'data/{user}-secret.json',"r") as f:
            data = json.load(f)
            encrypted_secret = data['secret']
        secret = decrypt(encrypted_secret, key)
    except:
        secret = ""

    return template("secret.tpl", secret=secret)

@post('/secret')
def post_secret():
    session_id = request.cookies.get("session_id","-")
    user = '-'
    if os.path.isfile(session_id + "-session.json"):
        with open(session_id + "-session.json","w") as f:
            data = json.load(f)
            user = data['user']
    if user == "-":
        return 'You need to log in to enter a secret!'
    with open(f'data/{user}-profile.json',"r") as f:
        profile = json.load(f)
        favorite_color = profile['favorite_color']
        key = profile['key']
    secret = request.forms.get('secret', None)
    encrypted_secret = encrypt(secret, key)
    with open(f'data/{user}-secret.json',"w") as f:
        json.dump({
                'secret': encrypted_secret,
        }, f)
    return f"Your secret, {user}, is safe with me. I also like {favorite_color}."

@route('/counter')
def get_counter():
    n = int( request.cookies.get('counter', '0') )
    n = n + 1
    response.set_cookie("counter", str(n), path='/')
    return f"The counter is at {n}"

@get('/signup')
def get_signup():
    current_user = request.cookies.get("user","-")
    if current_user != "-":
        return "Sorry, you have to sign out first."
    return template("signup.tpl")

@post('/signup')
def post_signup():
    user = request.forms.get('user', None)
    if not user:
        return "Please enter a user name."
    password = request.forms.get('password', None)
    if not password:
        return "Please enter a password."
    password2 = request.forms.get('password', None)
    if not password2:
        return "Please enter the same password a second time."

    if len(user) < 3:
        return "Sorry, the user name requires at least 3 characters"
    if not user.isalnum():
        return "Sorry, the user name must be letters and digits"
    # if user exists, then that's an error
    if os.path.isfile(f'data/{user}-profile.json'):
        return "Sorry, that user name is taken"

    if len(password) < 6:
        return "Sorry, the password requires at least 6 characters"
    if not password.isalnum():
        return "Sorry, the password must be letters and digits"

    if password != password2:
        return "Sorry, the passwords must match"

    # store the password
    salt = random_string(20)
    hash_known_password = hash_password(password + salt, n=100000)

    # get favorite color
    favorite_color = request.forms.get('favorite_color', "unknown")
    if favorite_color.strip() == "":
        favorite_color = "unknown"

    with open(f'data/{user}-profile.json',"w") as f:
        json.dump({
                'salt': salt,
                'password-hash': hash_known_password,
                'favorite_color': favorite_color,
                'key': to_string(Fernet.generate_key())
            }, f)

    response.set_cookie("user", user, path='/')
    return f"ok, it looks like you logged in as {user}"

@get('/login')
def get_login():
    session_id = request.cookies.get("session_id","-")
    current_user = '-'
    if os.path.isfile(session_id + "-session.json"):
        with open(session_id + "-session.json","w") as f:
            data = json.load(f))
            current_user = data['user']
    if current_user != "-":
        return "Sorry, you have to sign out first."
    return template("login.tpl")


@post('/login')
def post_login():
    user = request.forms.get('user', None)
    if not user:
        return "Please enter a user name."
    password = request.forms.get('password', None)
    if not password:
        return "Please enter a password."

    # set default response to '-' if login fails
    session_id = str(random.randint(0,100000000000))
    response.set_cookie("session",session_id, path='/')

    #response.set_cookie("user", '-', path='/')
    with open(session_id + "-session.json","w") as f:
        data = {
            "user":'-'
            }
        json.dump(data,f))

    user = user.strip()

    # sanitize user name so we don't inject malicious filenames
    if not user.isalnum():
        return "Sorry, the user name must be letters and digits"

    # see if user exists
    filename = f'data/{user}-profile.json'
    if not os.path.isfile(filename):
        return "Sorry, no such user"

    # fetch password
    with open(f'data/{user}-profile.json',"r") as f:
        data = json.load(f)

    # check password correctness
    if data['password-hash'] != hash_password(password + data['salt'], n=100000):
        return "Sorry, the user name and password do not match"

    # successful login
    response.set_cookie("user", user, path='/')
    with open(session_id + "-session.json","w") as f:
        data = {
            "user":user
            }
        json.dump(data,f))
    return f"ok, it looks like you logged in as {user}"

@route('/logout')
def get_logout():
    return "ok, it looks like you logged out"
    with open(session_id + "-session.json","w") as f:
        data = {
            "user":'-'
            }
        json.dump(data,f))

if 'PYTHONANYWHERE_DOMAIN' in os.environ:
    application = default_app()
else:
    run(host='localhost', port=8080)
