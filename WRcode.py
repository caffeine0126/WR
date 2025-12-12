import requests
import json
import os # 환경 변수를 사용하기 위해 추가
from datetime import datetime, timedelta

# ==========================================
# 1. User Configuration & Authentication
# ==========================================
# Get the key from the system environment variable KMA_API_KEY.
SERVICE_KEY = os.environ.get("KMA_API_KEY") 

# Grid coordinates (Modify this)
NX = "60"
NY = "127"

# ==========================================
# 2. KMA API Base Time Calculation Logic
# ==========================================
def get_base_date_time():
    """
    Calculates the base_date and base_time for the API request.
    It uses a 15-minute buffer (current minute < 45) to ensure stability.
    """
    now = datetime.now()
    
    # Allow a 15-minute buffer for KMA server updates
    if now.minute < 45: 
        now = now - timedelta(hours=1)
        
    current_hour = now.hour
    base_date = now.strftime('%Y%m%d')
    
    # Standard announcement times are 02, 05, 08, 11, 14, 17, 20, 23
    if current_hour < 2:
        base_time = "2300"
        base_date = (now - timedelta(days=1)).strftime('%Y%m%d')
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
# 3. Data Request and Parsing
# ==========================================
def fetch_weather():
    # ⚠️ Authentication Check
    if not SERVICE_KEY:
        print("Error: KMA_API_KEY environment variable is not set.")
        print("Please set the key using: export KMA_API_KEY=\"YOUR_KEY\"")
        return
        
    base_date, base_time = get_base_date_time()
    
    # 🚨 DEBUG: Output the calculated base time for troubleshooting 401 errors
    print(f"DEBUG_TIME: {base_date} {base_time}") 
    
    url = 'http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst'
    
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
        response = requests.get(url, params=params, timeout=5) # 5초 타임아웃 추가
        
        # Check HTTP status code
        if response.status_code != 200:
            print(f"HTTP Error: {response.status_code} (Check network or base_time)")
            return

        data = response.json()
        
        # Handle API error messages inside the JSON
        if data['response']['header']['resultCode'] != '00':
            print(f"API Error ({data['response']['header']['resultCode']}): {data['response']['header']['resultMsg']}")
            return

        items = data['response']['body']['items']['item']
        
        if not items:
            print("Error: No forecast items received. Base time might be invalid.")
            return
            
        weather_data = {}
        target_time = items[0]['fcstTime'] 

        for item in items:
            if item['fcstTime'] == target_time:
                cat = item['category']
                val = item['fcstValue']
                weather_data[cat] = val

        # ==========================================
        # 4. Output Generation (Modify for Polybar/Conky)
        # ==========================================
        temp = weather_data.get('TMP', '-')
        sky = weather_data.get('SKY', '0')
        pty = weather_data.get('PTY', '0')
        
        # Text conversion logic
        weather_str = ""
        if pty != '0':
            pty_map = {'1':'Rain', '2':'R/S', '3':'Snow', '4':'Shower'}
            weather_str = pty_map.get(pty, 'Wet')
        else:
            sky_map = {'1':'Clear', '3':'Cloudy', '4':'Overcast'}
            weather_str = sky_map.get(sky, 'Unknown')

        # Polybar에 바로 출력하기 위해 DEBUG 메시지 제거
        print(f"{weather_str} {temp}°C")

    except requests.exceptions.Timeout:
        print("Request Timeout")
    except requests.exceptions.ConnectionError:
        print("Connection Error")
    except Exception as e:
        print(f"Fetch Failed: {e}")

if __name__ == "__main__":
    fetch_weather()
