from flask import Flask,render_template, request, session, Response, redirect
from database import connector
from model import entities
from sqlalchemy import or_, and_
import json
import time
import datetime
from operator import  itemgetter,attrgetter
import threading


db = connector.Manager()
engine = db.createEngine()



app = Flask(__name__)
logged_session_key='user'
key_users='users'
cache = {}

cache_message={}

i=0

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<content>')
def static_content(content):
    return render_template(content)


@app.route('/users', methods = ['GET'])
#@synchronized()
def get_users():
    data = []
    #synchronized(db_log)
    if key_users in cache and (datatime.now()-cache[key_users]['time']).total_seconds()<20:
        #Get Cache
        data = cache[key_users]['data']
    else:
        session = db.getSession(engine)
        dbResponse = session.query(entities.User).order_by(entities.User.username)
        session.close()
        data = dbResponse[:]
        #Set Cache
        cache[key_users]={'data': data, 'time': datetime.now()}
    return Response(json.dumps(data, cls=connector.AlchemyEncoder), mimetype='application/json')


@app.route('/users/<id>', methods = ['GET'])
def get_user(id):
    db_session = db.getSession(engine)
    users = db_session.query(entities.User).filter(entities.User.id == id)
    session.close()
    for user in users:
        js = json.dumps(user, cls=connector.AlchemyEncoder)
        return  Response(js, status=200, mimetype='application/json')

    message = { 'status': 404, 'message': 'Not Found'}
    return Response(message, status=404, mimetype='application/json')



@app.route('/users', methods = ['POST'])
def create_user():
    c =  json.loads(request.form['values'])
    user = entities.User(
        username=c['username'],
        name=c['name'],
        fullname=c['fullname'],
        password=c['password']
    )
    session = db.getSession(engine)
    session.add(user)
    session.commit()
    session.close()
    return 'Created User'

@app.route('/messages', methods = ['POST'])
def create_message():
    c = json.loads(request.form['values'])
    message = entities.Message(
        content=c['content'],
        user_from_id=c['user_from_id'],
        user_to_id=c['user_to_id'],
    )
    session = db.getSession(engine)
    session.add(message)
    session.commit()
    session.close()
    return 'Created Message'


@app.route('/messagesjs', methods = ['POST'])
def create_message_with_js():
    c =  json.loads(request.data)
    message = entities.Message(
        content=c['content'],
        user_from_id=c['user_from_id'],
        user_to_id=c['user_to_id'],
    )
    session = db.getSession(engine)
    session.add(message)
    session.commit()
    session.close()
    return 'Created Message'

@app.route('/authenticate', methods = ["POST"])
def authenticate():
    message = json.loads(request.data)
    username = message['username']
    password = message['password']
    #2. look in database
    db_session = db.getSession(engine)
    try:
        user = db_session.query(entities.User
            ).filter(entities.User.username == username
            ).filter(entities.User.password == password
            ).one()
        message = {'message': 'Authorized'}
        session['logged'] = user.id
        return Response(message, status=200, mimetype='application/json')
    except Exception:
        message = {'message': 'Unauthorized'}
        return Response(message, status=401, mimetype='application/json')




@app.route('/users', methods = ['PUT'])
def update_user():
    session = db.getSession(engine)
    id = request.form['key']
    user = session.query(entities.User).filter(entities.User.id == id).first()
    c =  json.loads(request.form['values'])
    for key in c.keys():
        setattr(user, key, c[key])
    session.add(user)
    session.commit()
    session.close()
    return 'Updated User'

@app.route('/users', methods = ['DELETE'])
def delete_user():
    id = request.form['key']
    session = db.getSession(engine)
    users = session.query(entities.User).filter(entities.User.id == id)
    for user in users:
        session.delete(user)
    session.commit()
    session.close()
    return "Deleted User"

# CRUD MESSAGES#########################################
@app.route('/messages', methods = ['DELETE'])
def delete_message():

    id = request.form['key']
    session = db.getSession(engine)
    messages = session.query(entities.Message).filter(entities.Message.id == id)
    for message in messages:
        session.delete(message)
    session.commit()
    session.close()
    return "Deleted Message"


@app.route('/messages', methods = ['PUT'])
def update_message():
    session = db.getSession(engine)
    id = request.form['key']
    message = session.query(entities.Message).filter(entities.Message.id == id).first()
    c =  json.loads(request.form['values'])
    for key in c.keys():
        setattr(message, key, c[key])
    session.add(message)
    session.commit()
    session.close()
    return 'Updated Message'

@app.route('/messages', methods = ['GET'])
def get_messages():
    global i 
    data = []
    lock = threading.Lock()
    lock.acquire()
    print(i)
    if key_message in cache and (datatime.now()-cache[key_message]['time']).total_seconds()<20:
        data = cache_message[key_message]['data']
    else:
        i = i + 1 
        session = db.getSession(engine)
        dbResponse = session.query(entities.Message)
        session.close()
        data = dbResponse[:]
        cache_message[key_users]={'data': data, 'time': datetime.now()} 
    lock.release()
    return Response (json.dumps(data, cls=connector.AlchemyEncoder), mimetype='application/json')

@app.route('/chats/<user_id>', methods = ['GET'])
def get_chats(user_id):
    sessiondb = db.getSession(engine)
    data = []
    users=sessiondb.query(entities.User).filter(entities.User.id != user_id)
    sessiondb.close()
    for user in users:
        data.append(user)
    return Response(json.dumps({'response' : data}, cls=connector.AlchemyEncoder), mimetype='application/json')


@app.route('/chats/<user_from_id>/<user_to_id>', methods = ['GET'])
def get_chat(user_from_id, user_to_id):
    session = db.getSession(engine)
    messages = session.query(entities.Message).filter(
            entities.Message.user_from_id == user_from_id).filter(entities.Message.user_to_id==user_to_id)

    messages2 = session.query(entities.Message).filter(
            entities.Message.user_from_id == user_to_id).filter(entities.Message.user_to_id==user_from_id)
    session.close()
    data = []
    for message in messages:
        data.append(message)
    for message2 in messages2:
        data.append(message2)
    data=sorted(data,key=attrgetter('sent_on'),reverse=False)
    return Response(json.dumps(data, cls=connector.AlchemyEncoder), mimetype='application/json')


@app.route('/current', methods = ['GET'])
def current():
    sessiondb = db.getSession(engine)
    user = sessiondb.query(entities.User).filter(entities.User.id == session['logged']).first()
    sessiondb.close()
    js = json.dumps(user, cls=connector.AlchemyEncoder)
    return Response(js, status=200, mimetype='application/json')

@app.route('/logout', methods=['GET'])
def logout():
    if (logged_session_key in session):
        session.pop(logged_session_key)
        
    response = {
            "msg" : "Logged out"
        }
    json_response= json.dumps(response)
    return Response(json_response, mimetype='application/json')


if __name__ == '__main__':
    app.secret_key = ".."
    app.run(port=8080, threaded=True, host=('127.0.0.1'))
