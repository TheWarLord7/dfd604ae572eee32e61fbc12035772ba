from connection import Connection
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

Controller = Connection()

@app.route('/api/v1/ask/', methods=['POST'])
def ask():
    body = request.get_json()
    return jsonify({'message':Controller.ask(body['uuid'], body['query']), 'success': True})


@app.route('/api/v1/context/', methods=['POST'])
def context():
    body = request.get_json()

    return jsonify(Controller.get_context(body['uuid'].replace('-',''), " LIMIT 10"))

@app.route('/auth/v1/connect', methods=['POST'])
def connect():
    body = request.get_json()

    return jsonify({'uuid': Controller.get_identity()})

@app.route('/')
def test():
    return '<h1>Test Page</h1>'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False) 