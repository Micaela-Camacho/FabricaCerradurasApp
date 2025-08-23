# app.py
from flask import Flask
from flask_cors import CORS
from routes import (
    api,
)  # importa Blueprint, que contiene las rutas

# instancia de la aplicación Flask
app = Flask(__name__)

# CORS permite que el frontend se comunique con el backend
CORS(app)

# Registrar el Blueprint. para que la aplicación pueda usar todas las rutas definidas en 'routes.py'
app.register_blueprint(api)


# Ruta de ejemplo para probar que el servidor principal funciona
@app.route("/", methods=["GET"])
def home():
    return "¡Bienvenido a la API de Fabrica de Cerraduras!"


if __name__ == "__main__":
    # Inicia el servidor Flask en modo de depuración para que se reinicie
    # automáticamente con los cambios.
    app.run(debug=True, port=5000)
