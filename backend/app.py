from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # this allows all origins by default

@app.route('/api/dummy', methods=['GET'])
def dummy_endpoint():
    return jsonify({
        'message': 'This is a dummy API response!',
        'status': 'success'
    })

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
