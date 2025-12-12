import requests
import json
from datetime import datetime, timedelta

# ==========================================
# 1. User Configuration (Modify this section)
# ==========================================
# Enter the 'Decoding' key obtained from data.go.kr here.
SERVICE_KEY = "YOUR_DECODED_SERVICE_KEY_HERE"

# Grid coordinates (e.g., Jongno-gu, Seoul -> 60, 127)
# Search for "KMA grid coordinates Excel" to find your local coordinates.
NX = "60"
NY = "127"

# ==========================================
# 2. KMA API Base Time Calculation Logic
# ==========================================
def get_base_date_time():
    """
    KMA Short-term Forecast updates every 3 hours (02:00, 05:00, 08:00, etc.).
    This function calculates the most recent announcement time (base_time)
    that occurred before the current time.
    """
    now = datetime.now()
    
    # KMA recommends allowing approx. 10 minutes buffer (45 min past the hour)
    if now.minute < 45: 
        now = now - timedelta(hours=1)
        
    # Standard announcement times are 02, 05, 08, 11, 14, 17, 20, 23
    current_hour = now.hour
    base_date = now.strftime('%Y%m%d')
    
    # Base Time Logic
    if current_hour < 2:
        # 00, 01 hours use the previous day's 2300 data
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
    base_date, base_time = get_base_date_time()
    
    url = 'http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst'
    
    params = {
        'serviceKey': SERVICE_KEY,
        'pageNo': '1',
        'numOfRows': '1000', # Request enough rows
        'dataType': 'JSON',
        'base_date': base_date,
        'base_time': base_time,
        'nx': NX,
        'ny': NY
    }

    try:
        response = requests.get(url, params=params)
        
        # Check HTTP status code
        if response.status_code != 200:
            print(f"Error: Server response code {response.status_code}")
            return

        data = response.json()
        
        # Handle API error messages inside the JSON
        if data['response']['header']['resultCode'] != '00':
            print(f"API Error: {data['response']['header']['resultMsg']}")
            return

        items = data['response']['body']['items']['item']
        
        # Dictionary to store filtered weather data
        weather_data = {}
        
        # KMA data is scattered by category (TMP, PTY, etc.).
        # We only take data for the earliest forecast time (fcstTime)
        if not items:
            print("Error: No forecast items received.")
            return
            
        target_time = items[0]['fcstTime'] 

        for item in items:
            if item['fcstTime'] == target_time:
                cat = item['category']
                val = item['fcstValue']
                weather_data[cat] = val

        # ==========================================
        # 4. Output Generation
        # ==========================================
        # TMP: 1-hour temperature, SKY: Sky status, PTY: Precipitation type
        temp = weather_data.get('TMP', '-')
        sky = weather_data.get('SKY', '0') # 1:Clear, 3:Mostly Cloudy, 4:Cloudy
        pty = weather_data.get('PTY', '0') # 0:None, 1:Rain, 2:Rain/Snow, 3:Snow, 4:Shower
        
        # Text conversion logic
        weather_str = ""
        if pty != '0':
            # Precipitation takes precedence over sky status
            pty_map = {'1':'Rain', '2':'Rain/Snow', '3':'Snow', '4':'Shower'}
            weather_str = pty_map.get(pty, 'Wet')
        else:
            sky_map = {'1':'Clear', '3':'Cloudy', '4':'Overcast'}
            weather_str = sky_map.get(sky, 'Unknown')

        print(f"{weather_str} {temp}°C")

    except Exception as e:
        print(f"Failed to fetch data: {e}")

if __name__ == "__main__":
    fetch_weather()
