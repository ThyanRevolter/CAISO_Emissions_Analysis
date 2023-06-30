import requests
from requests.auth import HTTPBasicAuth
import json
from datetime import datetime, timedelta
import pandas as pd
import pytz

# account details
username = 'gcezar'
password = 'bits&wattsDemo1'
email = 'gcezar@stanford.edu'
org = 'Stanford University'

# request details
ba = 'SGIP_CAISO_PGE' 

def login(username, password):
    url = 'https://sgipsignal.com/login'
    try:
        rsp = requests.get(url, auth=HTTPBasicAuth(username, password))
    except BaseException as e:
        print('There was an error making your login request: {}'.format(e))
        return None

    try:
        return rsp.json()['token']
    except BaseException:
        print('There was an error logging in. The message returned from the '
              'api is {}'.format(rsp.text))
        return None


def forecast(token, ba, starttime=None, endtime=None, version=None):
    url = 'https://sgipsignal.com/sgipforecast'
    headers = {'Authorization': 'Bearer {}'.format(token)}

    params = {'ba': ba}
    if starttime:
        params.update({'starttime': starttime, 'endtime': endtime})
    if version:
        params['version'] = version

    rsp = requests.get(url, headers=headers, params=params)
    print('Status Code:', rsp.status_code)  # uncomment to see raw response
    return rsp.json()

token = login(username, password)

# print(token)
if not token:
    print('You will need to fix your login credentials (username and password '
          'at the start of this file) before you can query other endpoints. '
          'Make sure that you have registered at least once by uncommenting '
          'the register(username, password, email, org) line near the bottom '
          'of this file.')
    exit()

def get_forecast_data(from_time, num_hours, ba):
    to_time = from_time + timedelta(hours=num_hours, minutes=5)
    start_hour = from_time.hour
    # converting PST to UTC
    from_time = from_time.replace(tzinfo=pytz.timezone('US/Pacific')).astimezone(pytz.utc)
    to_time = to_time.replace(tzinfo=pytz.timezone('US/Pacific')).astimezone(pytz.utc)
    start_time_str = from_time.strftime("%Y-%m-%dT%H:%M:%S-0000")
    end_time_str = to_time.strftime("%Y-%m-%dT%H:%M:%S-0000")
    # Querying the forecast data from API
    forecast_data = forecast(token, ba, start_time_str, end_time_str)
    forecast_data = pd.DataFrame(forecast_data)
    # Removing unnecessary columns
    forecast_data = pd.DataFrame(forecast_data['forecast'].values.tolist()[0]).drop(['version', 'ba'], axis=1)
    forecast_data['Datetime'] = pd.to_datetime(forecast_data['point_time'], format='%Y-%m-%d %H:%M:%S')
    forecast_data = forecast_data.drop(['point_time'], axis=1)
    forecast_data.set_index('Datetime', inplace=True)
    # Selecting the data for the specified time range
    forecast_data = forecast_data[(forecast_data.index >= pd.Timestamp(start_time_str)) & (forecast_data.index <= pd.Timestamp(end_time_str))]
    co2_optimization_dict = {"dt":1/12, "num_hours":round((to_time - from_time).total_seconds()/3600), "start_hour":start_hour, "p_co2":0, "co2_grid":list(zip((list(map(int,forecast_data.index.view('int64')/100000000))), forecast_data['value'].values.tolist()))}
    co2_optimization_json = json.dumps(co2_optimization_dict, indent=4)
    return co2_optimization_json

# Enter start and num of hour for forecast data in the format: datetime(YYYY,M,D,H,M,S) in PST timezone
from_time = datetime(2022,11,1,0,0,0)
num_hours = 24 # maximum 35 hours
co2_optimization_json = get_forecast_data(from_time, num_hours, ba)
#write json to file
with open('co2_optimization.json', 'w') as f:
    json.dump(json.loads(co2_optimization_json), f)
