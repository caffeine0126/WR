import requests
import json
import os
import sys
from datetime import datetime, timedelta

# ==========================================
# 1. Configuration (Set your coordinates here)
# ==========================================
# Get the key from the system environment variable
SERVICE_KEY = os.environ.get("KMA_API_KEY") 

# Grid coordinates (Updated based on your input: 61, 119)
NX = "61" 
NY = "119" 

# KMA API endpoint
API_URL = 'http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst'

# ==========================================
# 2. Base Time Calculation (KST Environment)
# ==========================================
def get_base_date_time():
    """
    Calculates the most recent KMA announcement time (02, 05, 08... 23h).
    Assumes system time is set to KST (Asia/Seoul).
    """
    now = datetime.now()
    
    # 45분 이전이라면, 이전 시간대 데이터가 최신입니다. (예: 08:30 -> 0500 데이터 사용)
    if now.minute < 45: 
        target_time = now - timedelta(hours=1)
    else:
        target_time = now
        
    current_hour = target_time.hour
    base_date = target_time.strftime('%Y%m%d')
    
    # KMA Standard announcement times (02, 05, 08, 11, 14, 17, 20, 23)
    if current_hour < 2:
        # 00, 01 hours use the previous day's 2300 data
        base_time = "2300"
        base_date = (target_time - timedelta(days=1)).strftime('%Y%m%d')
    elif current_hour < 5:
        base_time = "0200"
    elif current_hour < 8:
        base_time = "0500"
    elif current_hour < 11:
        base_time = "0800"
    elif current_hour < 14:
        base_time = "1100"
    elif current_hour < 17:
        base_time = "1400"
    elif current_hour < 20:
        base_time = "1700"
    elif current_hour < 23:
        base_time = "2000"
    else:
        base_time = "2300"
        
    return base_date, base_time

# ==========================================
# 3. Data Fetch and Parse
# ==========================================
def fetch_weather():
    # ⚠️ Authentication Check & Exit
    if not SERVICE_KEY:
        # 키가 설정되지 않은 경우 에러 출력 (stderr로 보내 Polybar 출력 방지)
        print("KEY_ERR", file=sys.stderr)
        return

    base_date, base_time = get_base_date_time()
    
    # 🚨 Final Debugging Output (to stderr)
    print(f"DEBUG: Base Time {base_date} {base_time}, NX/NY: {NX}/{NY}", file=sys.stderr) 

    params = {
        'serviceKey': SERVICE_KEY,
        'pageNo': '1',
        'numOfRows': '1000',
        'dataType': 'JSON',
        'base_date': base_date,
        'base_time': base_time,
        'nx': NX,
        'ny': NY
    }

    try:
        response = requests.get(API_URL, params=params, timeout=7)
        
        if response.status_code != 200:
            print(f"HTTP_{response.status_code}", file=sys.stderr)
            return

        data = response.json()
        
        result_code = data['response']['header']['resultCode']
        if result_code != '00':
            print(f"API_ERR_{result_code}", file=sys.stderr)
            return

        items = data['response']['body']['items']['item']
        
        if not items:
            print("NO_DATA", file=sys.stderr)
            return
            
        weather_data = {}
        target_time = items[0]['fcstTime'] 

        for item in items:
            if item['fcstTime'] == target_time:
                weather_data[item['category']] = item['fcstValue']

        # ==========================================
        # 4. Output Formatting (For Polybar)
        # ==========================================
        temp = weather_data.get('TMP', '-')
        sky = weather_data.get('SKY', '0')
        pty = weather_data.get('PTY', '0')
        
        weather_str = ""
        # ☔ PTY (강수 형태)가 우선
        if pty != '0':
            # Nerd Font icons: Rain, Rain/Snow, Snow, Shower
            pty_map = {'1':'', '2':'', '3':'', '4':''} 
            weather_str = pty_map.get(pty, '')
        # ☁️ SKY (하늘 상태)
        else:
            # Nerd Font icons: Clear, Cloud, Overcast
            sky_map = {'1':'', '3':'', '4':''} 
            weather_str = sky_map.get(sky, '')

        # 최종 출력 (예:  -2°C)
        print(f"{weather_str} {temp}°C")

    except requests.exceptions.RequestException:
        print("NET_FAIL", file=sys.stderr)
    except Exception as e:
        print(f"FATAL_ERR: {e}", file=sys.stderr)

if __name__ == "__main__":
    fetch_weather()
