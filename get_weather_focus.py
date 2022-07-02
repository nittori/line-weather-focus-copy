import json
import urllib.request as req
import time
import datetime
import os
from dateutil import tz

def get_json(area_code):
    today=time.strftime("%y%m%d")
    json_url=f"https://www.jma.go.jp/bosai/forecast/data/forecast/{area_code}.json" 
    file_abs_path = os.path.abspath(__file__)
    file_dir = os.path.dirname(file_abs_path)
    filename = file_dir+f"/{today}_{area_code}.json"
        
    req.urlretrieve(json_url, filename)    
    return filename

def read_json(filename):
    with open(filename, 'r', encoding="UTF-8") as f:
        data = json.load(f)
    return data
    
def get_various_code(area_code):
    codes = []
    tmp_code = ""
    for s in area_code:
        if s == "-":
            codes.append(tmp_code)
        else :
            tmp_code += s
    prefecture_code = codes[0]
    local_code = codes[1]
    municipality_code = codes[2]

    return prefecture_code,local_code,municipality_code

def get_weather_focus():    
    JST = tz.gettz('Asia/Tokyo')
    now = datetime.datetime.now(JST)
    today = datetime.datetime.date(now)
    
    area_code = os.environ.get("area_code")
    prefecture_code,local_code,municipality_code = get_various_code(area_code)
    
    #data取得
    
    web_link=f"https://www.jma.go.jp/bosai/forecast/#area_type=offices&area_code={prefecture_code}"
    
    filename = get_json(prefecture_code)
    data = read_json(filename)
    
    #0-0 天気予報
    
    timeDefines = data[0]["timeSeries"][0]["timeDefines"]#取得日、明日、明後日の日付
    for idx,timeDefine in enumerate(timeDefines):
        timeDefine = datetime.datetime.strptime(timeDefine, '%Y-%m-%dT%H:%M:%S%z')
        timeDefine_date = datetime.datetime.date(timeDefine)
        if today == timeDefine_date:
            time_num = idx
            continue
    
    areas = data[0]["timeSeries"][0]["areas"]
    
    for area in areas:
        if local_code == area["area"]["code"]:
            area_name = area["area"]["name"]
            weather = area["weathers"][time_num]
            weather = weather.replace("\u3000", "")
            continue
    
    #0-1 降水確率
    timeDefines = data[0]["timeSeries"][1]["timeDefines"]
    areas = data[0]["timeSeries"][1]["areas"]
    
    for area in areas:
        if local_code == area["area"]["code"]:
            pops = []
            times = []
            for i in range(len(timeDefines)):
                if i == 0:
                    continue
                pops.append(area["pops"][i])
                timeDefine = datetime.datetime.strptime(timeDefines[i], '%Y-%m-%dT%H:%M:%S%z')
                hour = timeDefine.hour
                times.append(f"{hour}-{(hour+6)%24}")
    
    pops_data = ""
    for t in times:
        pops_data += t+" "
    pops_data += "\n"
    for pop in pops:    
        pops_data += pop+"%  "
        
        
    #0-2 市町村、最高気温、最低気温
    timeDefines = data[0]["timeSeries"][2]
    areas = data[0]["timeSeries"][2]["areas"]
    for area in areas:
        if municipality_code == area["area"]["code"]:
            municipality_name = area["area"]["name"]
            min_temp = area["temps"][0]
            max_temp = area["temps"][1]
    
    #1-0 prefecture
    prefecture = data[1]["timeSeries"][0]["areas"][0]["area"]["name"]
    
    header = f"{today.strftime('%Y年%m月%d日')} \n" 
    body1 = f"-天気- \n{weather}\n"
    body2 = f"-降水確率- \n{pops_data}\n"
    body3 = f"-{municipality_name}の気温-\n最高気温 : {max_temp}°C\n最低気温 : {min_temp}°C\n" 
    footer = f"\n{web_link}"
    
    text = header+body1+body2+body3+footer
    print(text)
    return text
    
if __name__ == "__main__":
    get_weather_focus()
    