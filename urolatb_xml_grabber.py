  import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pytz

# Set timezone to Europe/Madrid
timezone = pytz.timezone('Europe/Madrid')

# Get today's date and calculate dates for the next 5 days
today = datetime.now(timezone)
dates = [today + timedelta(days=i) for i in range(0, 6)]

url = "https://www.urolatelebista.com/programacion"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

programs = []

for item in soup.find_all('div', class_='sppb-addon-content-wrap'):
    time = item.find('h3', class_='sppb-addon-title').text.strip()
    title_tag = item.find('p')
    title = title_tag.text.strip() if title_tag else "No title available"
    programs.append({'time': time, 'title': title.capitalize()})

# Sort programs by start time
programs.sort(key=lambda x: datetime.strptime(x['time'], '%H:%M'))

# Create XMLTV format output for each day
xmltv = '<?xml version="1.0" encoding="UTF-8"?>\n<tv>\n'
channel = '<channel id="urolatb.es"><display-name>Urola TB</display-name></channel>\n'
xmltv += channel

for date in dates:
    for i in range(len(programs)):
        time_obj = datetime.strptime(programs[i]['time'], '%H:%M')
        start_time = f"{date.strftime('%Y%m%d')}{time_obj.strftime('%H%M%S')} +0100"
        
        # Calculate stop time (next programme's start time or 1 hour if it's the last programme)
        if i + 1 < len(programs):
            next_time_obj = datetime.strptime(programs[i + 1]['time'], '%H:%M')
            end_time = f"{date.strftime('%Y%m%d')}{next_time_obj.strftime('%H%M%S')} +0100"
        else:
            # If it’s the last programme, set the stop time to 1 hour later
            end_time_obj = time_obj + timedelta(hours=1)
            end_time = f"{date.strftime('%Y%m%d')}{end_time_obj.strftime('%H%M%S')} +0100"
        
        xmltv += f'''
        <programme start="{start_time}" stop="{end_time}" channel="urolatb.es">
            <title>{programs[i]['title']}</title>
            <desc>{programs[i]['title']}</desc>
        </programme>
        '''

xmltv += '</tv>'

# Output the XMLTV formatted data
print(xmltv)
