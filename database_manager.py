import sqlite3
from structures import Object3D, Matrix
import data_handling

class DatabaseManager():
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

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
        self.conn.commit()
        print('SUCCESS: Database \'ObjectData\' built')

    def save_objects(self, objects):
        for object_3d in objects.values():
            sql = 'REPLACE INTO ObjectData VALUES (?,?,?,?,?)'
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
