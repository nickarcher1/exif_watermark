from geopy.geocoders import Nominatim

class time:
    def __init__(self, timestamp: str):
        self.year:   str = timestamp[0:4]
        self.month:  str = timestamp[5:7]
        self.day:    str = timestamp[8:10]
        self.hour:   str = timestamp[11:13]
        self.minute: str = timestamp[14:16]
    
    def add_lead_zero(self, h: int) -> str:
        if len(str(h)) == 1:
            return f"0{h}"
        return str(h)

    def murican_time(self) -> tuple[str, str]:
        h: int = int(self.hour)
        am_pm: str = "AM"
        if h>12:
            h-=12
            am_pm = "PM"
        elif h == 0:
            h=12
        return self.add_lead_zero(h), am_pm
    
    def get24hourTimestamp(self) -> str:
        return f"{self.hour}:{self.minute} {self.day}/{self.month}/{self.year}"

    def getMuricanTimestamp(self) -> str:
        adjusted_hour, am_pm = self.murican_time()
        return f"{adjusted_hour}:{self.minute} {am_pm}  {self.day}/{self.month}/{self.year}"

    def __str__(self) -> str:
        # return self.getMuricanTimestamp()
        return f"{self.day}/{self.month}/{self.year}"

class location:
    def __init__(self, loc_data: dict[int, tuple]):
        self.lat: float
        self.lon: float
        self.lat, self.lon = self.dms_to_dec(loc_data)
        geolocator = Nominatim(user_agent="my_geopy_app")   # I want to make this global or something
        self.location = geolocator.reverse(f"{self.lat},{self.lon}").raw['address']

    def dms_to_dec(self, loc_data: dict[int, tuple]) -> tuple[float, float]:
        dir1:    str = loc_data[1]
        dir1deg: str = loc_data[2][0]
        dir1min: str = loc_data[2][1]
        dir1sec: str = loc_data[2][2]
        dir2:    str = loc_data[3]
        dir2deg: str = loc_data[4][0]
        dir2min: str = loc_data[4][1]
        dir2sec: str = loc_data[4][2]
        
        lat = float(dir1deg) + float(dir1min)/60 + float(dir1sec)/3600
        if dir1 in ('S', 'W'):
            lat *= -1
        lon = float(dir2deg) + float(dir2min)/60 + float(dir2sec)/3600
        if dir2 in ('S', 'W'):
            lon *= -1

        return lat, lon

    def getCityState(self) -> str:
        if 'city' in self.location.keys():
            city = self.location['city']
        elif 'municipality' in self.location.keys():
            city = self.location['municipality']
        elif 'village' in self.location.keys():
            city = self.location['village']
        elif 'county' in self.location.keys():
            city = self.location['county']
        elif 'town' in self.location.keys():
            city = self.location['town']
        else:
            city = ''

        if 'state' in self.location.keys():
            state = self.location['state']
        elif 'province'  in self.location.keys():
            state = self.location['province']
        elif 'region'  in self.location.keys():
            state = self.location['region']
        else:
            state = ''

        citystate = city
        if citystate == '':
            citystate = state
        else:
            citystate += f", {state}"
        if city == state:
            return city
        
        return citystate
    
    def getCountry(self) -> str:
        country = self.location['country']
        if country == 'Schweiz/Suisse/Svizzera/Svizra':
            country = 'Schweiz'
        if country == 'België / Belgique / Belgien':
            country = 'België'
        return country
    
    def __str__(self) -> str:
        return f"{self.getCityState()}\n{self.getCountry()}"
 