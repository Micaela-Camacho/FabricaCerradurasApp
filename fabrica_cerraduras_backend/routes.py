# routes.py
import mysql.connector
from flask import Blueprint, jsonify, request
from database import get_db_connection

# Blueprint llamado 'api' agrupa todas las rutas.
api = Blueprint("api", __name__)

# --- Rutas para INSUMOS ---


# Endpoint para OBTENER TODOS los insumos
@api.route("/api/insumos", methods=["GET"])
def get_insumos():
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500

    cursor = conn.cursor(dictionary=True)
    try:
        # Ejecuta la consulta SQL para seleccionar todos los insumos.
        cursor.execute("SELECT * FROM insumos")
        insumos = (
            cursor.fetchall()
        )  # fetchall() obtiene todos los resultados de la consulta.
        return jsonify(insumos)  # Devuelve la lista de insumos en formato JSON.
    except Exception as e:
        print(f"Error al obtener insumos: {e}")
        return jsonify({"error": "Error interno del servidor al obtener insumos"}), 500
    finally:
        # El bloque finally asegura que el cursor y la conexión se cierren
        # siempre, sin importar si hubo un error o no.
        cursor.close()
        conn.close()


# Endpoint para OBTENER UN INSUMO por su ID
@api.route("/api/insumos/<int:id_insumo>", methods=["GET"])
def get_insumo(id_insumo):
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500
    cursor = conn.cursor(dictionary=True)
    try:
        # Usa un placeholder (%s) para prevenir la inyección SQL, pasando el ID como un parámetro.
        cursor.execute("SELECT * FROM insumos WHERE idInsumo = %s", (id_insumo,))
        insumo = (
            cursor.fetchone()
        )  # fetchone() obtiene el primer resultado (o None si no existe).
        if insumo:
            return jsonify(insumo)
        return jsonify({"message": "Insumo no encontrado"}), 404
    except Exception as e:
        print(f"Error al obtener insumo por ID: {e}")
        return jsonify({"error": "Error interno del servidor al obtener insumo"}), 500
    finally:
        cursor.close()
        conn.close()


# Endpoint para AGREGAR un nuevo insumo
@api.route("/api/insumos", methods=["POST"])
def add_insumo():
    new_insumo_data = request.json  # Captura los datos JSON del cuerpo de la petición.
    nombre = new_insumo_data.get("nombreInsumo")
    cantidad = new_insumo_data.get("cantidadInsumo")

    # Validación básica de los datos.
    if not nombre or cantidad is None:
        return (
            jsonify({"error": "Nombre y cantidad del insumo son requeridos"}),
            400,
        )

    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO insumos (nombreInsumo, cantidadInsumo) VALUES (%s, %s)",
            (nombre, cantidad),
        )
        conn.commit()  # Confirma la transacción para guardar los cambios en la BD.
        return (
            jsonify({"message": "Insumo añadido exitosamente", "id": cursor.lastrowid}),
            201,
        )
    except Exception as e:
        conn.rollback()  # Si hay un error, deshace los cambios para conservar la integridad
        print(f"Error al añadir insumo: {e}")
        return jsonify({"error": "Error interno del servidor al añadir insumo"}), 500
    finally:
        cursor.close()
        conn.close()


# Endpoint para ACTUALIZAR un insumo existente por su ID
@api.route("/api/insumos/<int:id_insumo>", methods=["PUT"])
def update_insumo(id_insumo):
    updated_data = request.json
    nombre = updated_data.get("nombreInsumo")
    cantidad = updated_data.get("cantidadInsumo")

    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500
    cursor = conn.cursor()

    try:
        # Crea la consulta UPDATE dinámicamente.
        query_parts = []
        params = []
        if nombre:
            query_parts.append("nombreInsumo = %s")
            params.append(nombre)
        if cantidad is not None:
            query_parts.append("cantidadInsumo = %s")
            params.append(cantidad)

        if not query_parts:
            return jsonify({"error": "No se proporcionaron datos para actualizar"}), 400

        query = "UPDATE insumos SET " + ", ".join(query_parts) + " WHERE idInsumo = %s"
        params.append(id_insumo)

        cursor.execute(query, tuple(params))
        conn.commit()

        if (
            cursor.rowcount == 0
        ):  # rowcount es el número de filas afectadas por la última operación.
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
@api.route("/api/insumos/<int:id_insumo>", methods=["DELETE"])
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
@api.route("/api/insumos/inventario", methods=["POST"])
def inventario_insumos():
    data = request.json
    id_insumo = data.get("idInsumo")
    cantidad_cambiar = data.get("cantidadCambiar")

    if id_insumo is None or cantidad_cambiar is None:
        return jsonify({"error": "idInsumo y cantidadCambiar son requeridos"}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500
    cursor = conn.cursor()
    try:
        # callproc() es el método para ejecutar stored procedures.
        cursor.callproc("sp_inventario_insumos", (id_insumo, cantidad_cambiar))
        conn.commit()
        # Opcional: Consultar la nueva cantidad del insumo para la respuesta.
        cursor.execute(
            "SELECT cantidadInsumo FROM insumos WHERE idInsumo = %s", (id_insumo,)
        )
        new_cantidad = cursor.fetchone()

        if new_cantidad:
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
        print(f"Error MySQL en sp_inventario_insumos: {err}")
        return (
            jsonify({"error": str(err)}),
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


# --- Rutas para ARTICULOS y PRODUCCIÓN ---


# Endpoint para OBTENER TODOS los artículos y su stock actual
@api.route("/api/articulos", methods=["GET"])
def get_articulos():
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT a.idArticulo, a.nombreArticulo, a.tipoArticulo, sa.cantidadDisponible
            FROM articulos a
            JOIN stock_articulos sa ON a.idArticulo = sa.idArticulo
        """
        )
        articulos = cursor.fetchall()
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
@api.route("/api/articulos/producir", methods=["POST"])
def producir_articulo():
    data = request.json
    id_articulo = data.get("idArticulo")
    cantidad_producir = data.get("cantidadProducir")

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
        cursor.callproc("sp_produccion_articulos", (id_articulo, cantidad_producir))
        conn.commit()
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
        conn.rollback()
        print(f"Error MySQL en sp_produccion_articulos: {err}")
        return (
            jsonify({"error": str(err)}),
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
@api.route("/api/reportes/insumos_bajo_stock", methods=["GET"])
def get_insumos_bajo_stock():
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500
    cursor = conn.cursor(dictionary=True)
    try:
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
