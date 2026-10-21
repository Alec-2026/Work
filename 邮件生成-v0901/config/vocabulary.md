# 热词表
文档: https://help.aliyun.com/zh/model-studio/custom-hot-words?spm=a2c4g.11186623.0.0.1998601bPKdWOG

1. 创建热词表
curl -X POST https://dashscope.aliyuncs.com/api/v1/services/audio/asr/customization \
-H "Authorization: Bearer sk-206d44d93c8f40cdab71b3c35be97e31" \
-H "Content-Type: application/json" \
-d '{
    "model": "speech-biasing",
    "input": {
            "action": "create_vocabulary",
            "target_model": "paraformer-v2",
            "prefix": "testpfx",
            "vocabulary": [
                {"text": "益好", "weight": 4, "lang": "zh"},
                {"text": "益好旗舰店经理", "weight": 4, "lang": "zh"},
                {"text": "经理", "weight": 4, "lang": "zh"},
                {"text": "益好店铺", "weight": 4, "lang": "zh"},
                {"text": "旗舰店", "weight": 4, "lang": "zh"},
                {"text": "益好旗舰店", "weight": 4, "lang": "zh"},
                {"text": "教培", "weight": 4, "lang": "zh"},
                {"text": "赵乐", "weight": 4, "lang": "zh"},
                {"text": "接待客户", "weight": 4, "lang": "zh"},
                {"text": "起订", "weight": 4, "lang": "zh"},
                {"text": "工厂", "weight": 4, "lang": "zh"},
                {"text": "加厚", "weight": 4, "lang": "zh"},
                {"text": "漏水", "weight": 4, "lang": "zh"},
                
                {"text": "都能做", "weight": 4, "lang": "zh"},
                {"text": "都能印", "weight": 4, "lang": "zh"},
                {"text": "单独开发", "weight": 4, "lang": "zh"},
                {"text": "单独定制", "weight": 4, "lang": "zh"},
                {"text": "能做的", "weight": 4, "lang": "zh"},
                
                {"text": "东讯", "weight": 4, "lang": "zh"},
                {"text": "定制经理", "weight": 4, "lang": "zh"},
                {"text": "周雪", "weight": 4, "lang": "zh"}

            ]
        }
}'

2. 查询所有热词表
curl -X POST https://dashscope.aliyuncs.com/api/v1/services/audio/asr/customization \
-H "Authorization: Bearer sk-206d44d93c8f40cdab71b3c35be97e31" \
-H "Content-Type: application/json" \
-d '{
    "model": "speech-biasing",
    "input": {
                "action": "list_vocabulary",
                "prefix": null,
                "page_index": 0,
                "page_size": 10
            }
}'

3. 查询指定热词表
curl -X POST https://dashscope.aliyuncs.com/api/v1/services/audio/asr/customization \
-H "Authorization: Bearer sk-206d44d93c8f40cdab71b3c35be97e31" \
-H "Content-Type: application/json" \
-d '{
    "model": "speech-biasing",
    "input": {
                "action": "query_vocabulary",
                "vocabulary_id": "vocab-testpfx-9a8c51985bae468894de75f729627f0f"
            }
}'


4. 更新热词表
curl -X POST https://dashscope.aliyuncs.com/api/v1/services/audio/asr/customization \
-H "Authorization: Bearer sk-206d44d93c8f40cdab71b3c35be97e31" \
-H "Content-Type: application/json" \
-d '{
    "model": "speech-biasing",
    "input": {
                "action": "update_vocabulary",
                "vocabulary_id": "vocab-testpfx-9a8c51985bae468894de75f729627f0f",
                "vocabulary": [
{"text": "KT板", "weight": 4, "lang": "zh"},
{"text": "周雪", "weight": 4, "lang": "zh"},
{"text": "中空杯", "weight": 4, "lang": "zh"},
{"text": "纸碗", "weight": 4, "lang": "zh"},
{"text": "纸杯", "weight": 4, "lang": "zh"},
{"text": "赵乐", "weight": 4, "lang": "zh"},
{"text": "展架", "weight": 4, "lang": "zh"},
{"text": "益好定制", "weight": 4, "lang": "zh"},
{"text": "益好", "weight": 4, "lang": "zh"},
{"text": "小批量", "weight": 4, "lang": "zh"},
{"text": "无毛边", "weight": 4, "lang": "zh"},
{"text": "无纺布袋", "weight": 4, "lang": "zh"},
{"text": "瓦楞杯", "weight": 4, "lang": "zh"},
{"text": "锁水", "weight": 4, "lang": "zh"},
{"text": "孙悦", "weight": 4, "lang": "zh"},
{"text": "益好孙悦", "weight": 4, "lang": "zh"},
{"text": "手提袋", "weight": 4, "lang": "zh"},
{"text": "食品级", "weight": 4, "lang": "zh"},
{"text": "时间轴店铺", "weight": 4, "lang": "zh"},
{"text": "时间轴", "weight": 4, "lang": "zh"},
{"text": "色彩鲜艳", "weight": 4, "lang": "zh"},
{"text": "起订", "weight": 4, "lang": "zh"},
{"text": "旗舰店", "weight": 4, "lang": "zh"},
{"text": "旗舰", "weight": 4, "lang": "zh"},
{"text": "牛皮纸袋", "weight": 4, "lang": "zh"},
{"text": "奶茶杯", "weight": 4, "lang": "zh"},
{"text": "名片", "weight": 4, "lang": "zh"},
{"text": "妙语橙", "weight": 4, "lang": "zh"},
{"text": "免费设计", "weight": 4, "lang": "zh"},
{"text": "免费打样", "weight": 4, "lang": "zh"},
{"text": "漏水", "weight": 4, "lang": "zh"},
{"text": "款式多", "weight": 4, "lang": "zh"},
{"text": "客户经理", "weight": 4, "lang": "zh"},
{"text": "卡纸袋", "weight": 4, "lang": "zh"},
{"text": "卡片儿", "weight": 4, "lang": "zh"},
{"text": "咖啡杯", "weight": 4, "lang": "zh"},
{"text": "锦旗", "weight": 4, "lang": "zh"},
{"text": "奖杯", "weight": 4, "lang": "zh"},
{"text": "会员卡", "weight": 4, "lang": "zh"},
{"text": "环保油墨", "weight": 4, "lang": "zh"},
{"text": "环保袋", "weight": 4, "lang": "zh"},
{"text": "画册", "weight": 4, "lang": "zh"},
{"text": "横幅", "weight": 4, "lang": "zh"},
{"text": "海报", "weight": 4, "lang": "zh"},
{"text": "广告扇", "weight": 4, "lang": "zh"},
{"text": "刮刮卡", "weight": 4, "lang": "zh"},
{"text": "工厂", "weight": 4, "lang": "zh"},
{"text": "隔热", "weight": 4, "lang": "zh"},
{"text": "帆布袋", "weight": 4, "lang": "zh"},
{"text": "东讯旗舰店", "weight": 4, "lang": "zh"},
{"text": "东讯旗舰", "weight": 4, "lang": "zh"},
{"text": "东讯", "weight": 4, "lang": "zh"},
{"text": "定制经理", "weight": 4, "lang": "zh"},
{"text": "定制", "weight": 4, "lang": "zh"},
{"text": "东讯的定制经理", "weight": 4, "lang": "zh"},
{"text": "代金券", "weight": 4, "lang": "zh"},
{"text": "传单", "weight": 4, "lang": "zh"},
{"text": "菜单", "weight": 4, "lang": "zh"},
{"text": "彩旗", "weight": 4, "lang": "zh"},
{"text": "不干胶", "weight": 4, "lang": "zh"},
{"text": "保温袋", "weight": 4, "lang": "zh"},
{"text": "包装盒", "weight": 4, "lang": "zh"},
{"text": "包设计", "weight": 4, "lang": "zh"},
{"text": "我益好孙悦", "weight": 4, "lang": "zh"}
                   ]      
               }
}'