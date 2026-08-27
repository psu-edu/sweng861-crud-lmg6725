from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify({"status": "ok"})

@app.route('/api/hello')
def hello():
    return jsonify({"message": "Hello, World!"})

if __name__ == '__main__':
    app.run(debug=True)