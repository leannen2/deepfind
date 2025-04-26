from flask import Flask, jsonify

app = Flask(__name__)

# Dummy endpoint
@app.route('/api/dummy', methods=['GET'])
def dummy_endpoint():
    return jsonify({
        'message': 'This is a dummy API response!',
        'status': 'success'
    })

if __name__ == '__main__':
    app.run(debug=True)
