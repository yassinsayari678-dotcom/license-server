from flask import Flask, request, jsonify
import json, os, hashlib

app = Flask(__name__)
LICENSES_FILE = "licenses.json"
ADMIN_SECRET = "yassin-secret-2024"

def load_licenses():
    if os.path.exists(LICENSES_FILE):
        with open(LICENSES_FILE) as f:
            return json.load(f)
    return {}

def save_licenses(data):
    with open(LICENSES_FILE, "w") as f:
        json.dump(data, f)

@app.route("/verify", methods=["POST"])
def verify():
    data = request.json
    key = data.get("key")
    machine = data.get("machine_id")
    licenses = load_licenses()

    if key not in licenses:
        return jsonify({"valid": False, "reason": "Key not found"})

    lic = licenses[key]
    if not lic["active"]:
        return jsonify({"valid": False, "reason": "Disabled"})

    if lic["machine_id"] is None:
        lic["machine_id"] = machine
        licenses[key] = lic
        save_licenses(licenses)
        return jsonify({"valid": True})
    elif lic["machine_id"] == machine:
        return jsonify({"valid": True})
    else:
        return jsonify({"valid": False, "reason": "Wrong machine"})

@app.route("/add_license", methods=["POST"])
def add_license():
    data = request.json
    if data.get("admin_secret") != ADMIN_SECRET:
        return jsonify({"error": "Unauthorized"}), 403
    key = data["key"]
    licenses = load_licenses()
    licenses[key] = {"machine_id": None, "active": True}
    save_licenses(licenses)
    return jsonify({"success": True})

@app.route("/")
def home():
    return "License Server is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
