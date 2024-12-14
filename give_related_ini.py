import json

import pandas as pd

from gpt_request import gpt_request
from llm import gpt_response

columns = ['Activity', 'Initiative1', 'Relevance1', 'Initiative2', 'Relevance2', 'Initiative3', 'Relevance3',
           'Initiative4', 'Relevance4', 'Initiative5', 'Relevance5']
df = pd.DataFrame(columns=columns)
df_ini = pd.read_excel("Export for Mr. Rezazadeh 14030913_with ini.xlsx", sheet_name='initiatives')
df_activity = pd.read_excel("Export for Mr. Rezazadeh 14030913_with ini.xlsx", sheet_name='Data')
cxos = df_ini["معاونت"].unique()
initiatives = df_ini["InitiativeTitle"]
initiatives_text = ""

for cxo in cxos:
    initiatives_text += f"\nHere are the {cxo} initiatives:\n"
    for initiative in df_ini[df_ini["معاونت"] == cxo]["InitiativeTitle"].unique():
        initiatives_text += f"{initiative}\n"

for index, df_row in df_activity.iterrows():
    if index == 20:
        break

    act_name = df_row["فعالیت"]  # This is correct
    act_title = df_row["موضوع برنامه"]
    act_cxo = df_row["معاونت"]
    end_text = "you respons must start with { and ends with }"
    prompt = f"""You are an expert in business analysis. I have a list of activities which have some budget for our telecom company and a list of our telecom company strategy initiatives. For each activity, please provide a list of up to 5 and minimum 3 initiatives that have the highest relevance, along with the percentage of relevance for each solution. 
    these are our company initiatives:***{initiatives_text}***
    no i want analyze *activity {act_name} with title{act_title} and for {act_cxo} part*
    Please analyze the relevance of each initiative to {act_name} activity and return the results in JSON format, structured as follows:
    {{
        "Activity A": [
            {{"initiative": "initiative 2", "relevance": 90}},
            {{"initiative": "initiative 4", "relevance": 80}},
            {{"initiative": "initiative 1", "relevance": 70}},
            {{"initiative": "initiative 5", "relevance": 50}},
            ...# more initiatives if exists
        ]
    }}
    
    *{end_text}*
    """
    print(len(prompt))
    length = len(prompt)
    get_data_flag = False

    while not get_data_flag:
        try:
            res1 = gpt_request(prompt)
            print(res1)

            json_end_index = res1.rfind('}')
            res2 = res1[:json_end_index + 1].strip()
            # Isolate the JSON part
            json_start = res2.find('{')  # Find the index of the first '{'
            json_string = res2[json_start:]  # Extract the substring from '{' to the end

            data = json.loads(json_string)

            # data = json.loads(res)
            new_row = {
                'Activity': act_name,  # Example activity

            }
            key = list(data.keys())[0]
            list_Activity = data[key]
            for i in range(5):
                try:
                    new_row[f'Initiative{i + 1}'] = list_Activity[i]["initiative"]
                    new_row[f'Relevance{i + 1}'] = list_Activity[i]["relevance"]
                except:
                    new_row[f'Initiative{i + 1}'] = ""
                    new_row[f'Relevance{i + 1}'] = ""

            # Create a DataFrame for the new row
            new_row_df = pd.DataFrame([new_row])

            # Use pd.concat to append the new row to the existing DataFrame
            df = pd.concat([df, new_row_df], ignore_index=True)
            get_data_flag = True
        except BaseException as e:
            print("\n###################\n", e, "\n###################\n")
df.to_excel("activity_initiatives.xlsx", index=False)
