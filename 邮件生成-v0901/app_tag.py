from utils.operate_database import OpDataBase
import logging
import traceback
from apps.view_product_gen_email.pipline_gen_email import pipline_route as view_product_pipline
from apps.started_design_gen_email.pipline_gen_email import pipline_route as started_design_pipline
from apps.uploaded_artwork_gen_email.pipline_gen_email import pipline_route as uploaded_artwork_pipline
from apps.viewed_promotion_gen_email.pipline_gen_email import pipline_route as viewed_promotion_pipline
logger = logging.getLogger()



def get_email_type_function(params):
    """
    选择哪个事件
    Returns:
    """
    email_type_map = {
        'viewed_product_abandonment': view_product_pipline,
        'started_design_abandonment': started_design_pipline,
        'upload_artwork_abandonment': uploaded_artwork_pipline,
        'viewed_promotion_abandonment': viewed_promotion_pipline
    }

    email_type = params['properties']['last_behavioral_email_type']
    if email_type is None:
        return view_product_pipline
    elif email_type in email_type_map.keys():
        return email_type_map[email_type]
    else:
        raise Exception(f'不支持该邮件类型or埋点事件，支持的邮件类型有: {email_type_map.keys()}')


def check_params(params):
    if 'properties' not in params.keys():
        raise Exception('缺失属性: properties')

    keys_level2 = [
        'last_behavioral_email_type',
        'firstname',
        'last_viewed_product_name',
        'industry_level_2',
        'dedicated_account_manager_label_for_ai_email',
        'first_order_offer_message'
    ]
    for key in keys_level2:
        if key not in params['properties'].keys():
            raise Exception(f'缺失属性: {key}')




@OpDataBase().decorator_insert_model_response
def tag_app(params):
    model_response = {}

    try:
        check_params(params)
        gen_email_function = get_email_type_function(params)
        model_response = gen_email_function(params)
        logger.info(f'model_response:{model_response}')
        return model_response
    except Exception as e:
        logger.error(traceback.format_exc())
        result = {
            'code': 0, 'model_response': None, 'info': f'failed: {str(e)}',
            'business': model_response.get('business', ''),
            'request_model': model_response.get('request_model', ''),
        }
        return result


if __name__ == '__main__':
    import json
    from 测试json import aa
    res = tag_app(aa)
    print(res)
