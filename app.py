from flask import Flask, render_template, abort, request, redirect, url_for
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


@app.route("/producto/nuevo", methods=["GET", "POST"])
def nuevo_producto():
    if request.method == "POST":
        nombre = request.form["nombre"].strip()
        precio = int(request.form["precio"])
        conn = get_connection()
        conn.execute(
            "INSERT INTO productos (nombre, precio) VALUES (?, ?)",
            (nombre, precio),
        )
        conn.commit()
        conn.close()
        return redirect(url_for("catalogo"))
    return render_template("nuevo.html")


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

@app.route("/producto/<int:producto_id>/editar", methods=["GET", "POST"])
def editar_producto(producto_id):
    conn = get_connection()
    producto = conn.execute(
        "SELECT * FROM productos WHERE id = ?", (producto_id,)
    ).fetchone()
    if producto is None:
        conn.close()
        abort(404)
    if request.method == "POST":
        nombre = request.form["nombre"].strip()
        precio = int(request.form["precio"])
        conn.execute(
            "UPDATE productos SET nombre = ?, precio = ? WHERE id = ?",
            (nombre, precio, producto_id),
        )
        conn.commit()
        conn.close()
        return redirect(url_for("detalle", producto_id=producto_id))
    conn.close()
    return render_template("editar.html", producto=producto)
