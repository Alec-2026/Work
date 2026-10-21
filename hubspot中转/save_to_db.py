from utils.op_database import OpDataBase
import json
import time
from datetime import datetime
"""
只负责给数据库中发送结果
"""

def save_to_db(attr):
    """
    Args:
        params:
        status: start_end

    Returns:
    """
    try:
        OpDataBase().insert_model_response_v2(
            request='',
            response='',
            status='success',
            request_model='',
            input_token=0,
            output_token=0,
            cost=-1,
            use_time=0,
            is_test=1,
            time=int(time.time()),
            date=str(datetime.now().strftime('%Y%m%d')),
            remote_addr= '127.0.0.1',
            business='hubspot中转',
            code=1,
            attr = json.dumps(attr, ensure_ascii=False, default=str)
        )
    except Exception as e:
        OpDataBase().insert_model_response_v2(
            request='',
            response='',
            status='failed',
            request_model='',
            input_token=0,
            output_token=0,
            cost=-1,
            use_time=0,
            is_test=1,
            time=int(time.time()),
            date=str(datetime.now().strftime('%Y%m%d')),
            remote_addr='127.0.0.1',
            business='hubspot中转',
            code=0,
            attr=json.dumps(attr, ensure_ascii=False, default=str)
        )