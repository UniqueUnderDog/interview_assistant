import os
from volcenginesdkarkruntime import Ark

def get_response(prompt,
                api_key='bbbb2dd9-de42-416b-9fb4-59ad0f45dc94',
                model='doubao-seed-1-6-thinking-250715'):
    client = Ark(
    # 从环境变量中读取您的方舟API Key
    api_key=os.environ.get("ARK_API_KEY",api_key), 
    # 深度思考模型耗费时间会较长，请您设置较大的超时时间，避免超时，推荐30分钟以上
    timeout=1800,
    )
    response = client.chat.completions.create(
    # 替换 <MODEL> 为Model ID
    model=model,
    messages=[
        {"role": "user", "content": prompt}
    ]
)
    return response.choices[0].message.content

print(get_response('你好'))