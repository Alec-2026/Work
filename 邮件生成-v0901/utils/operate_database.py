import traceback
import logging
import time
from datetime import datetime
from utils.load_config import get_config
from clickhouse_driver import Client
import json
import uuid

logger = logging.getLogger()


class OpDataBase(object):
    def __init__(self):
        conf = get_config()
        self.clickhouse_host = conf['db_clickhouse']['host']
        self.clickhouse_user = conf['db_clickhouse']['user']
        self.clickhouse_password = conf['db_clickhouse']['password']
        self.clickhouse_database = conf['db_clickhouse']['database']
        self.clickhouse_port = conf['db_clickhouse']['port']

        self.insert_table = conf['db_clickhouse']['insert_table']
        self.prompt_table = conf['db_clickhouse']['prompt_table']

    def decorator_insert_model_response(self, func):
        def insert_model_response(
            table_name, remote_addr, request, response, status, request_model, input_token,
            output_token, cost, use_time, is_test, time, date, business, code
        ):
            try:
                client = Client(
                    self.clickhouse_host,
                    user=self.clickhouse_user,
                    password=self.clickhouse_password,
                    database=self.clickhouse_database,
                    port=self.clickhouse_port
                )

                sql_string = f"""
                    INSERT INTO {table_name} 
                    (remote_addr, request, response, status, request_model, input_token, output_token, cost, use_time, is_test, time, date, business, code)
                    VALUES
                """
                data = [
                    (
                        str(remote_addr),
                        json.dumps(request, ensure_ascii=False),
                        json.dumps(response, ensure_ascii=False),
                        status, request_model, input_token, output_token,
                        cost, use_time, is_test, time, date, str(business), code
                    )
                ]

                client.execute(sql_string, data)
                logger.info("数据插入成功")
            except Exception as e:
                logger.error(f'数据插入失败, {traceback.format_exc()}')

            finally:
                if 'client' in locals():  # 确保finally块中client已定义
                    client.disconnect()  # 显式关闭连接

        def wrapper(*args, **kwargs):  # 接受任意位置和关键字参数
            result = func(*args, **kwargs)  # 调用原始函数，并传递参数
            table_name = self.insert_table
            params = args[-1]
            insert_model_response(
                table_name=table_name,
                remote_addr=params.get('remote_addr', '127.0.0.1'),
                request=params,
                response=result,
                status=result.get('info', None),
                request_model=result.get('request_model', None),
                input_token=result.get('input_token', 0),
                output_token=result.get('output_token', 0),
                cost=result.get('cost', 0),
                use_time=result.get('use_time', 0),
                is_test=1,
                time=time.time(),
                date=datetime.now().strftime('%Y%m%d'),
                business=result.get('business', None),
                code=result['code']
            )
            return result

        return wrapper


    def upload_prompt(self, business_name, prompt, version):
        """将prompt上传到ck"""
        try:
            client = Client(
                self.clickhouse_host,
                user=self.clickhouse_user,
                password=self.clickhouse_password,
                database=self.clickhouse_database,
                port=self.clickhouse_port
            )

            sql_string = f"""
                    INSERT INTO {self.prompt_table} 
                    (prompt_id, business_name, prompt, version, time, date)
                    VALUES
                """

            prompt_id = str(uuid.uuid4())
            data = [
                (
                    prompt_id,
                    business_name,
                    prompt,
                    str(version),
                    time.time(),
                    datetime.now().strftime('%Y-%m-%d')
                )
            ]

            client.execute(sql_string, data)
            logger.info("数据插入成功")
        except Exception as e:
            logger.error(f'数据插入失败, {traceback.format_exc()}')

        finally:
            if 'client' in locals():  # 确保finally块中client已定义
                client.disconnect()  # 显式关闭连接

    def get_last_prompt(self, business_name):
        """查询指定业务名称的 prompt"""  # 修正文档字符串，原描述与方法功能不符
        try:
            client = Client(
                self.clickhouse_host,
                user=self.clickhouse_user,
                password=self.clickhouse_password,
                database=self.clickhouse_database,
                port=self.clickhouse_port
            )

            sql_string = f"""
                SELECT prompt FROM {self.prompt_table}
                WHERE business_name = %(business_name)s
                and `time` = (
                    select max(`time`) 
                    from prompt_customer_aware 
                    where business_name = %(business_name)s
                )
            """
            params = {
                'business_name': business_name,
            }

            # 执行查询并获取结果
            result = client.execute(sql_string, params)
            if len(result) == 0:
                return ''
            prompt_content = result[0][0]
            logger.info("数据查询成功")
            return prompt_content
        except Exception as e:
            logger.error(f'数据查询失败, {traceback.format_exc()}')
            return ''
        finally:
            if 'client' in locals():  # 确保finally块中client已定义
                client.disconnect()  # 显式关闭连接


if __name__ == '__main__':
    odb = OpDataBase()
    res = odb.query_prompt('独立站-获取客户名称')
    print(res)