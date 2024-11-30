from colorama import Fore, Back, Style
import lib.BaseFunction as base
import geoip2.database
import re

##########################################################
##########################################################

_B = Style.BRIGHT
_N = Style.NORMAL
_D = Style.DIM
_w = Fore.WHITE
_y = Fore.YELLOW
_b = Fore.BLUE
_r = Fore.RED
_c = Fore.CYAN
_g = Fore.GREEN
_m = Fore.MAGENTA
_by= Back.YELLOW + Fore.BLACK
_blg = Back.LIGHTGREEN_EX + Fore.BLACK
_bb = Back.BLUE + Fore.WHITE
_bc = Back.CYAN + Fore.WHITE
_br = Back.RED + Fore.WHITE
_bbw = Back.WHITE + Fore.BLACK
_bm = Back.MAGENTA + Fore.WHITE
_reset = Style.RESET_ALL


##########################################################
##########################################################
##########################################################
##########################################################
##########################################################
##########################################################


def GetGeoLocationFromIP(LocationDict:dict,GeoDB,IpAdress:str):
    """ Get Ip Location From GeoIpDatabase or list of locaion in config File
    Args: 
        LocationDict : Dict of Localtion From Config File
        GeoDB : Path of GeoIpDatabase
        IpAdress : IP Adrees For Search
    Returns:
        if Found a list Includes [ip,Country,Region,City,Latitude,Longitude,Time Zone]
        if Not Found return None
    """
    LocationLst = IpinLocationList(LocationDict,IpAdress)
    if LocationLst == None:
        LocationLst = GetIpLocationFromDatabase(IPAdress=IpAdress,GeoDatabaseName=GeoDB)
    return LocationLst



def IpinLocationList(LocationDict,IpAdrees):    
    for _LocationName in LocationDict:
        _locationLst = LocationDict[_LocationName]
        _IpLst = _locationLst['IP']
        for x in _IpLst:
            _Ip = RemoveObsoleteChar(x)
            if re.findall(f'^{_Ip}',IpAdrees):
                return _locationLst            
    return None
    
    

def RemoveObsoleteChar(IPStr):
    """Get Ip String and Remove '*' and '.' from end of string and return it"""    
    while True:
        CharisRemove = False
        if IPStr.endswith("*"):
            IPStr = IPStr[:-1]
            CharisRemove = True
        if IPStr.endswith("."):
            IPStr = IPStr[:-1]
            CharisRemove = True
        if IPStr.endswith("-"):
            IPStr = IPStr[:-1]
            CharisRemove = True
        if IPStr.endswith("_"):
            IPStr = IPStr[:-1]
            CharisRemove = True
        if IPStr.endswith("/"):
            IPStr = IPStr[:-1]
            CharisRemove = True
        if IPStr.endswith("/"):
            IPStr = IPStr[:-1]
            CharisRemove = True
        if CharisRemove is False:
            return IPStr

def GetIpLocationFromDatabase(IPAdress,GeoDatabaseName):
    try:        
    # Load the GeoLite2 City database
        with geoip2.database.Reader(GeoDatabaseName) as reader:
            response = reader.city(IPAdress)
        
        # Extract location information
            location_data = {
                "IP": IPAdress,
                "Country": response.country.name,
                "Region": response.subdivisions.most_specific.name,
                "City": response.city.name,
                "Latitude": response.location.latitude,
                "Longitude": response.location.longitude,
                "Time Zone": response.location.time_zone
        }
        return location_data
    except Exception as e:
        return None


def CheckLocationFilter_Country(Filter_Country,CountryName):
    if Filter_Country == []:
        return True
    elif CountryName.strip() == '':
        return True
    else:
        for _ in Filter_Country:
            if _.lower().strip() == CountryName.strip().lower():
                return True
    return False        


##########################################################
##########################################################
##########################################################
##########################################################
##########################################################

if __name__ == "__main__":        
    print(f"{Style.NORMAL + Fore.YELLOW}You should not run this file directly")  


