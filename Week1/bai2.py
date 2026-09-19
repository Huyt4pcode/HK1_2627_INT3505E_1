from flask import Flask, request, jsonify
app = Flask(__name__)

@app.route("/info")
def info():
    return jsonify({
        "course": "SOA",
        "topic": "Flask API"
    }), 200

@app.route("/students", methods=["POST"])
def students():
    data = request.get_json(silent=True) or {}
    return jsonify({
        "received_student": data
    }), 200

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)