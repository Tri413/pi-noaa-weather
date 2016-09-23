#! /usr/bin/env python

import xml.etree.ElementTree
import urllib.request
import sys, getopt
from datetime import datetime
from datetime import timedelta

#Settings
wind_threshold = 6 #notification windspeed
forecast_days = 5

#Setup
iftttKey =  "SET TO YOUR KEY"
now = datetime.now()
begin = now + timedelta(days=1)
end = now + timedelta(days=forecast_days)
params = "wspd=wspd"

def dateAsStandardDate(dt: datetime):
    mm = str(dt.month)
    dd = str(dt.day)
    yyyy = str(dt.year)
    hour = str(dt.hour)
    mi = str(dt.minute)
    ss = str(dt.second)
    return yyyy + "-" + mm + "-" + dd + "T00:00:00"

def fetchNOAAForecast(lat: float, lon: float, begin: datetime, end: datetime, noaaParams: str):
    noaaUrl = "http://graphical.weather.gov/xml/sample_products/browser_interface/ndfdXMLclient.php?lat={0}&lon={1}&product=time-series&begin={2}&end={3}&{4}"
    formattedUrl = noaaUrl.format(lat, lon, dateAsStandardDate(begin), dateAsStandardDate(end), noaaParams)
    # NOT returning the correct data
    forecastXml = urllib.request.urlopen(formattedUrl).read()
    return forecastXml

def notifyService(maxWind: int, forecasted: str):
    print("Max wind: " + str(maxWind))
    iftttUrl = "https://maker.ifttt.com/trigger/windy_soon/with/key/{0}?value1={1}&value2={2}"
    urllib.request.urlopen(iftttUrl.format(iftttKey, maxWind, forecasted))
    return

#---------------------------------------------------------------------------
# BEGINING OF EXECUTION

# first parameter can be the IFTTT key
if sys.argv.count > 1:
    iftttKey = sys.argv[1]

noaaForecast = fetchNOAAForecast(37.50, -77.64, begin, end, params)
rt = xml.etree.ElementTree.fromstring(noaaForecast)
i = max = maxLoc = 0

# Loop through looking for wind exceeding threshold
for wind in rt.iter('value'):
    if int(wind.text) > max:
        max = int(wind.text)
        maxLoc = i
    i += 1
    
# Notify service if wind exceeds threshold
if max > wind_threshold:
    forecastDate = ""
    i = 0
    for dt in rt.iter('start-valid-time'):
        if i == maxLoc:
            forecastDate = dt.text
        i += 1
    notifyService(max, forecastDate)
