# un cursor es el objeto que usamos para interactuar con la base de datos
import pymysql.cursors
# esta clase nos dará una instancia de una conexión a nuestra base de datos
class MySQLConnection:
    def __init__(self, db):
        # cambiar el usuario y la contraseña según sea necesario
        connection = pymysql.connect(host = 'localhost',
                                    user = 'root', 
                                    password = 'admin123', 
                                    db = db,
                                    charset = 'utf8mb4',
                                    cursorclass = pymysql.cursors.DictCursor,
                                    autocommit = True)
        # establecer la conexión a la base de datos
        self.connection = connection
    # el método para consultar la base de datos
    def query_db(self, query, data=None):
        with self.connection.cursor() as cursor:
            try:
                print("Running Query:", cursor.mogrify(query, data))

                cursor.execute(query, data)

                if query.lower().find("insert") >= 0:
                    self.connection.commit()
                    return cursor.lastrowid

                elif query.lower().find("select") >= 0:
                    result = cursor.fetchall()
                    return result

                else:
                    self.connection.commit()

            except Exception as e:
                print("Algo sucedio y salió mal", e)
                return False

            finally:
                self.connection.close()
# connectToMySQL recibe la base de datos que estamos usando y la usa para crear una instancia de MySQLConnection
def connectToMySQL(db):
    return MySQLConnection(db)