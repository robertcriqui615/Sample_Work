import os
import pyodbc

from dotenv import load_dotenv
from typing import Union, Iterable

load_dotenv()
conString = os.environ["conString"]


class DBCon:

    def __init__(self, conString: str):
        """:param connectionString: pointer to the database"""

        self.conString = conString

    def returnDict(self, cmd: str, keyColumn: int, valueColumn: Union[int, Iterable]=None, parameters: tuple = None) -> dict:
        """
        :param cmd: stored procedure to execute
        :param keyColumn: column number we want to use for the key
        :param valueColumn: column number we want to use for the value
        :param parameters: parameters to be passed in to the stored procedure
        :return: dictionary of query result
        """

        if valueColumn is None:
            return {row[keyColumn]: list(row) for row in self.returnData(cmd, parameters)}

        if isinstance(valueColumn, (list, tuple)):
            return {row[keyColumn]: [row[col] for col in valueColumn] for row in self.returnData(cmd, parameters)}

        return {row[keyColumn]: row[valueColumn] for row in self.returnData(cmd, parameters)}

    def returnDictClass(self, cmd: str, keyColumn: int, cls: type, parameters: tuple = None) -> dict:
        """
        :param cmd: stored procedure to execute
        :param keyColumn: column number we want to use for the key
        :param cls: type of class we want to create
        :param parameters: parameters to be passed in to the stored procedure
        :return: dictionary of query result
        """

        return {row[keyColumn]: cls(*row) for row in self.returnData(cmd, parameters)}


    def returnList(self, cmd: str, parameters: tuple = None, columns: tuple = None) -> list:
        """
        :param cmd: stored procedure to execute
        :param parameters: parameters to be passed in to the stored procedure
        :param columns: column numbers we want to use for the value
        :return: list of query result
        """

        if columns is None:
            return [list(row) for row in self.returnData(cmd, parameters)]

        if len(columns) == 1:
            return [row[columns[0]] for row in self.returnData(cmd, parameters)]

        return [[row[column] for column in columns] for row in self.returnData(cmd, parameters)]

    def returnOne(self, cmd: str, parameters: tuple = None):
        """
        :param cmd: stored procedure to execute
        :param parameters: parameters to be passed in to the stored procedure
        :return: a single value from a query
        """
        return next(self.returnData(cmd, parameters))[0]

    def insertData(self, cmd: str, parameters: tuple = None):
        """
        :param cmd: stored proceudre we want to execute
        :param parameters: parameters for said stored procedure
        :return: loops through all rows untl all sets are exhausted
        """

        with pyodbc.connect(self.conString) as con:

            try:
                crsr = self._getFinalCursor(con, cmd, parameters)
                crsr.commit()
            except pyodbc.Error as e:
                crsr.rollback()
                print('e')

    def returnData(self, cmd: str, parameters: tuple = None) -> tuple:
        """
        :param cmd: stored proceudre we want to execute
        :param parameters: parameters for said stored procedure
        :return: loops through all rows untl all sets are exhausted
        """

        with pyodbc.connect(self.conString) as con:

            crsr = self._getFinalCursor(con, cmd, parameters)

            for row in crsr:
                yield row

    @classmethod
    def _getFinalCursor(cls, con: pyodbc.Connection, cmd: str, parameters: tuple) -> pyodbc.Cursor:
        """
        Gets out cursor to be looped over. If the query errors out, we'll return a mock cursor that
        returns an empty list as an iterator, and always returns False for nextset.

        :param con: Connection String
        :param cmd: stored procedure we want to execute
        :param parameters: parameters for said stored procedure
        :return: result set cursor
        """
        query = cls.buildSPQuery(cmd, cls.getParameterCount(parameters))

        try:
            if "?" not in query:
                crsr = con.execute(query)
            else:
                crsr = con.execute(query, parameters)
        except pyodbc.Error as e:
            print(e)
            return MockCursor()

        return crsr

    @staticmethod
    def buildSPQuery(cmd: str, paramCount: int) -> str:
        """
        :param cmd: Stored Procedure to execute
        :param paramCount: number of parameters
        :return: final query string to be used by the pyodbc driver
        """

        if paramCount == 0:
            return f'{{CALL {cmd}}}'

        questionMarks = ('?,' * paramCount)[:-1]
        return f'{{CALL {cmd} ({questionMarks})}}'

    @staticmethod
    def getParameterCount(parameters: tuple) -> int:
        """
        :param parameters: parameters for a stored procedure
        :return: number of parameters
        """

        if parameters is None:
            return 0

        return len(parameters)


class MockCursor:
    """Used to return mock an empty cursor if our query errors out"""

    def __iter__(self):
        return iter([])

    def nextset(self):
        return False


con = DBCon(conString)  # Will be used throughout the project to query data