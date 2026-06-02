import os
import requests
from flask import Flask, render_template, request
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

API_KEY = os.getenv("ABUSEIPDB_API_KEY")

def check_ip(ip_address):
    url = "https://api.abuseipdb.com/api/v2/check"

    headers = {
        "Key": API_KEY,
        "Accept": "application/json"
    }

    params = {
        "ipAddress": ip_address,
        "maxAgeInDays": 90,
        "verbose": True
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)

        if response.status_code == 200:
            return response.json()["data"], None
        elif response.status_code == 422:
            return None, "Invalid IP address. Please enter a valid IPv4 or IPv6 address."
        elif response.status_code == 429:
            return None, "Daily API limit reached. Please try again tomorrow."
        else:
            return None, f"API error: {response.status_code}"

    except requests.RequestException:
        return None, "Could not reach the AbuseIPDB API. Check your internet connection."


def get_risk_level(score):
    if score == 0:
        return "Clean", "clean"
    elif score <= 25:
        return "Low Risk", "low"
    elif score <= 75:
        return "Suspicious", "suspicious"
    else:
        return "Malicious", "malicious"


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/check", methods=["POST"])
def check():
    ip_address = request.form.get("ip_address", "").strip()

    if not ip_address:
        return render_template("index.html", error="Please enter an IP address.")

    data, error = check_ip(ip_address)

    if error:
        return render_template("index.html", error=error)

    risk_label, risk_class = get_risk_level(data["abuseConfidenceScore"])

    return render_template(
        "result.html",
        data=data,
        risk_label=risk_label,
        risk_class=risk_class
    )


if __name__ == "__main__":
    app.run(debug=True)