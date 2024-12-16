import json
import pandas as pd
import os

from gpt_request import gpt_request

try:
    df = pd.read_excel("activity_initiatives.xlsx")
    # start_index = max(df["Index"].unique()) + 1
    start_index = 0
except:
    # Define the columns for the DataFrame
    columns = ['Activity', 'Initiative1', 'Relevance1', "Count1", 'Initiative2', 'Relevance2', "Count2", 'Initiative3',
               'Relevance3', "Count3",
               'Initiative4', 'Relevance4', "Count4", 'Initiative5', 'Relevance5', "Count5"]
    df = pd.DataFrame(columns=columns)
    start_index = 0

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

end_index = 1500  # Process until the end of df_activity

# Process the specified rows in df_activity
for index in range(start_index, end_index):
    if index in df["Index"].unique():
        continue
    df_row = df_activity.iloc[index]
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

    print(f"Processing index: {index}, prompt length: {len(prompt)}")
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
                    'Original Index': index  # Add the original index to the new row
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
    sorted_results = dict(sorted(results.items(), key=lambda item: item[1]['total_relevance'], reverse=True))
    # After all runs, prepare the final DataFrame
    final_data = []
    new_row = {'Index': index, 'Activity': act_name}
    i = 0
    for initiative, info in sorted_results.items():
        try:
            new_row[f'Initiative{i + 1}'] = initiative
            new_row[f'Relevance{i + 1}'] = info['total_relevance']
            new_row[f'Count{i + 1}'] = str(info['count'])
        except:
            new_row[f'Initiative{i + 1}'] = ""
            new_row[f'Relevance{i + 1}'] = ""
            new_row[f'Count{i + 1}'] = ""
        i = i + 1
        if i == 5:
            break

    final_data.append(new_row)

    # Create a DataFrame from the final data
    final_df = pd.DataFrame(final_data)

    # Sort by Total Relevance and keep only the top 5 initiatives
    # final_df = final_df.sort_values(by='total_relevance', ascending=False).head(5)

    # Append the final results to the existing DataFrame
    df = pd.concat([df, final_df], ignore_index=True)

    # Save the updated DataFrame to an Excel file
    df.to_excel("activity_initiatives.xlsx", index=False)

# Clean up: remove the last processed index file if all rows have been processed
# if index == end_index - 1:
#     os.remove(last_index_file)
