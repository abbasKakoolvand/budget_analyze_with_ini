import json
import pandas as pd

from gpt_request import gpt_request
from llm import gpt_response

# Define the columns for the DataFrame
columns = ['Activity', 'Initiative1', 'Relevance1', 'Initiative2', 'Relevance2', 'Initiative3', 'Relevance3',
           'Initiative4', 'Relevance4', 'Initiative5', 'Relevance5']
df = pd.DataFrame(columns=columns)

# Read the Excel file
df_ini = pd.read_excel("Export for Mr. Rezazadeh 14030913_with ini.xlsx", sheet_name='initiatives')
df_activity = pd.read_excel("Export for Mr. Rezazadeh 14030913_with ini.xlsx", sheet_name='Data')

# Create a string of initiatives
cxos = df_ini["معاونت"].unique()
initiatives_text = ""

for cxo in cxos:
    initiatives_text += f"\nHere are the {cxo} initiatives:\n"
    for initiative in df_ini[df_ini["معاونت"] == cxo]["InitiativeTitle"].unique():
        initiatives_text += f"{initiative}\n"

# Specify the start and end indices for the rows you want to process
start_index = 0  # Change this to your desired start index
end_index = 99  # Change this to your desired end index (exclusive)

# Process the specified rows in df_activity
for index, df_row in df_activity.iloc[start_index:end_index].iterrows():
    act_name = df_row["فعالیت"]  # This is correct
    act_title = df_row["موضوع برنامه"]
    act_cxo = df_row["معاونت"]
    end_text = "you respons must start with { and ends with }"

    prompt = f"""You are an expert in business analysis. I have a list of activities which have some budget for our telecom company and a list of our telecom company strategy initiatives. For each activity, please provide a list of up to 5 and minimum 3 initiatives that have the highest relevance, along with the percentage of relevance for each solution. 
    these are our company initiatives:***{initiatives_text}***
    no i want analyze *activity {act_name} with title {act_title} and for {act_cxo} part*
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

    # Initialize variables
    results = {}
    number_of_runs = 5

    # Run the code block 5 times
    for _ in range(number_of_runs):
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

                new_row = {
                    'Activity': act_name,  # Example activity
                }
                key = list(data.keys())[0]
                list_Activity = data[key]

                for item in list_Activity:
                    initiative = item["initiative"]
                    relevance = item["relevance"]

                    # If the initiative is already in results, update its total relevance and count
                    if initiative in results:
                        results[initiative]['total_relevance'] += relevance
                        results[initiative]['count'] += 1
                    else:
                        results[initiative] = {'total_relevance': relevance, 'count': 1}

                get_data_flag = True
            except BaseException as e:
                print("\n###################\n", e, "\n###################\n")

    # After all runs, prepare the final DataFrame
    final_data = []
    for initiative, info in results.items():
        final_data.append({
            'Activity': act_name,
            'Initiative': initiative,
            'Total Relevance': info['total_relevance'],
            'Count': info['count']
        })

    # Create a DataFrame from the final data
    final_df = pd.DataFrame(final_data)

    # Sort by Total Relevance and keep only the top 5 initiatives
    final_df = final_df.sort_values(by='Total Relevance', ascending=False).head(5)

    # Append the final results to the existing DataFrame
    df = pd.concat([df, final_df], ignore_index=True)

# Save the updated DataFrame to an Excel file
df.to_excel("activity_initiatives.xlsx", index=False)