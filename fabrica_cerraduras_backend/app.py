import mysql.connector
from flask import Flask, jsonify, request  # Importamos lo necesario de Flask
from flask_cors import CORS  # Para permitir comunicación con el frontend
from database import (
    get_db_connection,
)  # Importamos nuestra función para conectar a la BD

# Crea una instancia de la aplicación Flask
app = Flask(__name__)

# Configura CORS (Cross-Origin Resource Sharing)
# Esto es crucial para que tu frontend (que probablemente se ejecutará en un puerto diferente, ej. 3000)
# pueda hacer peticiones a tu backend (ej. puerto 5000).
# En desarrollo, permitimos todas las conexiones.
# En producción, esto debería ser más restrictivo (ej. CORS(app, origins="http://tu-dominio-frontend.com"))
CORS(app)

# --- RUTAS (ENDPOINTS) ---


# Ruta de ejemplo para probar que el servidor funciona
@app.route("/", methods=["GET"])
def home():
    return "¡Bienvenido a la API de Fabrica de Cerraduras!"


# --- Rutas para INSUMOS ---


# Endpoint para OBTENER TODOS los insumos
@app.route("/api/insumos", methods=["GET"])
def get_insumos():
    conn = get_db_connection()  # Obtenemos una conexión a la BD
    if conn is None:  # Si la conexión falló
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500

    # Creamos un cursor. dictionary=True nos permite obtener los resultados como diccionarios,
    # lo que es más fácil de manejar en Python y convertir a JSON.
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM insumos")  # Ejecutamos la consulta SQL
        insumos = cursor.fetchall()  # Obtenemos todos los resultados
        return jsonify(insumos)  # Devolvemos los insumos como JSON
    except Exception as e:
        # Si ocurre algún error en la consulta, lo capturamos y devolvemos un mensaje de error 500
        print(f"Error al obtener insumos: {e}")
        return jsonify({"error": "Error interno del servidor al obtener insumos"}), 500
    finally:
        # Este bloque se ejecuta siempre, haya error o no.
        # Asegura que el cursor y la conexión se cierren para liberar recursos.
        cursor.close()
        conn.close()


# Endpoint para OBTENER UN INSUMO por su ID
# <int:id_insumo> en la URL captura un número entero y lo pasa como argumento a la función.
@app.route("/api/insumos/<int:id_insumo>", methods=["GET"])
def get_insumo(id_insumo):
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500
    cursor = conn.cursor(
        dictionary=True
    )  # dictionary=True para resultados como diccionarios
    try:
        # Usamos %s como placeholder para evitar inyección SQL.
        # Los valores se pasan como una tupla en el segundo argumento de execute().
        cursor.execute("SELECT * FROM insumos WHERE idInsumo = %s", (id_insumo,))
        insumo = cursor.fetchone()  # fetchone() para obtener un solo resultado
        if insumo:
            return jsonify(insumo)
        # Si no se encuentra el insumo, devolvemos un 404 Not Found
        return jsonify({"message": "Insumo no encontrado"}), 404
    except Exception as e:
        print(f"Error al obtener insumo por ID: {e}")
        return jsonify({"error": "Error interno del servidor al obtener insumo"}), 500
    finally:
        cursor.close()
        conn.close()


# Endpoint para AGREGAR un nuevo insumo
# Los datos se envían en el cuerpo de la petición (request.json) en formato JSON.
@app.route("/api/insumos", methods=["POST"])
def add_insumo():
    new_insumo_data = request.json  # Captura los datos JSON enviados en la petición
    nombre = new_insumo_data.get("nombreInsumo")
    cantidad = new_insumo_data.get("cantidadInsumo")

    # Validación básica: asegurarse de que los datos requeridos existen
    if (
        not nombre or cantidad is None
    ):  # cantidad puede ser 0, por eso no solo 'if not cantidad'
        return (
            jsonify({"error": "Nombre y cantidad del insumo son requeridos"}),
            400,
        )  # 400 Bad Request

    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500
    cursor = conn.cursor()  # No necesitamos dictionary=True para INSERT

    try:
        cursor.execute(
            "INSERT INTO insumos (nombreInsumo, cantidadInsumo) VALUES (%s, %s)",
            (nombre, cantidad),
        )
        conn.commit()  # Confirma los cambios en la base de datos

        # Opcional: Devolver el ID del nuevo insumo
        return (
            jsonify({"message": "Insumo añadido exitosamente", "id": cursor.lastrowid}),
            201,
        )  # 201 Created
    except Exception as e:
        conn.rollback()  # Si hay un error, deshace los cambios para mantener la integridad
        print(f"Error al añadir insumo: {e}")
        return jsonify({"error": "Error interno del servidor al añadir insumo"}), 500
    finally:
        cursor.close()
        conn.close()


# Endpoint para ACTUALIZAR un insumo existente por su ID
# Puede recibir el nombre, la cantidad o ambos para actualizar.
@app.route("/api/insumos/<int:id_insumo>", methods=["PUT"])
def update_insumo(id_insumo):
    updated_data = request.json  # Datos JSON con las propiedades a actualizar
    nombre = updated_data.get("nombreInsumo")
    cantidad = updated_data.get("cantidadInsumo")

    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500
    cursor = conn.cursor()

    try:
        # Construimos la consulta UPDATE dinámicamente según los datos recibidos
        query_parts = []
        params = []

        if nombre:
            query_parts.append("nombreInsumo = %s")
            params.append(nombre)
        if cantidad is not None:  # Permitir 0 como cantidad válida
            query_parts.append("cantidadInsumo = %s")
            params.append(cantidad)

        if (
            not query_parts
        ):  # Si no se proporcionó ni nombre ni cantidad para actualizar
            return jsonify({"error": "No se proporcionaron datos para actualizar"}), 400

        query = "UPDATE insumos SET " + ", ".join(query_parts) + " WHERE idInsumo = %s"
        params.append(id_insumo)  # Añadimos el ID al final de los parámetros

        cursor.execute(query, tuple(params))  # Ejecutamos la consulta
        conn.commit()

        if cursor.rowcount == 0:  # rowcount indica cuántas filas fueron afectadas
            # Si rowcount es 0, el insumo no existe o no hubo cambios
            return jsonify({"message": "Insumo no encontrado o sin cambios"}), 404
        return jsonify({"message": "Insumo actualizado exitosamente"}), 200
    except Exception as e:
        conn.rollback()
        print(f"Error al actualizar insumo: {e}")
        return (
            jsonify({"error": "Error interno del servidor al actualizar insumo"}),
            500,
        )
    finally:
        cursor.close()
        conn.close()


# Endpoint para ELIMINAR un insumo por su ID
@app.route("/api/insumos/<int:id_insumo>", methods=["DELETE"])
def delete_insumo(id_insumo):
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM insumos WHERE idInsumo = %s", (id_insumo,))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"message": "Insumo no encontrado"}), 404
        return jsonify({"message": "Insumo eliminado exitosamente"}), 200
    except Exception as e:
        conn.rollback()
        print(f"Error al eliminar insumo: {e}")
        return jsonify({"error": "Error interno del servidor al eliminar insumo"}), 500
    finally:
        cursor.close()
        conn.close()


# Endpoint para llamar al Stored Procedure sp_inventario_insumos
@app.route("/api/insumos/inventario", methods=["POST"])
def inventario_insumos():
    data = request.json
    id_insumo = data.get("idInsumo")
    cantidad_cambiar = data.get(
        "cantidadCambiar"
    )  # Puede ser positivo (sumar) o negativo (restar)

    if id_insumo is None or cantidad_cambiar is None:
        return jsonify({"error": "idInsumo y cantidadCambiar son requeridos"}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500
    cursor = conn.cursor()
    try:
        # callproc() es el método para ejecutar stored procedures
        cursor.callproc("sp_inventario_insumos", (id_insumo, cantidad_cambiar))
        conn.commit()

        # Opcional: Consultar la nueva cantidad del insumo para devolverla en la respuesta
        """Nota: Los resultados de callproc a veces necesitan que se obtengan los resultados del SP
         con stored_results(), pero para un simple UPDATE, una nueva SELECT es más sencilla."""
        cursor.execute(
            "SELECT cantidadInsumo FROM insumos WHERE idInsumo = %s", (id_insumo,)
        )
        new_cantidad = (
            cursor.fetchone()
        )  # Obtiene el primer (y único) resultado de la consulta

        if new_cantidad:
            # new_cantidad es una tupla (cantidad_valor,), así que accedemos con [0]
            return (
                jsonify(
                    {
                        "message": "Inventario de insumo actualizado",
                        "nueva_cantidad": new_cantidad[0],
                    }
                ),
                200,
            )
        return (
            jsonify(
                {
                    "message": "Insumo no encontrado después de la actualización (posiblemente ID incorrecto)"
                }
            ),
            404,
        )
    except mysql.connector.Error as err:
        conn.rollback()
        # Captura errores específicos de MySQL, incluyendo los SIGNAL SQLSTATE de tus SPs
        return (
            jsonify(
                {
                    "error": f"Error en procedimiento almacenado 'sp_inventario_insumos': {err}"
                }
            ),
            500,
        )
    except Exception as e:
        conn.rollback()
        print(f"Error general al actualizar inventario de insumo: {e}")
        return (
            jsonify({"error": "Error interno del servidor al actualizar inventario"}),
            500,
        )
    finally:
        cursor.close()
        conn.close()


# --- Nuevas Rutas para ARTICULOS y PRODUCCIÓN ---


# Endpoint para OBTENER TODOS los artículos y su stock actual
@app.route("/api/articulos", methods=["GET"])
def get_articulos():
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500
    cursor = conn.cursor(dictionary=True)  # Queremos resultados como diccionarios
    try:
        # Aquí consultamos la tabla 'articulos' y 'stock_articulos'
        # para mostrar el nombre del artículo, tipo y la cantidad disponible.
        cursor.execute(
            """
            SELECT a.idArticulo, a.nombreArticulo, a.tipoArticulo, sa.cantidadDisponible
            FROM articulos a
            JOIN stock_articulos sa ON a.idArticulo = sa.idArticulo
        """
        )
        articulos = cursor.fetchall()  # Obtenemos todos los resultados
        return jsonify(articulos)
    except Exception as e:
        print(f"Error al obtener artículos: {e}")
        return (
            jsonify({"error": "Error interno del servidor al obtener artículos"}),
            500,
        )
    finally:
        cursor.close()
        conn.close()


# Endpoint para llamar al Stored Procedure sp_produccion_articulos
# Este endpoint es crucial para la lógica de negocio de la fábrica.
@app.route("/api/articulos/producir", methods=["POST"])
def producir_articulo():
    data = request.json  # Esperamos un JSON con 'idArticulo' y 'cantidadProducir'
    id_articulo = data.get("idArticulo")
    cantidad_producir = data.get("cantidadProducir")

    # Validaciones previas
    if id_articulo is None or cantidad_producir is None:
        return jsonify({"error": "idArticulo y cantidadProducir son requeridos"}), 400
    if not isinstance(cantidad_producir, int) or cantidad_producir <= 0:
        return (
            jsonify({"error": "cantidadProducir debe ser un número entero positivo"}),
            400,
        )

    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500
    cursor = conn.cursor()
    try:
        # Llama al stored procedure sp_produccion_articulos
        # El SP es el que manejará la lógica de descontar insumos y verificar stock.
        cursor.callproc("sp_produccion_articulos", (id_articulo, cantidad_producir))
        conn.commit()  # Confirma los cambios realizados por el SP

        # Opcional: Recuperar el nuevo stock del artículo para devolverlo en la respuesta
        # Esto te da una confirmación visual de que la producción afectó el stock.
        cursor.execute(
            "SELECT cantidadDisponible FROM stock_articulos WHERE idArticulo = %s",
            (id_articulo,),
        )
        new_stock = cursor.fetchone()

        message = f"Producción de {cantidad_producir} unidades del artículo {id_articulo} completada."
        response_data = {"message": message}
        if new_stock:
            response_data["nuevo_stock_articulo"] = new_stock[0]

        return jsonify(response_data), 200

    except mysql.connector.Error as err:
        conn.rollback()  # Si el SP lanzó un error (como insumos insuficientes), se revierte la transacción.
        print(
            f"Error MySQL en sp_produccion_articulos: {err}"
        )  # Para depuración en la terminal
        # Devolvemos el error específico del SP al frontend.
        return (
            jsonify(
                {"error": f"Error en procedimiento almacenado de producción: {err}"}
            ),
            500,
        )
    except Exception as e:
        conn.rollback()
        print(f"Error general al producir artículo: {e}")
        return (
            jsonify({"error": "Error interno del servidor al producir artículo"}),
            500,
        )
    finally:
        cursor.close()
        conn.close()


# Endpoint para OBTENER INSUMOS BAJO STOCK (usa la vista v_insumos_bajo_stock)
@app.route("/api/reportes/insumos_bajo_stock", methods=["GET"])
def get_insumos_bajo_stock():
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500
    cursor = conn.cursor(dictionary=True)  # Queremos resultados como diccionarios
    try:
        # Simplemente seleccionamos de la vista. La lógica de "bajo stock" ya está en la vista.
        cursor.execute("SELECT * FROM v_insumos_bajo_stock")
        insumos = cursor.fetchall()
        return jsonify(insumos)
    except Exception as e:
        print(f"Error al obtener insumos bajo stock: {e}")
        return (
            jsonify(
                {"error": "Error interno del servidor al obtener insumos bajo stock"}
            ),
            500,
        )
    finally:
        cursor.close()
        conn.close()


# Iniciar la aplicación Flask
# El if __name__ == '__main__': asegura que esto solo se ejecute cuando corras este archivo directamente.
if __name__ == "__main__":
    # app.run(debug=True, port=5000)
    # debug=True: recarga el servidor automáticamente con los cambios y muestra errores detallados.
    # port=5000: El puerto donde tu servidor Flask estará escuchando.
    app.run(debug=True, port=5000)
