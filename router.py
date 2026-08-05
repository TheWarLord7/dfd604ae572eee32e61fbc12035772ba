from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/v1/ask/', methods=['POST'])
def ask():
    body = request.get_json()

    # Connect internal body['query']

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)