from flask import Flask, render_template, abort, request, redirect, url_for, flash
from database import get_connection, init_db

app = Flask(__name__)

app.secret_key = "key-secreta"

init_db()

def validar_producto(conn, nombre, precio_texto, producto_id=None):
    """Devuelve (nombre, precio, errores). Si hay errores, no guardes nada."""
    errores = []
    nombre = nombre.strip()
    precio = None
    if not nombre:
        errores.append("El nombre es obligatorio")
    elif len(nombre) > 30:
        errores.append("El nombre no puede superar los 30 caracteres")
    else:
        if producto_id is None:
            repetido = conn.execute(
                "SELECT id FROM productos WHERE LOWER(nombre) = LOWER(?)",
                (nombre,),
            ).fetchone()
        else:
            repetido = conn.execute(
                "SELECT id FROM productos WHERE LOWER(nombre) = LOWER(?) AND id != ?",
                (nombre, producto_id),
            ).fetchone()
        if repetido:
            errores.append("Ya existe un producto con ese nombre")
    try:
        precio = int(precio_texto)
    except ValueError:
        errores.append("El precio debe ser un número entero")
    else:
        if precio <= 0:
            errores.append("El precio debe ser mayor que cero")
        elif precio > 100_000_000:
            errores.append("El precio es demasiado alto")
    return nombre, precio, errores

@app.route("/")
def inicio():
    conn = get_connection()
    total = conn.execute("SELECT COUNT(*) FROM productos").fetchone()[0]
    recientes = conn.execute(
        "SELECT * FROM productos ORDER BY id DESC LIMIT 3"
    ).fetchall()
    conn.close()
    return render_template("inicio.html", total=total, recientes=recientes)


@app.route("/catalogo")
def catalogo():
    conn = get_connection()
    productos = conn.execute("SELECT * FROM productos").fetchall()
    conn.close()
    return render_template("catalogo.html", productos=productos)


@app.route("/producto/nuevo", methods=["GET", "POST"])
def nuevo_producto():
    if request.method == "POST":
        nombre_form = request.form.get("nombre", "")
        precio_form = request.form.get("precio", "")
        conn = get_connection()
        nombre, precio, errores = validar_producto(conn, nombre_form, precio_form)
        if errores:
            conn.close()
            for error in errores:
                flash(error, "error")
            return (
                render_template("nuevo.html", nombre=nombre_form, precio=precio_form),
                400,
            )
        conn.execute(
            "INSERT INTO productos (nombre, precio) VALUES (?, ?)",
            (nombre, precio),
        )
        conn.commit()
        conn.close()
        flash("Producto agregado correctamente", "success")
        return redirect(url_for("catalogo"))
    return render_template("nuevo.html", nombre="", precio="")


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
        nombre_form = request.form.get("nombre", "")
        precio_form = request.form.get("precio", "")

        nombre, precio, errores = validar_producto(
            conn, nombre_form, precio_form, producto_id
        )

        if errores:
            conn.close()
            for error in errores:
                flash(error, "error")
            return (
                render_template(
                    "editar.html",
                    producto=producto,
                    nombre=nombre_form,
                    precio=precio_form,
                ),
                400,
            )

        conn.execute(
            "UPDATE productos SET nombre = ?, precio = ? WHERE id = ?",
            (nombre, precio, producto_id),
        )
        conn.commit()
        conn.close()
        flash("Producto actualizado correctamente", "success")
        return redirect(url_for("detalle", producto_id=producto_id))

    conn.close()
    return render_template(
        "editar.html",
        producto=producto,
        nombre=producto["nombre"],
        precio=producto["precio"],
    )


@app.route("/producto/<int:producto_id>/eliminar", methods=["POST"])
def eliminar_producto(producto_id):
    conn = get_connection()
    producto = conn.execute(
        "SELECT id FROM productos WHERE id = ?", (producto_id,)
    ).fetchone()
    if producto is None:
        conn.close()
        abort(404)
    conn.execute("DELETE FROM productos WHERE id = ?", (producto_id,))
    conn.commit()
    conn.close()
    flash("Producto eliminado correctamente", "success")
    return redirect(url_for("catalogo"))
