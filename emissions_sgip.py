# -*- coding: utf-8 -*-
"""
Only tested in Python 3.
You may need to install the 'requests' Python3 module.

Be sure to fill in your username, password, org name and email before running
"""

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
ba = 'SGIP_CAISO_PGE'  # identify grid region
# starttime and endtime are optional, if ommited will return the latest value
# starttime = '2019-01-01T00:00:00-0000'  # UTC offset of 0 (PDT is -7, PST -8)
# starttime_forecast = '2020-04-01T16:45:30-0800'  # UTC offset of 0 (PDT is -7, PST -8)
# endtime = '2019-01-02T00:00:00-0000'
# endtime_forecast = '2020-04-01T16:45:30-0800'

# long term forecast horizon
horizon = 'month'  # 'month' or 'year'


def register(username, password, email, org):
    url = 'https://sgipsignal.com/register'
    params = {'username': username,
              'password': password,
              'email': email,
              'org': org}
    rsp = requests.post(url, json=params)
    print(rsp.text)


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


def moer(token, ba, starttime=None, endtime=None, version=None):
    url = 'https://sgipsignal.com/sgipmoer'
    headers = {'Authorization': 'Bearer {}'.format(token)}
    params = {'ba': ba}
    if starttime:
        params.update({'starttime': starttime, 'endtime': endtime})
    if version:
        params['version'] = version

    rsp = requests.get(url, headers=headers, params=params)
    # print(rsp.text)  # uncomment to see raw response
    return rsp.json()


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


def longforecast(token, ba, horizon, starttime=None, endtime=None):
    url = 'https://sgipsignal.com/sgiplongforecast'
    headers = {'Authorization': 'Bearer {}'.format(token)}

    params = {'ba': ba,
              'horizon': horizon}
    if starttime:
        params.update({'starttime': starttime, 'endtime': endtime})

    rsp = requests.get(url, headers=headers, params=params)
    # print(rsp.text)  # uncomment to see raw response
    return (rsp.json())


# Only register once!!
# register(username, password, email, org)

token = login(username, password)
# print(token)
if not token:
    print('You will need to fix your login credentials (username and password '
          'at the start of this file) before you can query other endpoints. '
          'Make sure that you have registered at least once by uncommenting '
          'the register(username, password, email, org) line near the bottom '
          'of this file.')
    exit()

def get_moer_date(from_time, to_time):
    specific_moer_version = moer(token, 'SGIP_CAISO_PGE', from_time, to_time)
    real_time_moer_df = pd.DataFrame(specific_moer_version)
    print(real_time_moer_df)
    return real_time_moer_df

def get_forecast_date(from_time, to_time):
    forecast_moer = forecast(token, 'SGIP_CAISO_PGE', from_time, to_time)
    forecast_moer_df = pd.DataFrame(forecast_moer)
    print(pd.DataFrame(forecast_moer_df['forecast'].values.tolist()[0]))
    return pd.DataFrame(forecast_moer_df['forecast'].values.tolist()[0])

from_time, to_time = '2022-11-04T00:00:00-0000', '2022-11-05T00:00:00-0000'
moer_info = get_moer_date(from_time,to_time)
forecast_info = get_forecast_date(from_time,to_time)
combined_data = moer_info.set_index('point_time').join(forecast_info.set_index('point_time'), lsuffix='_moer', rsuffix='_forecast')
start_time = datetime(2022,11,5,0,0,0)
end_time =  datetime(2022,12,1,0,0,0)
delta = timedelta(days=1)
start_time_str = start_time.strftime("%Y-%m-%d")+"T00:00:00-0000"
end_time_str = end_time.strftime("%Y-%m-%d")+"T00:00:00-0000"
print("start_time_str ", start_time_str)
print("end_time_str ", end_time_str)
while start_time <= end_time:
    from_time = start_time.strftime("%Y-%m-%d")+"T00:00:00-0000"
    to_time = (start_time + delta).strftime("%Y-%m-%d")+"T00:00:00-0000"
    print("from_time", from_time)
    print("to_time", to_time)
    moer_info = get_moer_date(from_time,to_time)
    forecast_info = get_forecast_date(from_time,to_time)
    combined_data = combined_data.append(moer_info.set_index('point_time').join(forecast_info.set_index('point_time'), lsuffix='_moer', rsuffix='_forecast'))
    combined_data.to_excel("combined_data_5.xlsx")
    start_time += delta

# moer_info = get_moer_date(from_time,to_time)
# forecast_info = get_forecast_date(from_time,to_time)
# combined_data = moer_info.set_index('point_time').join(forecast_info.set_index('point_time'), lsuffix='_moer', rsuffix='_forecast')
# moer_info.to_excel("moer_info.xlsx")
# forecast_info.to_excel("forecast_info.xlsx")
combined_data.to_excel("combined_data_5.xlsx")
