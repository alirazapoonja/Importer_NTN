import sqlite3

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)
DB_FILE = "importers.db"
MAX_RESULTS = 50


def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/search")
def search():
    q = request.args.get("q", "").strip().lower()
    if len(q) < 3:
        return jsonify({"results": [], "message": "Type at least 3 letters."})

    # Every word the user types must appear somewhere in the importer name
    words = q.split()
    where = " AND ".join(["name_lc LIKE ?"] * len(words))
    params = [f"%{w}%" for w in words]

    conn = get_db()
    rows = conn.execute(
        f"SELECT name, ntn FROM importers WHERE {where} ORDER BY name LIMIT ?",
        params + [MAX_RESULTS],
    ).fetchall()
    conn.close()

    results = [{"name": r["name"], "ntn": r["ntn"]} for r in rows]
    return jsonify({"results": results, "limited": len(results) == MAX_RESULTS})


if __name__ == "__main__":
    app.run(debug=True)
