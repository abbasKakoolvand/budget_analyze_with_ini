import time

import requests
import json

from get_API_key import get_api_keys_list

api_num = 0
Api_keys = get_api_keys_list()


def gpt_response(prompt):
    global api_num, Api_keys
    API_KEY = Api_keys[api_num % len(Api_keys)]
    api_num = api_num + 1
    try:
        response = requests.post(
            url="https://api.aimlapi.com/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
            },
            data=json.dumps(
                {
                    # "model": "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
                    "model": "gpt-4o",
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
    except BaseException as e:
        print(e)
        time.sleep(60)


if __name__ == '__main__':
    print(gpt_response(f"""You are an expert in business analysis. I have a list of activities which have some budget for our telecom company and a list of our telecom company strategy initiatives.I have a list of activities which have some budget for our telecom company."""))
