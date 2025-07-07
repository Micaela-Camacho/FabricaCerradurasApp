import mysql.connector  # Importamos el conector para MySQL
import os  # Para interactuar con variables de entorno
from dotenv import load_dotenv  # Para cargar las variables del archivo .env

# Carga las variables de entorno desde el archivo .env
# Esto debe ejecutarse al inicio para que las variables estén disponibles
load_dotenv()


def get_db_connection():
    """
    Esta función intenta establecer y devolver una conexión a la base de datos MySQL.
    Si la conexión falla, imprime un error y devuelve None.
    """
    try:
        # Intentamos conectar a la base de datos usando las credenciales del .env
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),  # Obtiene el host del .env
            user=os.getenv("DB_USER"),  # Obtiene el usuario del .env
            password=os.getenv("DB_PASSWORD"),  # Obtiene la contraseña del .env
            database=os.getenv("DB_NAME"),  # Obtiene el nombre de la BD del .env
        )
        return conn  # Si la conexión es exitosa, la devolvemos
    except mysql.connector.Error as err:
        # Si hay un error de conexión, lo imprimimos
        print(f"Error al conectar a la base de datos: {err}")
        return None  # Y devolvemos None para indicar que falló


# Este bloque solo se ejecuta si corres 'database.py' directamente
# Es útil para probar si tu conexión a la BD funciona antes de ejecutar toda la app Flask.
if __name__ == "__main__":
    print("Probando conexión a la base de datos...")
    connection = get_db_connection()
    if connection:
        print("Conexión exitosa a la base de datos!")
        connection.close()  # Es importante cerrar la conexión cuando ya no se usa
        print("Conexión cerrada.")
    else:
        print(
            "¡Falló la conexión a la base de datos! Revisa tus credenciales en .env y si MySQL está corriendo."
        )
