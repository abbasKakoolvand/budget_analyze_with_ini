import asyncio
import random
import time
from asyncio import WindowsSelectorEventLoopPolicy

from requests.exceptions import Timeout


# Set your OpenAI API key

from g4f.client import Client

client = Client()

asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())


def gpt_request(prompt):
    time.sleep(61)
    available_models = [
        'gpt-4-turbo',
        'gpt-4',
        # 'gpt-3.5-turbo',
        "gemini-pro",
        'gpt-4o-mini',  # One of the older and more capable models
        'gpt-4o',  # A mid-tier model
        'llama-3.1-405b',
        'llama-3.1-70b',
        # # 'claude-3.5-sonnet',
        # 'llama-3.2-90b',
        # # 'claude-3.5-sonnet',
    ]

    # Step 2: Randomly select a model
    selected_model = random.choice(available_models)
    llm_model = selected_model
    print(selected_model)
    try:
        response = client.chat.completions.create(
            model=selected_model,
            # model="gemini-pro",
            # model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,  # Set the desired temperature here
            timeout=10  # This is where you set the timeout
        )
        response = response.choices[0].message.content
    except Timeout:
        print("Request timed out. Ignoring the response.")
        response = "None"

    fined_response = str(response).replace("```", "")
    print("response is :", fined_response)

    return fined_response
