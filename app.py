from flask import Flask,request,jsonify, session, abort, render_template, Blueprint
from flask_login import LoginManager, UserMixin, login_user, current_user, login_required, logout_user
from cassandra.cluster import Cluster
import json
import requests

app = Blueprint('app', __name__)
#app = Flask(__name__)
cluster = Cluster(contact_points=['172.17.0.2'],port=9042)
session = cluster.connect()

#Home page design
@app.route('/')
def hello():
        return("""<h1 style="text-align: center;">JOKES</h1> 
<h2 style="text-align: center;">Looking for funny jokes? Settle in: You're in the right place.</h2>
<img  style="display: block;margin: 30px auto;" src="https://www.dw.com/image/19227409_303.jpg">
<h3  style="text-align: center;">These jokes are guaranteed to make you laugh even on tough days</h3>
<p  style="text-align: center;">Did you know that laughing can actually improve your health? It strengthens your immune system, boosts mood, diminishes pain, and protects you from the damaging effects of stress.</p>
<body style="background-color: #98D2BF;"></body> """ )


@app.route('/joke',methods=['GET'])
def profile():
        rows = session.execute("""Select * From joke.stats""")
        result = []
        for r in rows:
                result.append({"id":r.id,"joke":r.joke})
        return jsonify(result)
 
@app.route('/joke/external', methods=['GET'])
def external():
        jokes ='https://official-joke-api.appspot.com/jokes/ten'
        resp = requests.get(jokes)
        if resp.ok:
                resp_jokes = resp.json()
                return jsonify(resp_jokes)
        else:
                print(resp.reason)

@app.route('/joke', methods=['POST'])
def create():
        session.execute( """INSERT INTO joke.stats(id,joke) VALUES( {},'{}')""".format(int(request.json['id']),request.json['joke']))
        return jsonify({'message': 'created: /records/{}'.format(request.json['id'])}), 200

@app.route('/joke', methods=['PUT'])
def update():
        session.execute( """UPDATE joke.stats SET joke= '{}' WHERE id={}""".format(request.json['joke'],int(request.json['id'])))
        return jsonify({'message': 'updated: /records/{}'.format(request.json['id'])}), 200

@app.route('/joke', methods=['DELETE'])
def delete(): 
	session.execute("""DELETE FROM joke.stats WHERE id={}""".format(int(request.json['id'])))
	return jsonify({'message': 'deleted: /records/{}'.format(request.json['id'])}), 200

if __name__ == '__main__':

        app.run(host='0.0.0.0', port=80)
