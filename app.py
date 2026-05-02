import os
from flask import Flask, render_template, request, redirect
import sqlite3
import string
import random

app = Flask(__name__)


def get_db():
    conn = sqlite3.connect("urls.db")
    conn.execute("""CREATE TABLE IF NOT EXISTS urls
                 (id INTEGER PRIMARY KEY,
                  short_code TEXT UNIQUE,
                  long_url TEXT)""")
    return conn


def generate_code():
    return "".join(random.choices(string.ascii_letters + string.digits, k=6))


@app.route("/", methods=["GET", "POST"])
def home():
    short_url = None
    if request.method == "POST":
        long_url = request.form["long_url"]
        code = generate_code()
        db = get_db()
        db.execute(
            "INSERT INTO urls (short_code, long_url) VALUES (?, ?)", (code, long_url)
        )
        db.commit()
        db.close()
        short_url = request.host_url + code
    return render_template("index.html", short_url=short_url)


@app.route("/<code>")
def redirect_url(code):
    db = get_db()
    result = db.execute(
        "SELECT long_url FROM urls WHERE short_code = ?", (code,)
    ).fetchone()
    db.close()
    if result:
        return redirect(result[0])
    return "URL not found!", 404


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
