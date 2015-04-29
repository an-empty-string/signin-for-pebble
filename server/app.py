from flask import Flask, jsonify, request, render_template, session, redirect
from db import *
import json
import random
import string
import datetime

config = json.load(open("config.json"))
app = Flask(__name__)
app.secret_key = config["secret-key"]

@app.route('/api/new_key.json')
def new_key():
    """
    Generate and return a new device/enrollment keypair. This is called by the Pebble
    app at first run.
    """
    auth_key = "".join([random.choice(string.ascii_lowercase + string.ascii_uppercase + "0123456789") for i in range(32)])
    enrollment_key = auth_key[:6]
    Device.create(auth_key=auth_key, enroll_key=enrollment_key)
    return jsonify(auth_key=auth_key, enrollment_token=enrollment_key)

@app.route('/api/<auth_key>/pending.json')
def pending_auth_requests(auth_key):
    pendings = sorted(list(filter(lambda k: not k.approved and not k.complete, Device.get(Device.auth_key == auth_key).owner.auth_requests)), key=lambda x: x.id, reverse=True)
    if not pendings:
        return jsonify(pending=[])
    else:
        return jsonify(pending=[pendings[0]._data])

@app.route('/api/<auth_key>/accept/<int:id>')
def accept_auth_request(auth_key, id):
    if list(filter(lambda k: k.id == id and not k.approved and not k.complete, Device.get(Device.auth_key == auth_key).owner.auth_requests)):
        AuthRequest.update(approved=True).where(AuthRequest.id == id).execute()
    return jsonify(ok=True)

@app.route('/api/<auth_key>/deny/<int:id>/')
def deny_auth_request(auth_key, id):
    if list(filter(lambda k: k.id == id and not k.approved and not k.complete, Device.get(Device.auth_key == auth_key).owner.auth_requests)):
        AuthRequest.update(approved=False, complete=True, completed_at=datetime.datetime.now()).where(AuthRequest.id == id).execute()
    return jsonify(ok=True)

@app.route('/api/<auth_key>/ok.json')
def ok(auth_key):
    if list(Device.select().where(Device.auth_key == auth_key)):
        return jsonify(ok=True)
    return jsonify(ok=False)

@app.route('/api/user/<int:uid>/service/<service>/request.json')
def new_auth_request(uid, service):
    ar = AuthRequest.create(user=User.get(User.id == uid), service=service)
    return jsonify(id=ar.id)

@app.route('/api/request/<int:rid>/status.json')
def req_status(rid):
    return jsonify(status=AuthRequest.get(AuthRequest.id == rid).approved)

@app.route('/')
def root():
    return render_template("index.html")

@app.route('/register/', methods=["GET", "POST"])
def reg():
    if request.method == "GET":
        return render_template("register.html")
    username = request.form["username"]
    enroll_key = request.form["enroll_key"]
    u = User.create(username=username, password="")
    Device.update(owner=u).where(Device.enroll_key == enroll_key).execute()
    session["username"] = username
    return render_template("dashboard.html")

@app.route('/login/')
def login():
    data = request.args.get('username', None)
    if not data:
        return render_template("login.html")

    user = User.get(User.username == data)
    ar = AuthRequest.create(user=user, service="Signin for Pebble")

    return render_template("login_pending.html", uid=user.id, username=data)

@app.route('/dashboard/')
def dashboard():
    things = sorted(list(filter(lambda k: k.complete, User.get(User.username == session["username"]).auth_requests)), key=lambda k: k.completed_at, reverse=True)
    return render_template("dashboard.html", stuff=things)

@app.route('/login_complete/<int:uid>/')
def login_complete(uid):
    u = User.get(User.id == uid)
    x = AuthRequest.select().where(AuthRequest.service == "Signin for Pebble", AuthRequest.user == u, AuthRequest.approved == True, AuthRequest.complete == False)
    if list(x):
        session["username"] = u.username
        AuthRequest.update(complete=True, completed_at=datetime.datetime.now()).where(AuthRequest.id == x[0].id).execute()
        return jsonify(approved=True)
    else:
        return jsonify(approved=False)

@app.route('/logout/')
def logout():
    del session["username"]
    return redirect('/')

app.run(debug=True)
