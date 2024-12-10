import requests
import json

from get_API_key import get_api_keys_list

api_num = 0
Api_keys = get_api_keys_list()


def gpt_response(prompt):
    global api_num, Api_keys
    API_KEY = Api_keys[api_num % len(Api_keys)]
    api_num = api_num + 1
    response = requests.post(
        url="https://api.aimlapi.com/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        data=json.dumps(
            {
                # "model": "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
                "model": "gpt-4o-2024-08-06",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                "max_tokens": 512,
                "stream": False,
            }
        ),
    )

    response.raise_for_status()
    return response.json()["choices"][0]['message']['content']
