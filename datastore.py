import os
import sqlite3
import json
from sqlite3 import Error
from contextlib import closing
from threading import Timer, Lock


class Datastore:

    def __init__(self, file_path=None):

        if file_path == None:

            if os.path.exists(os.environ['HOME']):
                # if HOME is set on the environment
                file_path = os.path.join(
                    os.environ['HOME'], 'Datastore', 'default.db')
            else:
                file_path = "default.db"

        self.lock = Lock()  # for thread safety

        if type(file_path) == str:
            if not len(file_path):
                raise ValueError("please provide a valid filepath")
            self.file_path = file_path

            # fix the extension
            if self.file_path.split('.')[-1] != 'db':
                self.file_path += '.db'
            try:
                directory = os.path.dirname(self.file_path)
                if directory:
                    os.makedirs(directory)
            except FileExistsError:
                pass
            # except:
            #     print(e)
            #     raise Exception("could not create the directory")

            # Create a table if it doesn't exist
            self.execute_sqlite(
                "CREATE TABLE IF NOT EXISTS DatastoreTable (key TEXT, value TEXT)")

        else:
            raise TypeError("filepath should be a string")

    def create(self, key, value, time=None):
        # validation
        self.validate_key(key)
        if self.key_exists(key):
            raise ValueError("key already exists")
        value = self.validate_and_clean_value(value)
        # validation end

        # insert key value(recreated) pair in the the database
        try:
            self.execute_sqlite(
                "INSERT INTO DatastoreTable VALUES (?, ?)",
                (key, value))
        except:
            raise Exception("Could not create entry")

        if time != None:
            self.validate_time(time)
            Timer(float(time), self.delete, [key]).start()
        
        return True

    def read(self, key):
        self.validate_key(key)

        if self.key_exists(key):
            # search database for the key
            value = self.execute_sqlite(
                "SELECT value FROM DatastoreTable WHERE key=?",
                (key,), fetch=True)[0]
            cleaned_value = json.dumps(json.loads(value))
        else:
            raise ValueError("Key does not exist")

        return cleaned_value

    def delete(self, key):
        self.validate_key(key)
        if self.key_exists(key):
            try:
                # delete key value pair
                self.execute_sqlite(
                    "DELETE FROM DatastoreTable WHERE key=?",
                    (key,))
            except:
                raise Exception("could not delete the data")
        else:
            raise ValueError("key does not exists")

        return True

    # further isolate database operations

    def execute_sqlite(self, command, data=None, fetch=False):
        with self.lock:  # lock the method while operation is running
            try:
                with closing(sqlite3.connect(self.file_path)) as connection:
                    with closing(connection.cursor()) as cursor:
                        if fetch:
                            if data != None:
                                cursor.execute(command, data)
                                return_value = cursor.fetchone()
                            else:
                                cursor.execute(command)
                                return_value = cursor.fetchone()
                            # print(return_value)

                        else:
                            if data != None:
                                return_value = cursor.execute(command, data)
                            else:
                                return_value = cursor.execute(command)
                    connection.commit()
            except sqlite3.OperationalError:
                raise Exception("Could not operate on database file")

            return return_value

    def validate_time(self, time):
        if type(time) == bool:
            raise ValueError("Time can not be a bollean value")
        try:
            _ = float(time)
            # print(time, _)
        except:
            raise ValueError(
                "Provide a proper time value in seconds (eg. 100)")

    def validate_key(self, key):
        if type(key) != str:
            raise TypeError("key should be a string")

        if len(key) > 32:
            raise ValueError("Key length should be within 32 character")

        if len(key) == 0:
            raise ValueError("Key can't be empty")

    def validate_and_clean_value(self, value):
        try:
            # clean the json string
            _json = json.dumps(json.loads(value))
        except:
            raise TypeError("Value is not a valid JSON")

        # if the size is within 16KB
        if _json.__sizeof__() > 16*1024:
            raise ValueError("JSON id too large")

        return _json

    def key_exists(self, key):
        r_value = self.execute_sqlite(
            "SELECT key, value FROM DatastoreTable WHERE key=?",
            (key,), fetch=True)

        return bool(r_value)

    def delete_database(self):
        # remove the file and directory
        os.remove(self.file_path)
        try:
            os.removedirs(os.path.dirname(self.file_path))
        except:
            pass
