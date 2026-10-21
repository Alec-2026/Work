# HubSpot 邮件生成与回写

本项目从 HubSpot 查询需要生成邮件的联系人，调用内部邮件生成服务产生标题和正文，再将结果批量回写到 HubSpot。项目同时支持单次执行和每 5 分钟定时执行。

## 处理流程

1. 在 HubSpot 服务端查询同时满足以下条件的联系人：
   - `email_send = Yes`
   - `email_subject NOT_HAS_PROPERTY`
   - `email_body NOT_HAS_PROPERTY`
2. 本地再次检查邮件标题和正文确实为空。
3. `app.py` 每轮最多取前 100 个联系人，并发调用邮件生成服务。
4. 校验生成数量及联系人 ID，然后将 `email_subject` 和 `email_body` 批量回写 HubSpot。

## 环境要求

- Python 3.10+
- `requests`
- 能访问 HubSpot API
- 能访问内部邮件生成服务 `http://10.1.21.45:5022/gen_email`

安装依赖：

```bash
python -m pip install requests
```

## HubSpot 配置

程序按以下优先级读取访问令牌：

1. 函数的 `access_token` 参数
2. 环境变量 `HUBSPOT_ACCESS_TOKEN`
3. 项目目录中的 `conf.ini`

`conf.ini` 示例：

```ini
[hubspot]
access_token = your-private-app-token
```

HubSpot 私有应用需要具备联系人读取和写入权限。请勿将真实 Token 提交到代码仓库。

## 运行方式

### 单次执行

```bash
python app.py
```

也可以在代码中调用：

```python
from app import run_email_generation

result = run_email_generation(max_workers=50)
print(result)
```

返回结果示例：

```python
{
    "success": True,
    "contact_count": 100,
    "generated_count": 100,
    "updated_count": 100,
    "upload_responses": [...],
}
```

### 定时执行

```bash
python task_scheduler.py
```

默认行为：

- 启动后等待 5 分钟再首次执行。
- 之后每 5 分钟按固定时间点提交一轮任务。
- 同一时间只执行 1 轮，上一轮未完成时，后续任务进入队列等待。
- 单轮失败会记录异常，不会终止后续调度。
- 按 `Ctrl+C` 停止提交新任务并退出。

自定义调度参数：

```python
from task_scheduler import run_scheduler

run_scheduler(interval_seconds=300, worker_count=1)
```

> 注意：任务不会并发执行，但如果单轮耗时长于调度周期，后续任务会在队列中累积。

## 模块使用

### 查询待处理联系人

```python
from need_email_contact import get_contacts_needing_email

contacts = get_contacts_needing_email()
print(f"待处理数量：{len(contacts)}")
```

### 查询某个联系人的 CRM 档案

```python
from hubspot_contact import get_contact_crm_profile

profile = get_contact_crm_profile("customer@example.com")
print(profile)

# 按联系人记录 ID 查询，支持整数或数字字符串
profile = get_contact_crm_profile(record_id="123456789")
# 第一个位置参数也支持记录 ID
profile = get_contact_crm_profile(123456789)
```

`get_contact_crm_profile()` 的 `email` 和 `record_id` 必须且只能提供一个。
邮箱查询返回 `query_email`，记录 ID 查询返回 `query_record_id`。
原 `get_contact_crm_profile_by_id()` 调用统一改为 `get_contact_crm_profile(record_id=...)`。

### 查询联系人事件

```python
from hubspot_events import get_contact_events

result = get_contact_events(
    email="customer@example.com",
    recent_days=1,
    max_events=10,
)
print(result["events"])

# 按 HubSpot 联系人记录 ID 查询（支持整数或数字字符串）
result = get_contact_events(record_id="123456789", recent_days=1, max_events=10)
# 也支持直接传入 ID 作为第一个位置参数
result = get_contact_events(123456789, recent_days=1)
```

`email` 和 `record_id` 必须且只能提供一个，`recent_days` 为必填正整数。
邮箱查询返回 `query_email`，ID 查询返回 `query_record_id`；其余返回字段保持不变。

### 回写邮件内容

```python
from upload_data import upload_contact_emails

responses = upload_contact_emails(
    [
        {
            "id": "123456789",
            "email_subject": "Your email subject",
            "email_body": "Your email body",
        }
    ]
)
print(responses)
```

`upload_contact_emails()` 会直接覆盖已有值，也允许使用空字符串清空字段。批量请求会自动按每批 100 条拆分。

## 日志

日志同时输出到终端和：

```text
logs/app.log
```

日志文件每天轮转，保留最近 7 天。日志记录处理数量、执行阶段、耗时和异常，不记录邮件正文。

## 测试

运行全部单元测试：

```bash
python -m unittest -v test_app.py test_upload_data.py test_task_scheduler.py
```

单元测试使用模拟响应，不会调用真实邮件生成服务，也不会写入 HubSpot。

## 项目结构

```text
app.py                   单轮业务流程
task_scheduler.py        五分钟定时调度
need_email_contact.py    查询待生成邮件的联系人
gen_email.py             调用内部邮件生成服务
upload_data.py           批量回写 HubSpot
hubspot_contact.py       HubSpot CRM 客户端及联系人档案查询
hubspot_events.py        HubSpot 联系人事件查询
utils/logging_config.py  日志配置
```
