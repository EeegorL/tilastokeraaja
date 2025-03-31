import requests;
import os;
import math;
from utils.utils import *;
from dotenv import load_dotenv;
load_dotenv();
from openpyxl import *;

def fetchData(location, dateStart, dateEnd, timeStart, timeEnd):
    bmaDefaultPath = os.getenv("BMA_DEFAULT_PATH");

    username = os.getenv("BMA_USERNAME_" + location.upper());
    password = os.getenv("BMA_PASSWORD_" + location.upper());
    
    session = requests.sessions.Session();
    session.get("https://api.bma.fi/session");

    bmaDefaultPath = "https://api.bma.fi";

    loginReqObject = session.post(bmaDefaultPath + "/jwt/login", {"username": username, "password": password, "email": False, "active_directory": False}).json();
    session.post(bmaDefaultPath + "/login", {"username": username, "password": password, "email": False, "active_directory": False}).json();
    session.options("https://api.bma.fi/jwt/login");
    cookie = session.cookies.get_dict().get("PHPSESSID");

    loginToken = loginReqObject["token"];

    startSplit = dateStart.split(".");
    endSplit = dateEnd.split(".");

    startBackwards = startSplit[2] + "-" + startSplit[1] + "-" + startSplit[0];
    endBackwards = endSplit[2] + "-" + endSplit[1] + "-" + endSplit[0];

    thisLocationCode = locationCode(location=location);

    bmaRegularUrl = bmaDefaultPath + "/statistics/custom/day/" + startBackwards + "%20" + timeStart + ":00/" + endBackwards + "%20" + timeEnd + ":00/" + thisLocationCode + "/Europe/Helsinki";
    bmaVectorUrl = bmaDefaultPath + "/statistics/vector4d/" + thisLocationCode + "/day/1/" + startBackwards + "%20" + timeStart + ":00/" + endBackwards + "%20" + timeEnd + ":00/Europe/Helsinki";

    def dataFromUrl(location, url, bmaVectorUrl):
        if(location.upper() != "VIIKKI"):
            fetch = requests.get(url, headers={"Authorization": "Bearer " + loginToken, "Cookie": "PHPSESSID=" + cookie}).json();

            if(fetch["status"] == True):
                dates = fetch["x_label"];
                data = fetch["data"];
                location = location;

                dataLength = len(dates);
                dataArray = [];
                dayIndex = 0;

                while dayIndex < dataLength:
                    dayTotal = 0;
                    for device in data:
                        dayTotal += device["visitors"][dayIndex];
                    dataArray.append(int(math.ceil(dayTotal / 2)));
                    dayIndex += 1;
                
                dataDict = dict();
                dataDict["data"] = dataArray;
                dataDict["dates"] = dates;
                dataDict["location"] = location.upper();

                return dataDict;
            else:
                return;

        else: # erityiskohtelua rakkaan Viikkimme Vector4D:lle
            regularFetch = requests.get(url, headers={"Authorization": "Bearer " + loginToken, "Cookie": "PHPSESSID=" + cookie}).json();
            if(regularFetch["status"] == True):
                vector4dFetch = requests.get(bmaVectorUrl, headers={"Authorization": "Bearer " + loginToken, "Cookie": "PHPSESSID=" + cookie}).json();

                dataArray = [];
                dates = regularFetch["x_label"];

                regularData = [];
                vectorData = [];

                day = 0;
                while day < len(dates):
                    regularTotal = 0;
                    for device in regularFetch["data"]:
                        if(type(device) == dict):            
                            visitors = device["visitors"];

                            regularTotal += visitors[day];

                    regularData.append(int(math.ceil(regularTotal / 2)));
                
                    vector4dTotal = 0;
                    for device in vector4dFetch["devices"]:
                        if(type(device) == dict):            
                            dayDataOfDevice = device["data"][day];
                            try:
                                vector4dTotal += int(dayDataOfDevice["adult_in"]) + int(dayDataOfDevice["adult_out"]) + int(dayDataOfDevice["teen_in"]) + int(dayDataOfDevice["teen_out"]) + int(dayDataOfDevice["child_in"]) + int(dayDataOfDevice["child_out"]);
                            except TypeError:
                                pass; # on ollut päiviä kun Vector4D-laskurit ovat olleet alhaalla, niin tällainen tähän, että ignooraa sellaiset päivät. ei siistein tapa, mutta hoitaa hommansa

                    vectorData.append(int(math.ceil(vector4dTotal / 2)));
                    day += 1;

                resultArr = [];
                resultI = 0;

                while resultI < len(regularData):
                    resultArr.append(regularData[resultI] + vectorData[resultI]);
                    resultI += 1;
            
                dataDict = dict();
                dataDict["data"] = resultArr;
                dataDict["dates"] = dates;
                dataDict["location"] = location.upper();
                
                return dataDict;
            else:
                return;
                
    session.close();
    return dataFromUrl(location, bmaRegularUrl, bmaVectorUrl);
