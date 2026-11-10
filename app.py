from flask import Flask, render_template, abort, request, redirect, url_for, flash
from database import get_connection, init_db

app = Flask(__name__)

app.secret_key = "key-secreta"

init_db()

def formatear_precio(valor):
    return f"{valor:,}".replace(",", ".")


app.add_template_filter(formatear_precio, "precio")


def obtener_categorias(conn):
    return conn.execute("SELECT * FROM categorias ORDER BY nombre").fetchall()


def validar_producto(conn, nombre, precio_texto, categoria_texto, producto_id=None):
    """Devuelve (nombre, precio, categoria_id, errores). Si hay errores, no guardes nada."""
    errores = []
    nombre = nombre.strip()
    precio = None
    categoria = None

    # Nombre
    if not nombre:
        errores.append("El nombre es obligatorio")
    elif len(nombre) > 100:
        errores.append("El nombre no puede superar los 100 caracteres")
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

    # Categoría
    try:
        categoria = conn.execute(
            "SELECT * FROM categorias WHERE id = ?", (int(categoria_texto),)
        ).fetchone()
    except ValueError:
        categoria = None
    if categoria is None:
        errores.append("Selecciona una categoría válida")

    # Precio
    try:
        precio = int(precio_texto)
    except ValueError:
        errores.append("El precio debe ser un número entero")
    else:
        if categoria is not None:
            if precio < categoria["precio_min"]:
                errores.append(
                    f"En {categoria['nombre']} el precio mínimo es "
                    f"${formatear_precio(categoria['precio_min'])}"
                )
            elif precio > categoria["precio_max"]:
                errores.append(
                    f"En {categoria['nombre']} el precio máximo es "
                    f"${formatear_precio(categoria['precio_max'])}"
                )
        elif precio <= 0:
            errores.append("El precio debe ser mayor que cero")

    categoria_id = categoria["id"] if categoria else None
    return nombre, precio, categoria_id, errores


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
    productos = conn.execute(
        """
        SELECT p.*, c.nombre AS categoria
        FROM productos p
        JOIN categorias c ON c.id = p.categoria_id
        ORDER BY p.id
        """
    ).fetchall()
    conn.close()
    return render_template("catalogo.html", productos=productos)


@app.route("/producto/nuevo", methods=["GET", "POST"])
def nuevo_producto():
    conn = get_connection()
    categorias = obtener_categorias(conn)

    if request.method == "POST":
        nombre_form = request.form.get("nombre", "")
        precio_form = request.form.get("precio", "")
        categoria_form = request.form.get("categoria_id", "")

        nombre, precio, categoria_id, errores = validar_producto(
            conn, nombre_form, precio_form, categoria_form
        )

        if errores:
            conn.close()
            for error in errores:
                flash(error, "error")
            return (
                render_template(
                    "nuevo.html",
                    nombre=nombre_form,
                    precio=precio_form,
                    categoria_id=categoria_form,
                    categorias=categorias,
                ),
                400,
            )

        conn.execute(
            "INSERT INTO productos (nombre, precio, categoria_id) VALUES (?, ?, ?)",
            (nombre, precio, categoria_id),
        )
        conn.commit()
        conn.close()
        flash("Producto agregado correctamente", "success")
        return redirect(url_for("catalogo"))

    conn.close()
    return render_template(
        "nuevo.html", nombre="", precio="", categoria_id="", categorias=categorias
    )


@app.route("/producto/<int:producto_id>")
def detalle(producto_id):
    conn = get_connection()
    producto = conn.execute(
        """
        SELECT p.*, c.nombre AS categoria
        FROM productos p
        JOIN categorias c ON c.id = p.categoria_id
        WHERE p.id = ?
        """,
        (producto_id,),
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

    categorias = obtener_categorias(conn)

    if request.method == "POST":
        nombre_form = request.form.get("nombre", "")
        precio_form = request.form.get("precio", "")
        categoria_form = request.form.get("categoria_id", "")

        nombre, precio, categoria_id, errores = validar_producto(
            conn, nombre_form, precio_form, categoria_form, producto_id
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
                    categoria_id=categoria_form,
                    categorias=categorias,
                ),
                400,
            )

        conn.execute(
            "UPDATE productos SET nombre = ?, precio = ?, categoria_id = ? WHERE id = ?",
            (nombre, precio, categoria_id, producto_id),
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
        categoria_id=producto["categoria_id"],
        categorias=categorias,
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

@app.errorhandler(404)
def pagina_no_encontrada(error):
    return render_template("404.html"), 404
