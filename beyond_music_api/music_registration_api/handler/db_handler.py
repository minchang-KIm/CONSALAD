import os
import sys
import time
import pyodbc
import pymongo
sys.path.append(str(os.path.dirname(os.path.abspath(os.path.dirname(__file__)))))
from config.parse import get_config

retry_count = 5

class Database:
    @classmethod
    def __init__(cls):
        pass

    @classmethod
    def __connection(cls, name):
        # ml_dev  : 백업 데이터 select 시 사용
        # ml_live : 라이브 데이터 실서버 사용
        # ml_live_select : 라이브 데이터 select 시 사용
        # test 용 코드 :

        # if name == "ml_live":
        #     name = "ml_live_select"

        conn_dict = get_config()[name]
        host = conn_dict['server']
        user = conn_dict['user']
        password = conn_dict['password']
        database = conn_dict['database']
        charset = conn_dict['charset']
        autocommit = conn_dict['autocommit']
        conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + host + ';DATABASE=' + database + ';UID=' + user + ';PWD=' + password + '',autocommit=True, charset=charset)
        cursor = conn.cursor()
        return cursor

    @classmethod
    def get_mongo_client(cls, name):
        for try_num in range(retry_count+1):
            try:
                # mongo or mongo_local
                mongo_dict = get_config()[name]
                mongo_address = mongo_dict['address']
                mongo_user = mongo_dict['user']
                mongo_passwd = mongo_dict['password']
                myclient = pymongo.MongoClient(f"mongodb://{mongo_user}:{mongo_passwd}@{mongo_address}/?authSource=admin&"
                                               "readPreference=primary&"
                                               "appname=MongoDB%20Compass&ssl=false")
                return myclient
            except Exception as e:
                print(f"Error : DB Connection {e} with try count {try_num}")
                if try_num < retry_count:
                    print(f"time sleep for retry again..{2**try_num}..")
                    time.sleep(2**try_num)
                else:
                    raise Exception(e)

    @classmethod
    def execute_list(cls, query: str, name):
        for try_num in range(retry_count+1):
            try:
                cursor = cls.__connection(name)
                cursor.execute(query)
                columns = [column[0] for column in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
            except Exception as e:
                print(f"Error : DB Connection {e} with try count {try_num}")
                if try_num < retry_count:
                    print(f"time sleep for retry again..{2**try_num}..")
                    time.sleep(2**try_num)
                else:
                    raise Exception(e)

    @classmethod
    def execute_object(cls, query: str, name):
        for try_num in range(retry_count+1):
            try:
                cursor = cls.__connection(name)
                cursor.execute(query)
                columns = [column[0] for column in cursor.description]
                result = cursor.fetchone()
                if result is not None:
                    result = dict(zip(columns, result))
                return result
            except Exception as e:
                print(f"Error : DB Connection {e} with try count {try_num}")
                if try_num < retry_count:
                    print(f"time sleep for retry again..{2**try_num}..")
                    time.sleep(2**try_num)
                else:
                    raise Exception(e)

    @classmethod
    def execute_none_result(cls, query: str, name):
        for try_num in range(retry_count + 1):
            try:
                cursor = cls.__connection(name)
                cursor.execute(query)
                break
            except Exception as e:
                print(f"Error : DB Connection {e} with try count {try_num}")
                if try_num < retry_count:
                    print(f"time sleep for retry again..{2**try_num}..")
                    time.sleep(2**try_num)
                else:
                    raise Exception(e)

if __name__ == '__main__':
    print(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
    print(sys.path)
    sys.path.append(str(os.path.dirname(os.path.abspath(os.path.dirname(__file__)))))
    print(sys.path)