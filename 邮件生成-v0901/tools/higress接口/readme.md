curl --request POST \
  --url http://10.1.21.49:8082/v1/chat/completions \
  --header 'Authorization: Bearer sk-49e1db70ecdd40bd8b628d51b9b13f75' \
  --header 'Content-Type: application/json' \
  --data '{
    "model": "tensorzero::model_name::default-llm-no-think",
    "messages": [
      {
        "role": "user",
        "content": "wakeup"
      }
    ],
    "temperature": 0.6,
    "top_p": 0.8,
    "max_tokens": 2048,
    "chat_template_kwargs": {
        "thinking": false
    }
  }'