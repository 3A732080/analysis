import pymssql

class DatabaseConnection:
    _instance = None

    def __new__(cls, server, user, password, database):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance.connection = pymssql.connect(server, user, password, database)
        return cls._instance

    def __init__(self, server, user, password, database):
        self.cursor = self.connection.cursor(as_dict=True)

    def query(self, sql, exception = True):
        try:
            self.cursor.execute(sql)
            results = self.cursor.fetchall()
            result_column = [desc[0] for desc in self.cursor.description]

            if not results:
                return {
                    'success': True,
                    'data': {'column': result_column, 'value': []},
                }

            processed_results = []

            for row in results:
                processed_row = {'column': [], 'value': []}
                for column, value in row.items():
                    processed_row['column'].append(column)
                    processed_row['value'].append(value)
                processed_results.append(processed_row['value'])
            
            return {
                'success': True,
                'data': {'column': result_column, 'value': processed_results},
            }

        except pymssql.DatabaseError as e:
            if exception == False:
                return {
                    'success': False,
                    'data': {'column': [], 'value': []},
                }

            return {
                'success': False,
                'data': str(e),
            }  
        
        except pymssql.OperationalError as e:
            if exception == False:
                return {
                    'success': False,
                    'data': {'column': [], 'value': []},
                }

            return {
                'success': False,
                'data': str(e),
            }  
        
        except Exception as e:
            if exception == False:
                return {
                    'success': False,
                    'data': {'column': [], 'value': []},
                }

            
            return {
                'success': False,
                'data': str(e),
            }  

    def close(self):
        self.cursor.close()
        self.connection.close()
        DatabaseConnection._instance = None

