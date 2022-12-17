#Name: Rushikesh Mahesh Bhagat
#UTA ID: 1001911486

from flask import Flask, flash, render_template, request, redirect,g,session
from numpy import broadcast

import pyodbc
import csv

from datetime import datetime

import requests

from settings_template import server, database, username, password, driver, mapQuest_key, mapQuest_url

import time


connstr = 'DRIVER='+driver+';SERVER=tcp:'+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password


from flask_socketio import SocketIO,send,join_room,emit
from flask_session import Session
from flask_cors import CORS
import pusher




app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
cors=CORS(app)
socketio = SocketIO(app,async_handlers=True, cors_allowed_origins='*')
Session(app)


###### SocketIO Routes ######
@socketio.on('message')
def handle_message(msg):
    print('message:',msg)
    send(msg, broadcast=True)

@app.route("/")
def index():
  return render_template('index.html',async_mode=socketio.async_mode)

@app.route("/chatroom", methods=['GET','POST'])
def chatroom():
  if request.method == 'POST' :
    session.pop('user',None)
    username = request.form['iname']
    session['user']=username
    room = request.form['iroom']
    getcategory = request.form['category']
    
    return render_template('chatroom.html', username=username, room=room, category=getcategory,async_mode=socketio.async_mode)

@app.before_request
def before_request():
    g.user = None
    if 'user' in session:
       g.user = session['user']

@socketio.on('join', namespace='/chatroom')
def join(message):
    room = message['room']
    join_room(room)
    emit('status', {'msg':  message['username'] + ' has entered the room.'}, room=room)

@socketio.on('text', namespace='/chatroom')
def text(message):
    room = message['room']
    emit('message', {'msg': message['username'] + ' : ' + message['msg']}, room=room)

#-------------Code for average score and score display---------------
@socketio.on('score', namespace='/chatroom')
def score(message):
    mylist = list()
    room = message['room']
    score = message['msg1']
    mylist.append(int(score))
    avg = sum(mylist)/len(mylist)

    emit('message',{'msg': message['msg'],'average':avg}, room=room)

@app.route("/logout")
def logout():
    session.pop('user',None)
    session.pop('room',None)
    return render_template('index.html',async_mode=socketio.async_mode)

@app.route("/endgame")
def endgame():
    session.pop('user',None)
    return render_template('index.html',async_mode=socketio.async_mode)


if __name__=='__main__':
    socketio.run(app,debug=True)


