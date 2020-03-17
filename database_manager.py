import sqlite3
from structures import Object3D, Matrix
import data_handling

class DatabaseManager():
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_database()

    def close_database(self):
        self.conn.close()

    def create_database(self):
        object_table = '''
            CREATE TABLE IF NOT EXISTS ObjectData (
                name TEXT PRIMARY KEY,
                colour TEXT,
                points TEXT,
                lines TEXT,
                surfaces TEXT
            )
            '''
        self.cursor.execute(object_table)
        print('SUCCESS: Database \'ObjectData\' built')

        users_table = '''
            CREATE TABLE IF NOT EXISTS UserData (
                username TEXT PRIMARY KEY,
                password TEXT,
                registered_time TEXT,
                login_time TEXT,
                total_logins INTEGER
            )
            '''
        self.cursor.execute(users_table)
        print('SUCCESS: Database \'UserData\' built')
        self.conn.commit()

    def save_objects(self, objects):
        for object_3d in objects.values():
            sql = 'INSERT OR REPLACE INTO ObjectData VALUES (?,?,?,?,?)'
            self.cursor.execute(sql, [object_3d.name, str(object_3d.colour), str(data_handling.v_strip_2d_array(object_3d.points.access_matrix(), 3)), str(object_3d.lines), str(object_3d.surfaces)])
        self.conn.commit()
        print('SUCCESS: Object data saved')

    def import_objects(self, engine):
        for name, colour, points, lines, surfaces in self.cursor.execute('SELECT * FROM ObjectData'):
            object_3d = Object3D(name, colour)
            object_3d.add_points(Matrix(data_handling.string_to_2d_float_array(points, 3)))
            object_3d.add_lines(data_handling.string_to_2d_int_array(lines, 2))
            object_3d.add_surfaces(data_handling.string_to_2d_int_array(surfaces, 4))
            engine.add_object(object_3d)

    def add_user(self, username, password, registered_time):
        sql = 'INSERT OR REPLACE INTO UserData (username, password, registered_time, login_time, total_logins) VALUES (?,?,?,?,?)'
        self.cursor.execute(sql, [username, password, registered_time, None, 0])
        self.conn.commit()
        print('SUCCESS: New user added')

    def update_login_time(self, username, login_time):
        sql = 'UPDATE UserData SET login_time = ?, total_logins = total_logins + 1 WHERE username = ?'
        self.cursor.execute(sql, [login_time, username])
        self.conn.commit()

    def query_field(self, select_field, query_field, query_value):
        sql = 'SELECT '+ select_field +' FROM UserData WHERE ' + query_field +' = ?'
        self.cursor.execute(sql, [query_value])
        return self.cursor.fetchone()[0]

    def check_user_existance(self, entered_username, entered_password):
        exists = False
        sql = 'SELECT username, COUNT(*) FROM UserData WHERE EXISTS (SELECT * FROM UserData WHERE username = ? AND password = ?)'
        for username, count in self.cursor.execute(sql, [entered_username, entered_password]):
            if count > 0:
                exists = True
        return exists