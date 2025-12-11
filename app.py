from flask import Flask, render_template, request, redirect, url_for, send_file, flash
import sqlite3
import csv
import io
from pathlib import Path

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "data" / "wishlist.db"
DB_PATH.parent.mkdir(exist_ok=True)

app = Flask(__name__)
app.secret_key = "troque_esta_chave_para_producao"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS wishes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT,
                wish_text TEXT NOT NULL,
                fulfilled INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    conn.close()

init_db()

@app.route("/", methods=["GET"])
def index():
    conn = get_db_connection()
    wishes = conn.execute("SELECT * FROM wishes ORDER BY created_at DESC").fetchall()
    conn.close()
    return render_template("index.html", wishes=wishes)

@app.route("/add", methods=["POST"])
def add_wish():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    wish_text = request.form.get("wish_text", "").strip()

    if not name or not wish_text:
        flash("Por favor preencha seu nome e o desejo.", "error")
        return redirect(url_for("index"))

    conn = get_db_connection()
    with conn:
        conn.execute(
            "INSERT INTO wishes (name, email, wish_text) VALUES (?, ?, ?)",
            (name, email, wish_text)
        )
    flash("Desejo enviado ao Papai Noel com sucesso 🎅", "success")
    return redirect(url_for("index"))

@app.route("/toggle/<int:wish_id>", methods=["POST"])
def toggle_fulfilled(wish_id):
    conn = get_db_connection()
    cur = conn.execute("SELECT fulfilled FROM wishes WHERE id = ?", (wish_id,))
    row = cur.fetchone()
    if row is None:
        flash("Desejo não encontrado.", "error")
        conn.close()
        return redirect(url_for("index"))
    new_val = 0 if row["fulfilled"] else 1
    with conn:
        conn.execute("UPDATE wishes SET fulfilled = ? WHERE id = ?", (new_val, wish_id))
    conn.close()
    return redirect(url_for("index"))

@app.route("/delete/<int:wish_id>", methods=["POST"])
def delete_wish(wish_id):
    conn = get_db_connection()
    with conn:
        conn.execute("DELETE FROM wishes WHERE id = ?", (wish_id,))
    conn.close()
    flash("Desejo removido.", "info")
    return redirect(url_for("index"))

@app.route("/export/csv", methods=["GET"])
def export_csv():
    conn = get_db_connection()
    rows = conn.execute("SELECT id, name, email, wish_text, fulfilled, created_at FROM wishes ORDER BY created_at DESC").fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "name", "email", "wish_text", "fulfilled", "created_at"])
    for r in rows:
        writer.writerow([r["id"], r["name"], r["email"], r["wish_text"], r["fulfilled"], r["created_at"]])
    output.seek(0)

    return send_file(io.BytesIO(output.getvalue().encode("utf-8")),
                     mimetype="text/csv",
                     download_name="wishlist_export.csv",
                     as_attachment=True)

if __name__ == "__main__":
    # Modo de desenvolvimento — para produção rode com um WSGI server.
    app.run(host="0.0.0.0", port=5000, debug=True)
