from redashAPI.client import RedashAPIClient
from pymongo import MongoClient
import requests
import subprocess
import json

# First line -> refresh token
# Second line -> access token
tk_file = open('token.txt', 'r')

ref_token = tk_file.readline()
tk_file.close()
cmd = 'curl -i https://api.wootric.com/oauth/token ' \
      '-F grant_type=refresh_token -F refresh_token="' + ref_token + '"'
response, str_json = \
    subprocess.run(cmd, shell=True, universal_newlines=True, check=True,
                   capture_output=True).stdout.split('{')
json_data = json.loads("{" + str_json)
print(json_data)
ref_token = json_data['refresh_token']
acc_token = json_data['access_token']
tk_file = open('token.txt', 'w')
tk_file.write(ref_token + "\n" + acc_token)
tk_file.close()

# Request Json
r = requests.get("https://api.wootric.com/v1/nps_summary?access_token=" +
                 acc_token)
data = json.loads(r.text)
print(data)

# Connect to MongoDB
"""
    :args:
    HOST
    PORT
"""
client = MongoClient('localhost', 27017)
db = client.nps
collection = db.data
if collection.find():
    data_id = collection.replaceOne({}, data)
else:
    data_id = collection.insert_one(data).inserted_id

print(data_id)

# Create Client instance
"""
    :args:
    API_KEY
    REDASH_HOST (optional): 'http://localhost:5000' by default
"""
Redash = RedashAPIClient(api_key='IkvyuBL46xjj0JiVGgpwqnVuxgBDaFPqkzKtRsaa')
Redash.create_query("nps", 2, "db.data.find({})")

res = Redash.generate_query_result(2, db.data.find({}), 2)
print(res)



# Create Visualization
"""
    :args:
    NAME
    QUERY_ID
    CHART_TYPE: ["line", "column", "area", "pie", "scatter", "bubble", "box"]
    X_AXIS_COLUMN
    Y_AXIS_COLUMN
    Y_LABEL (optional): Custom name for legend
"""
Redash.create_visualization("respostas", 1, "column",
                            [
                                1, 2, 3
                            ], [
                                res['detractors'],
                                res['passives'],
                                res['promoters']
                            ], [
                                'detractors',
                                'passives',
                                'promoters'
                            ])


# Create Dashboard
"""
    :args:
    NAME
"""
Redash.create_dashboard("NPS Dashboard")


# Add Visualization into Dashboard
"""
    :args:
    DASHBOARD_ID
    VISUALIZATION_ID
    FULL_WIDTH (optional): Full width or not on dashboard, False by default
"""
Redash.add_to_dashboard(1, 1)


# Publish Dashboard and get its public URL
"""
    :args:
    DASHBOARD_ID
"""
url = Redash.get_dashboard_public_url(1)

print(url)