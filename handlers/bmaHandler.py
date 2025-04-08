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
    session.get(bmaDefaultPath+"/session");


    loginReqObject = session.post(bmaDefaultPath + "/jwt/login", {"username": username, "password": password, "email": False, "active_directory": False}).json();
    session.post(bmaDefaultPath + "/login", {"username": username, "password": password, "email": False, "active_directory": False}).json();
    session.options(bmaDefaultPath+"/jwt/login");
    cookie = session.cookies.get_dict().get("PHPSESSID");

    loginToken = loginReqObject["token"];

    startSplit = dateStart.split(".");
    endSplit = dateEnd.split(".");

    startBackwards = startSplit[2] + "-" + startSplit[1] + "-" + startSplit[0];
    endBackwards = endSplit[2] + "-" + endSplit[1] + "-" + endSplit[0];

    thisLocationCode = locationCode(location=location);
    timeStrForXlsx = str(timeStart)+":00 - "+str(timeEnd)+":00"

    bmaRegularUrl = bmaDefaultPath + "/statistics/custom/hour/" + startBackwards + "%20" + "00:00:00/" + endBackwards + "%20" + "23:59:59/" + thisLocationCode + "/Europe/Helsinki";
    bmaVectorUrl = bmaDefaultPath + "/statistics/vector4d/" + thisLocationCode + "/hour/1/" + startBackwards + "%20" + "00:00:00/" + endBackwards + "%20" + "23:59:59/Europe/Helsinki";

    def dataFromUrl(location, url, bmaVectorUrl):
        if(location.upper() != "VIIKKI"):
            fetch = requests.get(url, headers={"Authorization": "Bearer " + loginToken, "Cookie": "PHPSESSID=" + cookie}).json();

            if(fetch["status"] == True):
                datesWithTimes = fetch["x_label"];
                dates = [];
                for date in datesWithTimes:
                    formattedDate = date.split(" ")[0];
                    if(formattedDate not in dates):
                        dates.append(formattedDate);

                data = fetch["data"];

                dayDataI1 = {}
                regularData = [];

                for i, x in enumerate(datesWithTimes):
                    h = x.split(" ")[1].split(":")[0];
                    pvm = x.split(" ")[0];

                    if((int(timeStart) <= int(h) < int(timeEnd)) or (int(timeStart) <= int(h) and int(timeEnd) == 24)):
                        if(pvm in dayDataI1):
                            dayDataI1[pvm].append(i);
                        else:
                            dayDataI1[pvm] = [i];
                

                for day in dayDataI1:
                    dayTotal = 0;
                    for dvc in data:
                        for i in dayDataI1[day]:
                            dayTotal += dvc["visitors"][i];
                    regularData.append(int(math.ceil(dayTotal / 2)));
                
                dataDict = dict();
                dataDict["data"] = regularData; # [1,2,33,34,5,23,12,...]
                dataDict["dates"] = dates;
                dataDict["time"] = timeStrForXlsx;
                dataDict["location"] = location.upper();

                return dataDict;
        
            else:
                return; # peak virheenkäsittely 🔥🔥⛄
    
        else: # erityiskohtelua rakkaan Viikkimme Vector4D:lle
            regularFetch = requests.get(url, headers={"Authorization": "Bearer " + loginToken, "Cookie": "PHPSESSID=" + cookie}).json();
            if(regularFetch["status"] == True):
                vector4dFetch = requests.get(bmaVectorUrl, headers={"Authorization": "Bearer " + loginToken, "Cookie": "PHPSESSID=" + cookie}).json();

                datesWithTimes = regularFetch["x_label"];
                regularData = [];
                vectorData = [];

                dates = [];
                for date in datesWithTimes:
                    formattedDate = date.split(" ")[0];
                    if(formattedDate not in dates):
                        dates.append(formattedDate);

                data = regularFetch["data"];
                dayDataI1 = {}
                for i, x in enumerate(datesWithTimes):
                    h = x.split(" ")[1].split(":")[0];
                    pvm = x.split(" ")[0];
                    if(int(timeStart) <= int(h) < int(timeEnd)):
                        if(pvm in dayDataI1):
                            dayDataI1[pvm].append(i);
                        else:
                            dayDataI1[pvm] = [i];
                for day in dayDataI1:
                    dayTotal = 0;
                    for dvc in data:
                        for i in dayDataI1[day]:
                            dayTotal += dvc["visitors"][i];
                    regularData.append(int(math.ceil(dayTotal / 2)))


#-----------------------------------------------------------
                dates = [];
                dayDataI2 = {};

                for i, x in enumerate(vector4dFetch["devices"][0]["data"]):
                    start = x["date_start"];
                    startDate = start.split(" ")[0];
                    h = start.split(" ")[1].split(":")[0];
                    if(int(timeStart) <= int(h) < int(timeEnd)):
                        if(startDate in dayDataI2):
                            dayDataI2[startDate].append(i);
                        else:
                            dayDataI2[startDate] = [i];
                            dates.append(startDate);

                for day in dayDataI2:
                    dayTotal = 0;
                    for device in vector4dFetch["devices"]:
                        hourTotal = 0;
                        for i in dayDataI1[day]:
                            try:
                                _data = device["data"];
                                a_i = _data[i]["adult_in"] if _data[i]["adult_in"] != None else 0;
                                a_o = _data[i]["adult_out"] if _data[i]["adult_out"] != None else 0;
                                t_i = _data[i]["teen_in"] if _data[i]["teen_in"] != None else 0;
                                t_o = _data[i]["teen_out"] if _data[i]["teen_out"] != None else 0;
                                c_i = _data[i]["child_in"] if _data[i]["child_in"] != None else 0;
                                c_o = _data[i]["child_out"] if _data[i]["child_out"] != None else 0;
                                hourTotal += (a_i + a_o + t_i + t_o + c_i + c_o);
                            except:
                                pass;
                        
                        dayTotal += hourTotal;
                    vectorData.append(int(math.ceil(dayTotal / 2)));

                resultArr = [];
                resultI = 0;
                while resultI < len(regularData):
                    resultArr.append(regularData[resultI] + vectorData[resultI]);
                    resultI += 1;

                dataDict = dict();
                dataDict["data"] = resultArr;
                dataDict["dates"] = dates;
                dataDict["time"] = timeStrForXlsx;
                dataDict["location"] = location.upper();

                return dataDict;
            else:
                return;
                
    session.close();
    return dataFromUrl(location, bmaRegularUrl, bmaVectorUrl);
