# 部署信息(接口上线后可以在这个地方记录，防止后续忘记)
服务器: 10.1.21.56
部署地址: cd /home/diyadmin/独立站-邮件生成
使用环境: conda activate llm
启动命令: 
  - python service_gen_email.py
  - bash restart_flask.py
接口: 
ck存储表: tag_ai_gen_email
上线日期: 2026-09-15

版本管理文档：
https://alidocs.dingtalk.com/i/nodes/QOG9lyrgJP3OElxzTlEM3Y6vVzN67Mw4?utm_scene=person_space&utm_medium=dingdoc_doc_plugin_card&utm_source=dingdoc_doc

# 项目信息
- app_tag.py: 主app文件，将pipline写在这里，在这里将日志信息写入clickhouse
- auto_tag.py: app应用程序文件，进行业务逻辑处理，调用模型
- service_tag.py: 接口服务启动文件
- config, 配置文件
- data, 测试数据
- prompt, 提示词文件夹
- labels, 标签文件
- restart.sh, 启动脚本

- 运行相关
  - 离线批量跑数据
    - auto_tag.py, 单独离线跑一条数据
    - run_batch_llm.py，离线批量跑数据
  - 在线服务
    - tt_request.py: 单次请求
    - tt_request_batch.py: 批量请求
- utils, 工具箱
  - get_llm_conf.py, 获取llm链接方式的配置信息，部署在服务器上
  - load_config.py, 读取本地文件的配置
  - chat_with_llm.py, 封装llm的调用，包含获取prompt模版和message组合，模型的参数

# tips
- 当只修改conf和prompt时可直接修改，无需重新启动服务
- 每次服务启动的时候会校验，并存储prompt
- 每次启动服务时，会遍历prompt目录下的所有prompt，存入clickhouse表prompt_customer_aware
  - 看板位置: http://10.168.20.35:5002/

# sop
- 每次使用时复制为新的工程，并修改工程名称
- 使用sql_files目录下的dml文件建设新表，在config/conf.ini的db_clickhouse/insert_table修改为新表名，日志将会插入到该表中。
  - 小项目可以直接丢入默认的tag_cams_big_table表中，是一个汇总表。
- 在app_tag中修改pipeline, 当需要多次请求模型时，将逻辑写在这个文件中。该文件会将请求和结果插入clickhouse表中
- 在auto_tag中修改**业务逻辑**，运行auto_tag.py测试单条数据
  - 修改流程sop：
    1. fill_prompt, 加载并填充prompt模版
    2. get_message, 将prompt组合为message列表
    3. llm_request, 给模型发送消息，获取结果
       - check_model_response, 校验模型回复结果，返回为False时进行重试，返回为True则校验通过。
    4. fix_response, 优化润色模型的回复结果
  - others: 根据业务情况调整模型的参数，在utils/chat_with_llm.py中修改, 固定业务推荐温度设置为0.1，发散性的设置为0.7-1
- 运行run_batch_llm文件进行批量测试
- 运行service_tag.py启动服务
- 修改restart.sh脚本
- 上线到服务器
- 使用restart.sh脚本启动服务
- 运行tt_request.py进行测试

(对于请求量大的接口，建议使用gunicorn部署)