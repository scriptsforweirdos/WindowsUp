"""
Pulls XML from forecast.weather.gov
Parses Temp & Dew Point
Sends Win 10 Toast if weather conditions sufficient to open physical windows
Sends Win 10 Toast if weather conditions sufficient to close physical windows
Edit Lines 61-65 with your own local NWS XML and comfortable ranges.
"""
import json

from dateutil.parser import parse
import requests
import defusedxml.ElementTree as ET
from win10toast import ToastNotifier


def parseXML(path, savepath, lTemp, hTemp, lDew, hDew):
    params = [lTemp, hTemp, lDew, hDew]
    if not any(isinstance(x, int) for x in params):
        print("Please provide integers for Temps and Dew Points")
        return False
    lastData = json.load(open(savepath),)
    print("Previous Update: " + str(lastData["Time"]))
    print("Last window Status: " + str(lastData["windows"]))
    response = requests.get(path)
    xml_content = response.content
    root = ET.fromstring(xml_content)
    parsedTime = None
    currentTemp = None
    currentDewPoint = None
    for data in root.findall('data'):
        if data.attrib["type"] == "current observations":
            time = data.find('time-layout').find('start-valid-time').text
            parsedTime = parse(time, fuzzy=True)
            temps = data.find('parameters').findall('temperature')  # two, apparent and dew point
            for temp in temps:
                if temp.attrib["type"] == "apparent":
                    currentTemp = temp.find('value').text
                elif temp.attrib["type"] == "dew point":
                    currentDewPoint = temp.find('value').text
        if currentTemp and currentDewPoint and parsedTime:
            break
    print("Most Recent Update: " + str(parsedTime))
    print("Current Temp: " + str(currentTemp))
    print("Current Dew Point: " + str(currentDewPoint))
    if int(lTemp) <= int(currentTemp) <= int(hTemp) and int(lDew) <= int(currentDewPoint) <= int(hDew):
        windowStatus = "Open"
    else:
        windowStatus = "Close"
    if windowStatus != lastData["windows"]:
        toast = ToastNotifier()
        toast.show_toast(
            "Weather Update",
            windowStatus + " the windows",
            duration=None,
            icon_path='../weather.ico',
            threaded=True
        )
    wDict = {"Time": str(parsedTime), "Temp": currentTemp, "DP": currentDewPoint, "windows": windowStatus}
    output = json.dumps(wDict)
    with open(savepath, "w") as outfile:
        outfile.write(output)


if __name__ == "__main__":
    xmlpath = "https://forecast.weather.gov/MapClick.php?lat=41.9693&lon=-87.7253&unit=0&lg=english&FcstType=dwml"
    lowTemp = 65
    highTemp = 71
    lowDew = 0
    highDew = 60
    savePath = "../lastdata.txt"
    parseXML(xmlpath, savePath, lowTemp, highTemp, lowDew, highDew)
