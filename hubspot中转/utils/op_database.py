import traceback
from clickhouse_driver import Client
import mysql.connector
import pandas as pd
from mysql.connector import Error
import logging
from utils.load_config import get_config

logger = logging.getLogger()


class OpDataBase(object):
    def __init__(self):
        config = get_config()
        self.host = config['db_clickhouse']['host']
        self.user = config['db_clickhouse']['user']
        self.password = config['db_clickhouse']['password']
        self.database = config['db_clickhouse']['database']
        self.port = config['db_clickhouse']['port']
        self.table_name = config['db_clickhouse']['insert_table']


    """
    将数据插入clickhouse v2
    """
    def insert_model_response_v2(self,
        request, response, status, request_model, input_token, output_token, cost, use_time, is_test,
        time, date, remote_addr, business, code, attr
    ):
        try:
            client = Client(
                self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port,
            )

            sql_string = f"""
                INSERT INTO {self.table_name} (
                    request, response, status, request_model, input_token, output_token, cost, 
                    use_time, is_test, time, date, remote_addr, business, code, attr
                )
                VALUES
            """
            data = [(request, response, status, request_model, input_token, output_token, cost,
                    use_time, is_test, time, date, str(remote_addr), business, code, attr)]

            client.execute(sql_string, data)

            logger.info("数据插入成功")

        except Exception as e:
            logger.error(f'数据插入失败, {traceback.format_exc()}')


if __name__ == '__main__':
    pass