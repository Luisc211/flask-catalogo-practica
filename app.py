from flask import Flask, render_template, abort
from database import get_connection, init_db

app = Flask(__name__)

init_db()

@app.route("/")
def inicio():
    return "¡Hola, Flask!"

@app.route("/catalogo")
def catalogo():
    conn = get_connection()
    productos = conn.execute("SELECT * FROM productos").fetchall()
    conn.close()
    return render_template("catalogo.html", productos=productos)


@app.route("/producto/<int:producto_id>")
def detalle(producto_id):
    conn = get_connection()
    producto = conn.execute(
        "SELECT * FROM productos WHERE id = ?", (producto_id,)
    ).fetchone()
    conn.close()
    if producto is None:
        abort(404)
    return render_template("detalle.html", producto=producto)