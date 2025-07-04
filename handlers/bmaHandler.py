import requests;
import os;
import math;
from utils.utils import *;
from dotenv import load_dotenv;
load_dotenv();

def fetchData(location: str, dateStart: str, dateEnd: str, timeStart: str, timeEnd: str):
    bmaDefaultPath = os.getenv("BMA_DEFAULT_PATH");
    username = os.getenv(f"BMA_USERNAME_{location.upper()}");
    password = os.getenv(f"BMA_PASSWORD_{location.upper()}");
    
    session = requests.sessions.Session();
    session.get(f"{bmaDefaultPath}/session");

    loginReqObject = session.post(f"{bmaDefaultPath}/jwt/login", {"username": username, "password": password, "email": False, "active_directory": False}).json();
    session.post(f"{bmaDefaultPath}/login", {"username": username, "password": password, "email": False, "active_directory": False}).json();
    session.options(f"{bmaDefaultPath}/jwt/login");
    cookie = session.cookies.get_dict().get("PHPSESSID");

    loginToken = loginReqObject["token"];

    startSplit = dateStart.split(".");
    endSplit = dateEnd.split(".");

    startBackwards = f"{startSplit[2]}-{startSplit[1]}-{startSplit[0]}";
    endBackwards = f"{endSplit[2]}-{endSplit[1]}-{endSplit[0]}";

    thisLocationCode = locationCode(location=location);
    timeStrForXlsx = f"{str(timeStart)}:00 - {str(timeEnd)}:00"

    bmaRegularUrl = f"{bmaDefaultPath}/statistics/custom/hour/{startBackwards}%2000:00:00/{endBackwards}%2023:59:59/{thisLocationCode}/Europe/Helsinki";
    bmaVectorUrl = f"{bmaDefaultPath}/statistics/vector4d/{thisLocationCode}/hour/1/{startBackwards}%2000:00:00/{endBackwards}%2023:59:59/Europe/Helsinki";

    # tavallinen fetch
    # ------------------------
    regularFetch = requests.get(bmaRegularUrl, headers={"Authorization": f"Bearer {loginToken}", "Cookie": f"PHPSESSID={cookie}"}).json();

    if(regularFetch["status"] == True): 
        vector4dFetch = requests.get(bmaVectorUrl, headers={"Authorization": f"Bearer {loginToken}", "Cookie": f"PHPSESSID={cookie}"}).json(); # aloittaa Vector4D haun vain jos "tavallinen" haku onnistuu. 
        datesWithTimes = regularFetch["x_label"];
        regularData = [];
        vectorData = [];

        dates = [];
        dayDataIndexes = {}
        
        for date in datesWithTimes:
            justTheDate = date.split(" ")[0];
            if(justTheDate not in dates):
                dates.append(justTheDate);

        data = regularFetch["data"];
        
        for i, x in enumerate(datesWithTimes):
            hour = x.split(" ")[1].split(":")[0];
            date = x.split(" ")[0];
            if(int(timeStart) <= int(hour) < int(timeEnd)):
                if(date in dayDataIndexes):
                    dayDataIndexes[date].append(i);
                else:
                    dayDataIndexes[date] = [i];
        
        for day in dayDataIndexes:
            dayTotal = 0;
            for device in data:
                for i in dayDataIndexes[day]:
                    dayTotal += device["visitors"][i];
            regularData.append(int(math.ceil(dayTotal / 2)))

    # Vector4D fetch
    # ------------------------
        dates = [];
        dayDataIndexes_Vector4D = {};
        if(len(vector4dFetch["devices"]) > 0):
            try:
                for i, x in enumerate(vector4dFetch["devices"][0]["data"]):
                    start = x["date_start"];
                    startDate = start.split(" ")[0];
                    hour = start.split(" ")[1].split(":")[0];
                    if(int(timeStart) <= int(hour) < int(timeEnd)):
                        if(startDate in dayDataIndexes_Vector4D):
                            dayDataIndexes_Vector4D[startDate].append(i);
                        else:
                            dayDataIndexes_Vector4D[startDate] = [i];
                            dates.append(startDate);
                
                for day in dayDataIndexes_Vector4D:
                    dayTotal = 0;
                    for device in vector4dFetch["devices"]:
                        hourTotal = 0;
                        for i in dayDataIndexes[day]:
                            try:
                                _data = device["data"];
                                adult_in = _data[i]["adult_in"] if _data[i]["adult_in"] != None else 0;
                                adult_out = _data[i]["adult_out"] if _data[i]["adult_out"] != None else 0;
                                teen_in = _data[i]["teen_in"] if _data[i]["teen_in"] != None else 0;
                                teen_out = _data[i]["teen_out"] if _data[i]["teen_out"] != None else 0;
                                child_in = _data[i]["child_in"] if _data[i]["child_in"] != None else 0;
                                child_out = _data[i]["child_out"] if _data[i]["child_out"] != None else 0;
                                hourTotal += (adult_in + adult_out + teen_in + teen_out + child_in + child_out);
                            except: # lähinnä jos laskurit ovat pois päältä ja tulee tyhjää dataa
                                pass;
                
                        dayTotal += hourTotal;
                    vectorData.append(int(math.ceil(dayTotal / 2)));
            except Exception: # tänne ei kai pitäisi mennä, ellei BMA:n palvelu räjähdä tms.
                pass;
        
        resultArr = [];
        resultI = 0;
        while resultI < len(regularData):
            daytotal = regularData[resultI];
            if(len(vectorData) > 0): daytotal += vectorData[resultI];
            
            resultArr.append(daytotal);
            resultI += 1;
 
        dataDict = dict();
        dataDict["data"] = resultArr;
        dataDict["dates"] = dates;
        dataDict["time"] = timeStrForXlsx;
        dataDict["location"] = location.upper();

        session.close();
        return dataDict;
    else:
        session.close();
        return;