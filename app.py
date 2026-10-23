from flask import Flask, render_template

app = Flask(__name__)

PRODUCTOS = [
    {"id": 1, "nombre": "Cuaderno", "precio": 5000},
    {"id": 2, "nombre": "Lapicero", "precio": 1500},
    {"id": 3, "nombre": "Borrador", "precio": 800},
]

@app.route("/")
def inicio():
    return "¡Hola, Flask!"

@app.route("/catalogo")
def catalogo():
    return render_template("catalogo.html", productos=PRODUCTOS)