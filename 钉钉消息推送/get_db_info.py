import traceback
from clickhouse_driver import Client

from utils import get_config, read_sql



class DataBaseLog():
    def __init__(self):
        config = get_config()
        self.host = config['clickhouse']['host']
        self.user = config['clickhouse']['user']
        self.password = config['clickhouse']['password']
        self.database = config['clickhouse']['database']
        self.port = config['clickhouse']['port']
        self.gen_email_table = config['clickhouse']['gen_email_table']
        self.hubspot_sql_file = 'hubspot数据查询.sql'


    def get_hubspot_info(self):
        """执行 hubspot_sql_file 中的查询，返回 [{列名: 值}, ...]。"""
        client = None
        try:
            sql_string = read_sql(self.hubspot_sql_file)

            client = Client(
                self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port,
            )

            rows, columns = client.execute(sql_string, with_column_types=True)
            column_names = [column[0] for column in columns]
            return [dict(zip(column_names, row)) for row in rows]
        except Exception as e:
            traceback.print_exc()
            return []
        finally:
            if client is not None:
                client.disconnect()

    def get_gen_email_info(self):
        pass


if __name__ == '__main__':
    dbl = DataBaseLog()
    res = dbl.get_hubspot_info()
    print(res)
