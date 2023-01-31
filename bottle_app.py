# A very simple Bottle Hello World app for you to get started with...
import os
from bottle import default_app, route, run, redirect

@route('/')
def get_index():
    redirect('/public')

@route('/public')
def get_public():
    return 'This public message should be shown to everyone!'

@route('/secret')
def get_secret():
    return 'This secret message should only be shown to authorized people!'

@route('/login')
def get_login():
    return "ok, it looks like you logged in" 

@route('/logout')
def get_logout():
    return "ok, it looks like you logged out"

if 'PYTHONANYWHERE_DOMAIN' in os.environ:
    application = default_app()
else:
    run(host='localhost', port=8080)
    