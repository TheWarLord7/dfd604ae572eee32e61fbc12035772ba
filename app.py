from flask import Flask, request, jsonify
import uuid

app = Flask(__name__)

# Mock Controller for demonstration purposes
class Controller:
    @staticmethod
    def get_context(user_uuid, limit_str):
        return {"context": f"Retrieved context for {user_uuid} with {limit_str}"}
    
    @staticmethod
    def get_identity():
        return str(uuid.uuid4())

@app.route('/api/v1/ask/', methods=['POST'])
def ask():
    body = request.get_json()

    user_uuid = body.get('uuid')
    query = body.get('query')

    # Connect internal body['query']
    
    return jsonify({"success": True, "message": "Query received", "uuid": user_uuid})

@app.route('/api/v1/context/', methods=['POST'])
def context():
    body = request.get_json()

    # Fixing the function name to 'context' instead of 'ask' which was a duplicate
    return jsonify(Controller.get_context(body['uuid'].replace('-',''), " LIMIT 10"))

@app.route('/auth/v1/connect', methods=['POST'])
def connect():
    body = request.get_json()

    return jsonify({'uuid': Controller.get_identity()})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
