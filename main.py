
import csv
import os
import re
from datetime import datetime, timezone
from flask import Flask, Response, jsonify, request

BASE = os.path.dirname(os.path.abspath(__file__))
LEADS = os.path.join(
    "/tmp" if os.environ.get("VERCEL") else BASE,
    "leads.csv"
)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024  # 16 KB


@app.post("/api/contact")
def contact():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify(error="Invalid request"), 400

    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip()
    website = str(data.get("website", "")).strip()
    message = str(data.get("message", "")).strip()

    if not name or len(name) > 120:
        return jsonify(error="Enter a valid name"), 400

    if len(email) > 160 or not re.fullmatch(
        r"[^@\s]+@[^@\s]+\.[^@\s]+", email
    ):
        return jsonify(error="Enter a valid email"), 400

    if len(website) > 200 or len(message) > 2000:
        return jsonify(error="Input is too long"), 400

    row = [
        datetime.now(timezone.utc).isoformat(timespec="seconds"),
        name, email, website, message
    ]

    try:
        new_file = not os.path.exists(LEADS)

        with open(LEADS, "a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)

            if new_file:
                writer.writerow([
                    "time_utc", "name", "email",
                    "website", "message"
                ])

            writer.writerow(row)

    except OSError:
        app.logger.exception("Could not save contact request")
        return jsonify(
            error="Unable to save your request. Please try again."
        ), 500

    app.logger.info("New contact request received")
    return jsonify(ok=True), 200


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )
