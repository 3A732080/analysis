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
            execution_time = self.fetch_total_execution_time(sql)

            if not results:
                return {
                    'success': True,
                    'data': {'column': result_column, 'value': []},
                    'execution_time': execution_time
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
                'execution_time': execution_time
            }

        except pymssql.DatabaseError as e:
            if exception == False:
                return {
                    'success': False,
                    'data': {'column': [], 'value': []},
                    'execution_time': None
                }

            return {
                'success': False,
                'data': str(e),
                'execution_time': None
            }
        
        except pymssql.OperationalError as e:
            if exception == False:
                return {
                    'success': False,
                    'data': {'column': [], 'value': []},
                    'execution_time': None
                }

            return {
                'success': False,
                'data': str(e),
                'execution_time': None
            }  
        
        except Exception as e:
            if exception == False:
                return {
                    'success': False,
                    'data': {'column': [], 'value': []},
                    'execution_time': None
                }

            
            return {
                'success': False,
                'data': str(e),
                'execution_time': None 
            } 
        
    def fetch_total_execution_time(self, sql_command):
        try:
            query = "EXEC ExecuteDynamicQuery @SQLCommand=%s"
            self.cursor.execute(query, (sql_command,))
            execution_time = None
            
            while True:
                result = self.cursor.fetchone()
                if result is not None:
                    execution_time = result.get('TotalExecutionTime', None)

                if not self.cursor.nextset():
                    break
            
            if execution_time is not None:
                return execution_time
            
            else:
                print("Execution time key not found in result.")
                return None
        except Exception as e:
            print(f"Error: {str(e)}")
            return None

    def close(self):
        self.cursor.close()
        self.connection.close()
        DatabaseConnection._instance = None

