#! /usr/bin/python3
import signal
import lib.BaseFunction as base
import lib.AsciArt as AsciArt
import re
import os
from datetime import datetime, timedelta
import Banner
from collections import OrderedDict,Counter
from datetime import datetime
import sys
import dockerLib
import GeoIpLocation
import color.Back as Back
import color.Fore as Fore
import color.Style as Style
from color.Style import _B,_D,_N,_reset
from color.Back import _bw,_by,_bb,_bbl,_br,_bc,_bg,_bm,_brst,_bEx_w,_bEx_y,_bEx_b,_bEx_bl,_bEx_r ,_bEx_c ,_bEx_g ,_bEx_m ,_b_rest
from color.Fore import _fw,_fy,_fb,_fbl,_fr,_fc,_fg,_fm,_fEx_w,_fEx_y,_fEx_b,_fEx_bl,_fEx_r,_fEx_c,_fEx_g,_fEx_m,_f_reset



####################################################


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


####################################################

current_directory = os.path.dirname(os.path.realpath(__file__))
JsonConfigFile = f"{current_directory}/config/config.json"
jsonConfig = base.LoadJsonFile(JsonConfigFile)
LogsMode = base.GetValue(jsonConfig,'ParsingMode',verbus=False).lower()
Proxy_or_LoadBalance = base.GetValue(jsonConfig,'Proxy_or_LoadBalance',verbus=False,ReturnValueForNone='false')
GLOBAL_SEARCH_METHOD = base.GetValue(jsonConfig,'SearchMode',verbus=False,ReturnValueForNone='')
GLOBAL_SEARCH_METHOD_ALIAS = ''
SEARCHDISCRIPTION = ''

#MAX_LINE = jsonConfig["Max_Line_view",'']
MAX_LINE = base.GetValue(jsonConfig,'Max_Line_view',verbus=False,ReturnValueForNone=60)
EXP_PATH = base.GetValue(jsonConfig,'ExportPath',verbus=False,ReturnValueForNone='/tmp')

GEO_DB_NAME = base.GetValue(jsonConfig,'GeoConfig','GeoDatabasePath')
MY_GEO_LOCATION = base.GetValue(jsonConfig,'GeoConfig','location')

####################################################



signal.signal(signal.SIGINT, base.handler)

####################################################
####################################################
####################################################
####################################################




def CheckSearchMode(GlobalSearchMode):        
    global SEARCHDISCRIPTION
    global GLOBAL_SEARCH_METHOD
    global GLOBAL_SEARCH_METHOD_ALIAS
    if GlobalSearchMode.lower() == 'start':
        SEARCHDISCRIPTION = 'The search term must be at the beginning of the phrase.'
        GLOBAL_SEARCH_METHOD_ALIAS = 'start with'
    elif GlobalSearchMode.lower() == 'end':
        SEARCHDISCRIPTION = 'The search term must be at the end of the phrase.'
        GLOBAL_SEARCH_METHOD_ALIAS = 'end with'
    elif GlobalSearchMode.lower() == 'all':
        SEARCHDISCRIPTION = 'The search term can be anywhere in the phrase.'
        GLOBAL_SEARCH_METHOD_ALIAS = 'Anywhere'
    elif GlobalSearchMode.lower() == 'exactly':
        SEARCHDISCRIPTION = 'Search term exactly matches the phrase'
        GLOBAL_SEARCH_METHOD_ALIAS = 'match exactly'        
    else:
        GLOBAL_SEARCH_METHOD = 'start'
        SEARCHDISCRIPTION = 'The search term must be at the beginning of the phrase.'
        GLOBAL_SEARCH_METHOD_ALIAS = 'start with'
def ChangeSearchMode(SearchMode):
    while True:
        Selected = f'{_by}'
        Start_Select = ''
        End_Select = ''
        All_Select = ''
        exactly_Select = ''
        if SearchMode.lower() == 'start':
            Start_Select = Selected
            End_Select = All_Select = exactly_Select = ''
        elif SearchMode.lower() == 'end':
            End_Select = Selected
            Start_Select = All_Select = exactly_Select = ''            
        elif SearchMode.lower() == 'all':
            All_Select = Selected
            Start_Select = End_Select = exactly_Select = ''            
        elif SearchMode.lower() == 'exactly':
            exactly_Select = Selected
            Start_Select = End_Select = All_Select = ''            
        else:
            SearchMode = ''
        base.clearScreen()
        Banner.ParsingLogo()    
        print(f"{_w}")
        print(f"press [ {_D}{_w}Enter{_N}{_w} ] for back{_reset}")        
        print(f"type  [ {_D}{_w}0{_N}{_w} ]  for quit{_reset}")        
        print(f"      [ {_c}{Start_Select}start{_reset}{_w}   ] {_c}The search term must be at the beginning of the phrase.{_reset}")
        print(f"      [ {_c}{End_Select}end{_reset}{_w}     ] {_c}The search term must be at the end of the phrase.{_reset}")
        print(f"      [ {_c}{All_Select}all{_reset}{_w}     ] {_c}The search term can be anywhere in the phrase.{_reset}")
        print(f"      [ {_c}{exactly_Select}exactly{_reset}{_w} ] {_c}Search term exactly matches the phrase{_reset}")
        print("")
        SearchModeInput = input(f"{_B}{_w}Enter Search Mode or press {_b}Enter{_w} for back :{_reset}")        


        if SearchModeInput.lower().strip() in ['start','end','all','exactly',""]:
            return SearchModeInput.lower().strip()        
        else:
            base.PrintMessage(messageString=f'Value ( {SearchModeInput} ) not valid',MsgType="error", AddLine = True, addSpace = 0)
            input(f'{_reset}{_D}{_w}press enter ...{_reset}')

def ChangeSearchModeLuncher(_GlobalSearchMode):
    global SEARCHDISCRIPTION
    global GLOBAL_SEARCH_METHOD
    SearchMode = ChangeSearchMode(_GlobalSearchMode)    
    CheckSearchMode(SearchMode)
    GLOBAL_SEARCH_METHOD = SearchMode    
    

if LogsMode == None:
    base.PrintMessage('Section [ParsingMode] not found in config found',MsgType="error",TreminateApp=True,addSpace=0,AddLine=False)

if LogsMode == 'file':
    LOG_FILE = base.GetValue(jsonConfig,'LocalMode','Log_File',verbus=False)
    if LOG_FILE == None:
        base.PrintMessage('Section [Log_File] not found in config found',MsgType="error",TreminateApp=True,addSpace=0,AddLine=False)        
elif LogsMode == 'docker':
    ContainerName =  base.GetValue(jsonConfig,"Docker_Api_Server","container_name",verbus=False)
    if ContainerName == 'none':
        base.PrintMessage('Section [container_name] not found in config found',MsgType="error",TreminateApp=True,addSpace=0,AddLine=False)                
else:
    base.PrintMessage('Value section [LogsMode] not detected ',MsgType="error",TreminateApp=True,addSpace=0,AddLine=False)                

def read_file_once(file_path):
    # Static variable to store the file content
    if not hasattr(read_file_once, "_file_content"):
        try:
            with open(file_path, "r") as file:
                # Read and store the file content
                read_file_once._file_content = file.read()
        except FileNotFoundError:
            print(f"Error: File not found at {file_path}")
            read_file_once._file_content = None
    return read_file_once._file_content


def LoadLogFile(ReloadLog = False):
    global TimeofReadLogFile
    global CountLogs
    global To_Date
    global From_Date 
    global url_counter

    TimeofReadLogFile = datetime.now()        
    # Regex        
    #url_pattern = re.compile(r'"GET\s(\/[^\s]*)')

    global COUNTRY_COUNTER
    global TIMEZONE_COUNTER
    global REGION_COUNTER
    global CITY_COUNTER
    global REFERER_COUNTER
    COUNTRY_COUNTER = Counter()    
    TIMEZONE_COUNTER = Counter()    
    CITY_COUNTER = Counter()
    REGION_COUNTER = Counter()    
    REFERER_COUNTER = Counter()

    global Ip_counter
    global url_counter    
    global Agent_counter
    global Unknown_Agent_counter    
    global All_Agent_counter
    global browser_counter
    global status_code_counter
    global UnknowAgentName
    global FirstLine    
    global LogsStr
    UnknowAgentName = ""
    url_counter = Counter()
    Ip_counter = Counter()    
    Agent_counter = Counter()    
    Unknown_Agent_counter= Counter()
    All_Agent_counter = Counter()
    browser_counter = Counter()
    status_code_counter = Counter()
    CountLogs = 0
    base.clearScreen()
    Banner.PleaseWait()
    if LogsMode == 'file':
        read_lines = 0
    
        try:        
            if LogsStr == str: # Check Variable get data
                pass
        except:
            ReloadLog = True

        if ReloadLog:
            LogsStr = read_file_once(LOG_FILE)
        total_lines = len(LogsStr.splitlines())
        print(f" Total lines: {_B}{_w}{total_lines}{_reset}")

        FirstLine = True
        matchFound = False

        for _line in LogsStr.splitlines():
            if re.search(Date_pattern, _line) == None:
                continue
            else:
                matchFound = True                
            _rst = ParingLogFileWithFilter(_line)            
            if _rst != '':                    
                Ip_counter[_rst["IP"]] +=1
                url_counter[_rst["URL"]] += 1
                status_code_counter[_rst["CODE"]] += 1                    
                REFERER_COUNTER[_rst["REFERER"]] += 1
                if _rst["BORWSER"] != 'unknow':
                    browser_counter[_rst["BORWSER"]] += 1
                else:
                    Unknown_Agent_counter[_rst["ALL_AGENT"]] += 1                        
            read_lines += 1
            progress = (read_lines / total_lines) * 100
            print(f" Progress: {_B}{_y}{progress:.2f}%{_reset}", end="\r")

        if matchFound == False:            
            msg = """
The log structure does not match the Nginx log structure.
This situation occurs in the following cases:

  - The file specified is not the Nginx access.log file.
  - Nginx has just been launched and has not yet received any requests from the browser.

In the Nginx config, make sure the path to the access.log."""

            base.clearScreen()
            Banner.ParsingLogo()
            AsciArt.BorderIt(Text=msg,BorderColor=_r,TextColor=_y)            
            base.FnExit()
    else:
        #logs = CONTAINER.logs().decode("utf-8")        
        try:        
            if LogsStr == str: # Check Variable get data
                pass
        except:            
            ReloadLog = True
        if ReloadLog:            
            print(f"{_B}{_w} Fetch Log From Docker Container ....")
            LogsStr = dockerLib.LoadContainerLog(CONTAINER,DOCKER_IS_LOCAL)            
            base.clearScreen()
            Banner.PleaseWait()    

        total_lines = len(LogsStr.splitlines())
        FirstLine = True
        matchFound = False
        processed_length = 0
        print(f" Total lines: {_B}{_w}{total_lines}{_reset}")
        for _line in LogsStr.splitlines():
            processed_length += 1
            progress = (processed_length / total_lines) * 100
            #print(f"Progress: {progress:.2f}%", end="\r")
            print(f" Progress: {_B}{_y}{progress:.2f}%{_reset}", end="\r")
            if re.search(Date_pattern, _line) == None:
                continue
            else:
                matchFound = True
            _rst = ParingLogFileWithFilter(_line)                                

            if _rst != '':                
                Ip_counter[_rst["IP"]] +=1
                url_counter[_rst["URL"]] += 1
                status_code_counter[_rst["CODE"]] += 1                    
                REFERER_COUNTER[_rst["REFERER"]] += 1
                if _rst["BORWSER"] != 'unknow':
                    browser_counter[_rst["BORWSER"]] += 1
                else:
                    Unknown_Agent_counter[_rst["ALL_AGENT"]] += 1
                
#                if GEO_IS_DISABLE is False:
#                    UpdateGepCounter(_rst["GEO"])                                    
        
        if matchFound == False:            
            msg = """
The log structure does not match of the Nginx container log structure.
This situation occurs in the following cases:
  - The declared container is not an Nginx container.
  - The log path is redirected to a file in the Nginx configuration.
  - The container has just been started and has not yet received any requests in the browser.
"""
        
            base.clearScreen()
            Banner.ParsingLogo()
            AsciArt.BorderIt(Text=msg,BorderColor=_r,TextColor=_y)                        
            base.FnExit()
        else:
            AnalyzedDetectedIpFromGeo()    

def AnalyzedDetectedIpFromGeo():
    AddThisLine = True
    for ip_address in Ip_counter:
        LocationLst = GeoIpLocation.GetGeoLocationFromIP(LocationDict=MY_GEO_LOCATION,GeoDB=GEO_DB_NAME,IpAdress=ip_address,FilterOnCountry=FILTER_COUNTRY)
        if LocationLst != None:            
            UpdateGepCounter(LocationLst)     

def UpdateGepCounter(_rst):
    global COUNTRY_COUNTER
    global TIMEZONE_COUNTER
    global REGION_COUNTER
    global CITY_COUNTER
#    COUNTRY_COUNTER = Counter()    
#    TIMEZONE_COUNTER = Counter()    
#    CITY_COUNTER = Counter()
#    REGION_COUNTER = Counter()
    
    __Country = _rst["Country"]    
    __City = _rst["City"]
    __Region = _rst["Region"]
    __TimeZone = _rst["Time Zone"]

    if __Country == '':
        __Country = 'Not detected'
    COUNTRY_COUNTER[__Country] +=1
    if __Region != '':
        if __Country != "":
            REGION_COUNTER[f'{__Country} / {__Region}'] +=1
    if __City != '':
        if __Country != "":
            if __Region == "":
                CITY_COUNTER[f"{__Country} / {__City}"] +=1
            else:
                CITY_COUNTER[f"{__Country} / {__Region} / {__City}"] +=1
    if __TimeZone == '':
        __TimeZone = 'Not detected'
    TIMEZONE_COUNTER[__TimeZone] +=1    


def ParingLogFileWithFilter(line):    
        global Agent_counter
        global All_Agent_counter
        global UnknowAgentName
        Agent_counter = Counter()    
        All_Agent_counter = Counter()
        UnknowAgentName = ""

        AddThisLine = True                
        global CountLogs
        global FirstLine
        global From_Date
        global To_Date
        CountLogs += 1
        DateMatch = re.search(Date_pattern, line)                                    
        LogTime = ConvertDateinLog2RealTime(DateMatch)
        if ManualScope == '': # جلوگبری از به روزرسانی تاریخ ها اگر زمان تغییر داده شده است
            if DateMatch:
                To_Date = ConvertDateinLog2RealTime(DateMatch)
                if FirstLine: # ثبت تاریخ اولین خط
                    From_Date = ConvertDateinLog2RealTime(DateMatch)
                    FirstLine = False                                        
        else:        
            if LogTime < NEW_Date:
                AddThisLine = False
        ip_address = GetIpFromLine(line,FILTER_IP)
        if ip_address == None:
            AddThisLine = False
        
#        if GEO_IS_DISABLE is False:
#            LocationLst = GeoIpLocation.GetGeoLocationFromIP(LocationDict=MY_GEO_LOCATION,GeoDB=GEO_DB_NAME,IpAdress=ip_address,FilterOnCountry=FILTER_COUNTRY)
#            if LocationLst == None:
#                AddThisLine = False
#        else:
#            LocationLst = None

        Referer = GetRefererFromLine(line,FILTER_REFERER)        
        if Referer == '-':
            Referer = '[ EMPTY (-) ]'
        if Referer == None:
            AddThisLine = False                        

        url = GetUrlFromLine(line,FILTER_URL)
        if url == None:
            AddThisLine = False
        
        agentDict = getAgentFromLine(line,FILTER_AGENT)                
        agent = agentDict[0]
        user_agent = agentDict[1]
        All_Agent_counter[user_agent] +=1
        if agent == '':
            AddThisLine = False                
        
        if UNKNOW_AGENT_Str != '':
            UnknowAgentName = FilterByAgent(line,FILTER_UNKNOW_AGENT)
            if UnknowAgentName == None:
                AddThisLine = False
                
        StatusCode = GetCodeFromLine(line,FILTER_CODE)
        if StatusCode == None:
            AddThisLine = False
        
        if AddThisLine:
            _rtn = {}
            _rtn.update({"IP"  : ip_address,
                        "URL" : url,
                        "CODE" : StatusCode,
                        "BORWSER" : agent,
                        "ALL_AGENT" : user_agent,
                        "REFERER" : Referer,                        
                        })
            #return ip_address, url,StatusCode,agent,user_agent,Referer,LocationLst
            return _rtn
        else:
            return ''
    

def GetCodeFromLine(line,CodeFilter = []):##
    Status_Code_Pattern = re.compile(r'"GET\s(\/[^\s]*)\sHTTP/1\.\d"\s(\d{3})')    
    CodeMatch = Status_Code_Pattern.search(line)
    if CodeMatch:        
        status_code = int(CodeMatch.group(2))  # Extract the status code        
        if CodeFilter == []:
            return status_code
        else:
            for _code in CodeFilter:
                if _code == status_code:
                    return status_code
        return None        

def SearchIt(search_term,phrase,SearchMode=''):
    if SearchMode.strip() == "":
        SearchMode = GLOBAL_SEARCH_METHOD
    if SearchMode.lower().strip() == 'start':
        FindIt = re.findall(f"^{search_term}",phrase,re.IGNORECASE)
    elif SearchMode.lower().strip() == 'end':
        FindIt = re.findall(f"{search_term}$",phrase,re.IGNORECASE)
    elif SearchMode.lower().strip() == 'all':
        FindIt = re.findall(search_term,phrase,re.IGNORECASE)
    elif SearchMode.lower().strip() == 'exactly':
        if search_term.lower() == phrase.lower():
            FindIt = True
        else:
            FindIt = False

    return FindIt

def GetIpFromLine(line,IpFilter = []):
    if Proxy_or_LoadBalance:
        IP_pattern = r'"(\d+\.\d+\.\d+\.\d+)"$'
    else:
        IP_pattern = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'    
    IpMatch = re.search(IP_pattern, line)        
    if IpMatch: 
        ip_address = IpMatch.group(1)        
        if IpFilter == []:
            return ip_address
        else:
            for _Ip in IpFilter:
                #FindIp = re.findall(f"^{_Ip}",ip_address)                
                FindIp = SearchIt(_Ip,ip_address)
                if FindIp:
                    return ip_address            
        return None        

def GetRefererFromLine(line,RefererFilter = []):
    log_format = r'(?P<ip>[\d\.]+) - - \[(?P<time>[^\]]+)\] "(?P<method>[A-Z]+) (?P<url>[^ ]+) HTTP/[0-9.]+" (?P<status>\d{3}) (?P<size>\d+) "(?P<referer>[^"]*)" "(?P<user_agent>[^"]*)"'    
    match = re.match(log_format, line)
    if match:
        referer = match.group('referer')
        if RefererFilter == []:
            return referer
        else:
            for _referer in RefererFilter:
                if SearchIt(_referer,referer):
                    return referer
        return None        

def GetUrlFromLine(line,URLFilter = []):##
    url_pattern = re.compile(r'"GET\s(\/[^\s]*)')
    matchURL = url_pattern.search(line)
    if matchURL:        
        url = matchURL.group(1)  # Get the matched URL
        if URLFilter == []:
            return url
        else:
            for _UrlFilterItem in URLFilter:            
                #if _Url in line:            
                if SearchIt(_UrlFilterItem,url):
                    return url                
        return None

#def GetOsFromFromLine(Line,OsFilter = []):
#    os_regex = r"(Windows NT|Mac OS X|Linux|Android|iPhone|iPad)"

def getAgentFromLine(line,AgentFilter = []):    
    global UNKNOW_AGENT_Str    
    UNKNOW_AGENT_Str = ""
    browser_regex = r"(Chrome|Firefox|Safari|Opera|Edge|Trident)"
    user_agent = line.split('"')[-4]
    if FILTER_UNKNOW_AGENT != []:
        UNKNOW_AGENT_Str = user_agent    
        return ['unknow',user_agent]
    matchBrowser = re.search(browser_regex, user_agent)    
    if matchBrowser:
        Browser = matchBrowser.group(1)
        if AgentFilter == []:
            #All_Agent_counter[user_agent] +=1
            BrowserDict = [Browser,user_agent]
            return BrowserDict
        else:
            for _agent in AgentFilter:
                if Browser.lower() in _agent:
                    BrowserDict = [Browser,user_agent]
                    #All_Agent_counter[user_agent] +=1
                    return BrowserDict
            else:
                return ['',user_agent]

    #Unknown_Agent_counter_all[user_agent] +=1
    if AgentFilter == []:
        UNKNOW_AGENT_Str = user_agent    
        BrowserDict = ['unknow',user_agent,UNKNOW_AGENT_Str]
        return BrowserDict
    else:
        return ['',user_agent]
def FilterByAgent(line,AgentFilter):
    #if AgentFilter != []:
    #if UNKNOW_AGENT_Str != "":    
    agentName = line.split('"')[-4]            
    if AgentFilter == []:
        return agentName
    else:
        for _ in AgentFilter:
            #FindAgent = re.findall(f"^{_}",agentName)
            FindAgent = SearchIt(_,agentName)
            if FindAgent:
                return agentName        
    return None 


def printStatus():            
    RowAnalyzed = f"{_b}Row analyzed {_bb} {CountLogs} {_reset}"    
    CountIP = f"{_y}Uniq ip detected  {_by} {len(Ip_counter)} {_w}{_reset}"    
    CountAgent = f"{_g} Unknown agent detected {_blg} {len(Unknown_Agent_counter)} {_w}{_reset}"    
    CountURL = f"{_c} Uniq URL detected {_bc} {len(url_counter)} {_w}{_reset}"    
    CountRef = f"{_b} Uniq Referer detected {_bb} {len(REFERER_COUNTER)} {_w}{_reset}"    
    LastSync = f'{_B}{_b} at {_bb} {TimeofReadLogFile.strftime("%I:%M:%S %p")} {_w}{_reset}'
    TimeofLog = f'{_w}Log Found From [ {_B}{_w}{From_Date.strftime("%a %d %b %Y - %I:%M:%S %p")}{_reset}{_w} ] to [ {_B}{_w}{To_Date.strftime("%a %d %b %Y - %I:%M:%S %p" )}{_reset}{_w} ]{_reset}'    
    if GEO_IS_DISABLE is False:
        CountryStr = f"{_r}Country Detect {_br} {len(COUNTRY_COUNTER)} {_w}{_reset}"
        TimeZoneStr = f"{_m}Time Zone Detect {_bm} {len(TIMEZONE_COUNTER)} {_w}{_reset}"    
    COUNTRY_COUNTER
    
    TIMEZONE_COUNTER

#    if ManualScope == '':        
#        TimeofLog = f'{_w}Log Found From [ {_B}{_w}{From_Date.strftime("%a %d %b %Y - %I:%M:%S %p")}{_reset}{_w} ] to [ {_B}{_w}{To_Date.strftime("%a %d %b %Y - %I:%M:%S %p" )}{_reset}{_w} ]{_reset}'    
#    else:
#        TimeofLog = f'{_w}Time Range Changed for ( {_B}{_br} {ManualScope.upper()} {_reset}{_w} ) from [ {_B}{_bm}{From_Date.strftime("%a %d %b %Y - %I:%M:%S %p")}{_reset}{_w} ] to [ {_B}{_bm}{To_Date.strftime("%a %d %b %Y - %I:%M:%S %p" )}{_reset}{_w} ] {_reset}'
    if LogsMode == 'docker':
        PrintContainterStatus()        
    print ("{:<30}".format(RowAnalyzed + LastSync))
    print("")
    print("{:<30} {:<30} {:<30} {:<30}".format(CountIP,CountAgent,CountURL,CountRef))    
    print("")
    if len(Ip_counter) < 5:
            if CountLogs > 1000 :
                Proxy_text =f"""We found that IP addresses may not be recognized properly. This issue could be due to the
                "Proxy_or_LoadBalance" parameter in the "config.json" file not aligning with your network settings.
                If requests are routed through a proxy or load balancer before reaching the Nginx server,
                set the "Proxy_or_LoadBalance" parameter to "true." Otherwise, set it to "false."  
                If IP address or user location information is critical for your, 
                we recommend ensuring that the "Proxy_or_LoadBalance" parameter in the "config.json" file is configured correctly.
                """
                AsciArt.BorderIt(Text=Proxy_text,BorderColor=_y,TextColor=_w)
                print("")
    print ("{:<100}".format(TimeofLog))

    if filterStatus:        

        print("")
        print(f'{_w}--------------------------------------- Filter information [ {_b}{GLOBAL_SEARCH_METHOD_ALIAS} {_w}] ---------------------------------------{_reset}')    
        print("")
        if ManualScope != '':                    
            print(f'{_bbw} TIME {_reset}{_w} : Time Range for ( {_B}{_y} {ManualScope.upper()} {_reset}{_w} ) from [ {_B}{_y}{NEW_Date.strftime("%a %d %b %Y - %I:%M:%S %p")}{_reset}{_w} ] to [ {_B}{_y}{To_Date.strftime("%a %d %b %Y - %I:%M:%S %p" )}{_reset}{_w} ] {_reset}')                    
            print("")
        if FILTER_IP != []:            
            print(f'{_bbw} IP {_reset}{_w} : including IPs ( {_B}{_y} {FILTER_IP} {_reset} )')
            print("")
        if FILTER_URL != []:            
            print(f'{_bbw} URL {_reset}{_w} : including Urls ( {_B}{_y} {FILTER_URL} {_reset} )')            
            print("")
        if FILTER_AGENT != []:
            print(f'{_bbw} BROWSER {_reset}{_w} : including browsers ( {_B}{_y} {FILTER_AGENT} {_reset} )')            
            print("")
        if FILTER_CODE != []:
            print(f'{_bbw} STATUS CODE {_reset}{_w} : including status code ( {_B}{_y} {FILTER_CODE} {_reset} )')                        
            print("")
        if FILTER_UNKNOW_AGENT != []:
            print(f'{_bbw} UNKNOW AGENT {_reset}{_w} : including Unknow Agent ( {_B}{_y} {FILTER_UNKNOW_AGENT} {_reset} )')                                    
            print("")
        if FILTER_REFERER != []:
            print(f'{_bbw} REFERER {_reset}{_w} : including Referer ( {_B}{_y} {FILTER_REFERER} {_reset} )')                                    
            print("")
        if FILTER_COUNTRY != []:
            print(f'{_bbw} COUNTRY {_reset}{_w} : including Country ( {_B}{_y} {FILTER_COUNTRY} {_reset} )')                                    
            print("")
        print(f'{_w}--------------------------------------- Filter information [ {_b}{GLOBAL_SEARCH_METHOD_ALIAS} {_w}] ---------------------------------------{_reset}')    



def order_dict_by_value(d):
    """Orders a dictionary by its values in descending order.

    Args:
        d: The dictionary to be ordered.

    Returns:
        An OrderedDict with the same keys and values as the input dictionary,
        but ordered by value in descending order.
    """

    return OrderedDict(sorted(d.items(), key=lambda item: item[1], reverse=True))


def FnPrintIP(ListOfIP,MaxPrint = 50):
    """
    لیست آی پی ها و تعداد تکرار آن را پرینت می کتد
    
    Args: 
        ListOfIP :  received from parser
        MaxPrint :  It should not be printed smaller than what amount        
    """
    ordered_dict = order_dict_by_value(ListOfIP)
    base.clearScreen()
    Banner.ParsingLogo()
    printStatus()    
    print("")
    if filterStatus is False:
        print('-------------------------------------    Result    -------------------------------------')
        print("")
    print (_w + _B +"{:<5} {:<20} {:<10}".format("No.","IP","Count") + _reset )    
    print("")
    xI = 1
    for _ in ordered_dict :            
        if xI <= MaxPrint:
            print (_B + _w + "{:<5} {:<20} {:<10}".format(str(xI) ,_ , str(ordered_dict[_])) + _reset )
            xI += 1
        else:
            break    
    base.PrintMessage(messageString="End of List ...", MsgType="notif", AddLine = True, addSpace = 0, BackgroudMsg = False)  

def FnPrintTimeZone(ListOfTimeZone,MaxPrint = 50):
    ordered_dict = order_dict_by_value(ListOfTimeZone)
    base.clearScreen()
    Banner.ParsingLogo()
    printStatus()
    print("")
    if filterStatus is False:
        print('-------------------------------------    Result    -------------------------------------')
        print("")
    print (_w + _B +"{:<5} {:<10} {:<50}".format("No.","Count","Time Zone") + _reset )    
    print("")
    x_counter = 1
    for _TimeZone in ordered_dict:
        if x_counter <= MaxPrint:
            print (_B + _w + "{:<5} {:<10} {:<50}".format(str(x_counter),str(ordered_dict[_TimeZone]) ,_TimeZone ) + _reset )
            x_counter += 1
def FnPrintCountry(ListOfCountry,printIt,MaxPrint = 50):
    ordered_dict = order_dict_by_value(ListOfCountry)
    base.clearScreen()
    Banner.ParsingLogo()
    printStatus()
    print("")
    if filterStatus is False:
        print('-------------------------------------    Result    -------------------------------------')
        print("")

    print (_w + _B +"{:<5} {:<10} {:<50}".format("No.","Count","Location") + _reset )    
    print("")
    x_counter = 1
    for _Country in ordered_dict:
        if x_counter <= MaxPrint:
            print (_B + _w + "{:<5} {:<10} {:<50}".format(str(x_counter),str(ordered_dict[_Country]) ,_Country ) + _reset )
            if printIt :
                for _region in REGION_COUNTER:
                    if re.findall(f'^{_Country}',_region):
                        print (_w + "{:<5} {:<10} {:<50}".format(" "," " ,_region + f"( {str(REGION_COUNTER[_region])} )" ) + _reset )                    
                        for _city in CITY_COUNTER:
                            if re.findall(f'^{_region}',_city):                            
                                print (_w + "{:<5} {:<10} {:<50}".format(" "," " ,_city + f"( {str(CITY_COUNTER[_city])} )" ) + _reset )                    
            x_counter += 1
        else:
            break    

def FnPrintReferer(listOfReferer,MaxPrint = 50):
    ordered_dict = order_dict_by_value(listOfReferer)
    base.clearScreen()
    Banner.ParsingLogo()
    printStatus()
    print("")
    if filterStatus is False:
        print('-------------------------------------    Result    -------------------------------------')
        print("")
    print (_w + _B +"{:<5} {:<10} {:<100}".format("No.","Count","Referer") + _reset )    
    print("")
    xI = 1
    for _ in ordered_dict :        
        if xI <= MaxPrint:
            print (_B + _w + "{:<5} {:<10} {:<100}".format(str(xI), str(ordered_dict[_]) ,_ ) + _reset )
            xI += 1
        else:
            break    
    base.PrintMessage(messageString="End of List ...", MsgType="notif", AddLine = True, addSpace = 0, BackgroudMsg = False)  

def FnPrintAgent(ListOfAgent,MaxPrint = 50):
    ordered_dict = order_dict_by_value(ListOfAgent)
    base.clearScreen()
    Banner.ParsingLogo()
    printStatus()
    print("")
    if filterStatus is False:
        print('-------------------------------------    Result    -------------------------------------')
        print("")
    print (_w + _B +"{:<5} {:<10} {:<100}".format("No.","Count","Agent") + _reset )    
    print("")
    xI = 1
    for _ in ordered_dict :        
        if xI <= MaxPrint:
            print (_B + _w + "{:<5} {:<10} {:<100}".format(str(xI), str(ordered_dict[_]) ,_ ) + _reset )
            xI += 1
        else:
            break    
    base.PrintMessage(messageString="End of List ...", MsgType="notif", AddLine = True, addSpace = 0, BackgroudMsg = False)  

def FnPrintBrowser(ListofBrowser):   
    order_dict = order_dict_by_value(ListofBrowser)
    base.clearScreen()
    Banner.ParsingLogo()
    printStatus()
    if filterStatus is False:
        print("")
        print('-------------------------------------    Result    -------------------------------------')
        print("")

    xI = 1
    for x in order_dict:
        if xI <= 1:
            ClmnColor = _r
        elif xI <= 2:
            ClmnColor = _m
        elif xI <= 3:
            ClmnColor = _y
        elif xI <= 5:
            ClmnColor = _c
        elif xI <= 8:
            ClmnColor = _b
        xI += 1    
        print (f"{_w}{x}: {ClmnColor}{order_dict[x]}{_reset}")
    
def MainMenuIP():
    print(f"{_w}")
    print(f"type [ {_D}{_w}q{_N}{_w}     ] quit{_reset}")
    print(f"     [ {_D}{_w}enter{_N}{_w} ] for Main Menu")
    
    print("")
    UserInput = input(f"{_B}{_w}or Enter ({_y}IP{_w}) :{_reset}")
    if UserInput.strip() == "":
        base.clearScreen()
        Banner.ParsingLogo()    
        printStatus()
        MainMenu()        

def ExportMenu():
    base.clearScreen()
    Banner.ParsingLogo()    
    printStatus()    
    while True:        
        if filterStatus:
            FilterStr = f'{_y}[ {_br}{_B} ENABLE {_reset}{_y} ]'
        else:
            FilterStr = f'{_y}[ {_w}Disable {_y}]'    
        
        print(f"{_w}")
        print(f"press [ {_N}{_w}enter{_N}{_w} ] for Main Menu")
        print(f"type  [ {_N}{_w}0{_w}  ] quit{_reset}")
        print(f"      [ {_N}{_y}1{_w}  ] Export Summary as text File")
        print(f"      [ {_N}{_y}2{_w}  ] Export IP (CSV)")
        print(f"      [ {_N}{_y}3{_w}  ] Export URL (CSV)")
        print(f"      [ {_N}{_y}4{_w}  ] Export Browser (CSV)")
        print(f"      [ {_N}{_y}5{_w}  ] Export Status Code (CSV)")
        print(f"      [ {_N}{_y}6{_w}  ] Export Unknown Agent (CSV)")
        print(f"      [ {_N}{_y}7{_w}  ] Export All Agent (CSV)")
        print(f"      [ {_N}{_y}8{_w}  ] Export Country")
        print(f"      [ {_N}{_y}9{_w}  ] Export Country (Without Region & City)")        
        print(f"      [ {_N}{_y}10{_w} ] Export TimeZone (CSV)")
        print(f"      [ {_N}{_y}11{_w} ] Export Referer (CSV)")

        print("")
        UserInput = input(f"{_B}{_w}Enter Command :{_reset}")
        #for _i in ['q','','txt','i','u','b','c','ua','aa']:
        if UserInput.strip() == '':      
            return ''
        try:
            _intUserInpt = int(UserInput) 
            if _intUserInpt <= 11:
                return _intUserInpt
        except:            
            base.PrintMessage(messageString=f'Value ({UserInput}) not valid',MsgType="error", AddLine = True, addSpace = 0)        
        
def ExportMenuLuncher():
    UserInput = ExportMenu()
    if UserInput == 0:
        base.FnExit()
    elif UserInput == 1:
        ExportTextFile()
    elif UserInput == 2:
        ExportIpinCSV()
    elif UserInput == 3:
        ExportURLinCSV()
    elif UserInput == 4:
        ExportBrowserInCSV()
    elif UserInput == 5:
        ExportCodeInCSV()
    elif UserInput == 6:
        ExportUnknownAgentInCSV()
    elif UserInput == 7:
        ExportAllAgentInCSV()
    elif UserInput == 8:
        ExportCountry(Withcity=True)
    elif UserInput == 9:
        ExportCountry()
    elif UserInput == 10:
        ExportAllTimeZone()            
    elif UserInput == 11:
        ExportRefererinCSV()



def ExportCountry(Withcity=False):
    Ordered_Country = order_dict_by_value(COUNTRY_COUNTER)
    CountryList = []
    CountryList.append('Count,Country,')
    for _ in Ordered_Country:
        _x = Ordered_Country[_]
        CountryList.append(f"{_x},{_}")            
        if Withcity :
            for _region in REGION_COUNTER:
                if re.findall(f'^{_}',_region):
                    CountryList.append(f"{REGION_COUNTER[_region]},{_region}")                    
                    for _city in CITY_COUNTER:
                        if re.findall(f'^{_region}',_city):                            
                            CountryList.append(f"{CITY_COUNTER[_city]},{_city}")                                                        
    CreateFile(List4Save=CountryList,FileName='Country',Ext='csv')
        
def ExportAllTimeZone():
    Ordered_ZimeZone = order_dict_by_value(TIMEZONE_COUNTER)
    AllTimeZone = []
    AllTimeZone.append('Count,Time Zone')
    for _ in Ordered_ZimeZone:
        _x = Ordered_ZimeZone[_]
        AllTimeZone.append(f"{_x},{_}")
    CreateFile(List4Save=AllTimeZone,FileName='time-Zone',Ext='csv')
    
    

def ExportAllAgentInCSV():
    Ordered_AllAgent = order_dict_by_value(All_Agent_counter)
    AllAgentList = []
    AllAgentList.append('Count,Agent')
    for _ in Ordered_AllAgent:
        _x = Ordered_AllAgent[_]
        AllAgentList.append(f"{_x},{_}")
    CreateFile(List4Save=AllAgentList,FileName='All-Agent',Ext='csv')


def ExportUnknownAgentInCSV():
    Ordered_UnknownAgent = order_dict_by_value(Unknown_Agent_counter)
    UnknownAgentList = []
    UnknownAgentList.append('Count,Unknown Agent')
    for _ in Ordered_UnknownAgent:
        _x = Ordered_UnknownAgent[_]
        UnknownAgentList.append(f"{_x},{_}")
    CreateFile(List4Save=UnknownAgentList,FileName='Unknown_Agent',Ext='csv')

def ExportIpinCSV():
    ordered_IP = order_dict_by_value(Ip_counter)
    IPList = []
    IPList.append('IP,Count')
    for _ in ordered_IP:
        _x = ordered_IP[_]
        IPList.append(f"{_},{_x}")
    CreateFile(List4Save=IPList,FileName='IP',Ext='csv')

def ExportURLinCSV():
    ordered_url = order_dict_by_value(url_counter)
    UtlList = []
    UtlList.append('Count,URL')
    for _ in ordered_url:
        _x = ordered_url[_]
        UtlList.append(f"{_x},{_}")
    CreateFile(List4Save=UtlList,FileName='Url',Ext='csv')

def ExportRefererinCSV():
    ordered_Referer = order_dict_by_value(REFERER_COUNTER)
    RefererList = []
    RefererList.append('Count,Referer URL')
    for _ in ordered_Referer:
        _x = ordered_Referer[_]
        RefererList.append(f"{_x},{_}")
    CreateFile(List4Save=RefererList,FileName='Referer',Ext='csv')


def ExportBrowserInCSV():
    ordered_browser = order_dict_by_value(browser_counter)    
    BrowserList = []
    BrowserList.append('Browser,Count')
    for _ in ordered_browser:
        _x = ordered_browser[_]
        BrowserList.append(f"{_},{_x}")
    CreateFile(List4Save=BrowserList,FileName='Browser',Ext='csv')

def ExportCodeInCSV():
    StatusCodeList = []
    StatusCodeList.append('StatusCode,Count')
    for _status_code, _count in status_code_counter.most_common():        
        StatusCodeList.append(f"{_status_code},{_count}")
    CreateFile(List4Save=StatusCodeList,FileName='Status_Code',Ext='csv')


def ExportTextFile():
    current_date = datetime.now().strftime("%Y-%m-%d_%I:%M:%S %p")
    _RowAnalyzed = f"Row analyzed : {CountLogs}"    
    _CountIP = f"Uniq ip detected : {len(Ip_counter)}"    
    _CountAgent = f"Unknown agent detected : {len(Unknown_Agent_counter)}"
    _CountURL = f"Uniq URL detected : {len(url_counter)}"    
    _LastSync = f'{TimeofReadLogFile.strftime("%I:%M:%S %p")}'
    _TimeofLog = f'Log Found From [ {From_Date.strftime("%a %d %b %Y - %I:%M:%S %p")} ] to [{To_Date.strftime("%a %d %b %Y - %I:%M:%S %p" )}]'

    TextLst= []    
    TextLst.append(f"Nginx Parsing Logs on {current_date}")
    TextLst.append("")
    TextLst.append(_RowAnalyzed)    
    TextLst.append(_CountIP)
    TextLst.append(_CountAgent)
    TextLst.append(_CountURL)
    TextLst.append(_TimeofLog)    

    if filterStatus:
        TextLst.append("")
        TextLst.append(f'--------------------------------------   Filter information   --------------------------------------')
        if ManualScope != '':                    
            TextLst.append(f'[  TIME  ] Time Range for ( {ManualScope.upper()} ) from [ {From_Date.strftime("%a %d %b %Y - %I:%M:%S %p")} ] to [ {To_Date.strftime("%a %d %b %Y - %I:%M:%S %p" )} ] ')                    
        if FILTER_IP != '':            
            TextLst.append(f'[   IP   ] Including logs with ( {FILTER_IP} ) in IP Address')            
        if FILTER_URL != '':            
            TextLst.append(f'[   URL  ] Filter on URL is ON Including logs with ( {FILTER_URL} ) in Requset URL')            
        if FILTER_AGENT != []:
            TextLst.append(f'[   Browser   ] Filter on Browser is ON including items received from one of the browsers {FILTER_AGENT}.')        
        if FILTER_CODE != []:
            TextLst.append(f'[   Status Code   ] Filter on HTTP response status codes is ON including items received from one of the browsers {FILTER_CODE} .')            
        if FILTER_COUNTRY != []:
            TextLst.append(f'[   Country   ] Filter on Country is ON including items received from one of the Country {FILTER_CODE} .')            
        if FILTER_REFERER != []:
            TextLst.append(f'[   Referer   ] Filter on Referer is ON including items received from one of the Referer {FILTER_CODE} .')            

        TextLst.append(f'--------------------------------------   Filter information   --------------------------------------')        
        TextLst.append("")        


    ######  Add IP List

    ordered_IP = order_dict_by_value(Ip_counter)
    _counterNo = 1
    TextLst.append("")
    TextLst.append("List of IP :")
    TextLst.append("")
    TextLst.append("no /IP / Count ")    
    TextLst.append("")
    for _ in ordered_IP :
        if _counterNo <= MAX_LINE: 
            TextLst.append("{:<5} {:<20} {:<10}".format(str(_counterNo),_,str(ordered_IP[_])))	
            _counterNo += 1
        else:
            break	        

    ######  Add URL

    ordered_url = order_dict_by_value(url_counter)
    _counterNo = 1
    TextLst.append("")
    TextLst.append("URLs :")
    TextLst.append("")    
    TextLst.append("No. / Count / URL ")	
    TextLst.append("")
    for _ in ordered_url :
        if _counterNo <= MAX_LINE:         
            TextLst.append(f"{str(_counterNo)}    {str(ordered_url[_])}      {_} ")
            _counterNo += 1
        else:
            break	        

    ######  Add browser

    ordered_browser = order_dict_by_value(browser_counter)    
    TextLst.append("")
    TextLst.append("Browsers :")
    TextLst.append("")
    TextLst.append(f"Browser   /   Count")	
    TextLst.append("")
    for _ in ordered_browser :
        TextLst.append(f"{_}: {ordered_browser[_]}")

    ##### status code
    TextLst.append("")
    TextLst.append("Status Code :")
    TextLst.append("")
    for _status_code, _count in status_code_counter.most_common():        
        occurrencesMSg = "occurrences"
        if _status_code in All_NginxStatusCode:            
            occurrencesMSg = f"expands by Nginx"        
        TextLst.append(f"Code [ {_status_code} ] : {_count} {occurrencesMSg}")

    ######  Add Unknown_Agent


    ordered_Unknown_Agent = order_dict_by_value(Unknown_Agent_counter)
    _counterNo = 1
    TextLst.append("")
    TextLst.append("Unknown Agent :")
    TextLst.append("")
    TextLst.append(f'No / Count / Agent ')	
    TextLst.append("")
    for _ in ordered_Unknown_Agent :
        if _counterNo <= MAX_LINE:         
            TextLst.append(f"{str(_counterNo)}    {str(ordered_Unknown_Agent[_])}      {_} ")
            _counterNo += 1
        else:
            break	        



    ## ADD Country
    if GEO_IS_DISABLE is False:
        ordered_dict = order_dict_by_value(COUNTRY_COUNTER)
        x_counter = 1
        TextLst.append("")
        TextLst.append("List of Country :")
        TextLst.append("")
        TextLst.append(f'No / Count / Country ')	
        TextLst.append("")

        for _Country in ordered_dict:
            if x_counter <= MAX_LINE:
                TextLst.append(f"{str(x_counter)}   {str(ordered_dict[_Country])}   {_Country}")        
                for _region in REGION_COUNTER:
                    if re.findall(f'^{_Country}',_region):                    
                        TextLst.append(f"       {_region}( {str(REGION_COUNTER[_region])} ) ")        
                        for _city in CITY_COUNTER:
                            if re.findall(f'^{_region}',_city):                                                        
                                TextLst.append(f"      {_city}( {str(CITY_COUNTER[_city])} ) ")                                                                
                x_counter += 1
            else:
                break

    ## ADD Timezone
    if GEO_IS_DISABLE is False:
        ordered_dict = order_dict_by_value(TIMEZONE_COUNTER)
        x_counter = 1
        TextLst.append("")
        TextLst.append("List of Time Zone :")
        TextLst.append("")
        TextLst.append(f'No / Count / TimeZome ')	
        TextLst.append("")

        for _ in ordered_dict :
                if x_counter <= MAX_LINE:         
                    TextLst.append(f"{str(x_counter)}    {str(ordered_dict[_])}      {_} ")
                    x_counter += 1
                else:
                    break	        

    ### ADD Referer

    ordered_Referer = order_dict_by_value(REGION_COUNTER)
    _counterNo = 1
    TextLst.append("")
    TextLst.append("Referer :")
    TextLst.append("")    
    TextLst.append("No. / Count / Referer(URL) ")	
    TextLst.append("")
    for _ in ordered_url :
        if _counterNo <= MAX_LINE:         
            TextLst.append(f"{str(_counterNo)}    {str(ordered_url[_])}      {_} ")
            _counterNo += 1
        else:
            break	        




    CreateFile(List4Save=TextLst,FileName='nginx_Parsing_logs',Ext='txt')
    #### Create File
#    try:
#        with open(FilePath, 'w') as file:        
#            for _ in TextLst:
#                file.write("\n"+_)
#        print(f"File successfully created at: {FilePath}")
#    except Exception as e:
#        print(f"An error occurred: {e}")        

def CreateFile(List4Save:list,FileName:str,Ext:str):
    current_date = datetime.now().strftime("%Y-%m-%d_%I:%M:%S %p")
    file_name = f"{FileName}_{current_date}.{Ext}"
    FilePath = os.path.join(EXP_PATH,file_name)
    writeFile = False
    if base.CheckExistDir(EXP_PATH,"Export Directory") :
        try:
            with open(FilePath, 'w') as file:        
                for _ in List4Save:
                    file.write("\n"+_)
            writeFile = True                
        except:
            writeFile = False

    if writeFile:
        print("")
        print(f"{_B}{_w}File [{_g}{file_name}{_w}] successfully created on [{_g}{EXP_PATH}{_w}].{_reset}")
        print("")
        input('Press enter to continue ...')
    else:
        print("")
        print(f"{_B}{_r}Cannnot Create File, Something went wrong{_reset}")            
        print("")
        input('Press enter to continue ...')

def MainMenuAgent():
    print(f"{_w}")
    print(f"type [ {_D}{_w}q{_N}{_w}     ] quit{_reset}")
    print(f"     [ {_D}{_w}enter{_N}{_w} ] for Main Menu")
    print(f"     [ {_D}{_y}a{_N}{_w} ] for Unknow Agent")
    print("")
    UserInput = input(f"{_B}{_w}or Enter ({_y}Browser Name{_w}) :{_reset}")
    if UserInput.strip() == "":
        base.clearScreen()
        Banner.ParsingLogo()    
        printStatus()
        MainMenu()        
    
    if UserInput.lower() == 'a':
        base.clearScreen()
        Banner.ParsingLogo()
        NumberInt = GetNumberofFromUser(len(browser_counter))
        FnPrintAgent(Unknown_Agent_counter,NumberInt)


        

def MainMenu():
    global GEO_IS_DISABLE
    while True:        
        base.clearScreen()
        Banner.ParsingLogo()    
        printStatus()

        if filterStatus:
            FilterStr = f'{_y}[ {_br}{_B} ON {_reset}{_y} ]'
        else:
            FilterStr = f'{_y}[ {_w}OFF{_y} ]'    
        print(f"{_w}")                
        print(f"type [ {_D}{_w}0{_N}{_w}  ] quit{_reset}")        
        print(f"     [ {_c}1{_w}  ] {_c}list of IP{_reset}")
        print(f"     [ {_c}2{_w}  ] {_c}list of url{_reset}")
        print(f"     [ {_c}3{_w}  ] {_c}list of Browser{_reset}")
        print(f"     [ {_c}4{_w}  ] {_c}list of Status Code{_reset}")
        print(f"     [ {_c}5{_w}  ] {_c}list of Unknown Agent{_reset}")        
        print(f"     [ {_c}6{_w}  ] {_c}list of Referer{_reset}")        
        print(f"     [ {_c}7{_w}  ] {_c}list of Country{_reset}")
        print(f"     [ {_c}8{_w}  ] {_c}list of Timezone{_reset}")
        print(f"     [ {_y}9{_w}  ] {_y}Filter/s - {FilterStr}{_reset}")        
        print(f"     [ {_r}10{_w} ] {_r}Reload Log file{_reset}")
        print(f"     [ {_b}11{_w} ] {_b}Export to File{_reset}")
        if len(Ip_counter) < 5:
                if CountLogs > 1000 :
                    print(f"     [ {_c}proxy{_w} ] {_c}For Change {_y}Proxy config{_c} temporary {_reset}")
        print("")
        UserInput = input(f"     {_B}{_w}Enter [ {_b}1 ~ 11{_w} ] or press {_b}Enter{_w} for reload :{_reset}")

        if UserInput.strip().lower() == 'proxy':
            return UserInput.strip().lower()
        
        if UserInput.strip() == "":
            UserInput = '1'
        try:
            _intUserInpt = int(UserInput) 
            if _intUserInpt <= 11:
                return _intUserInpt
        except:            
            base.PrintMessage(messageString=f'Value ({UserInput}) not valid',MsgType="error", AddLine = True, addSpace = 0)
        
    
def PrimaryMainMenuLuncher():
    global Proxy_or_LoadBalance
    UserInput = MainMenu()
    if UserInput == 0:
        base.FnExit()
    elif UserInput == 1:
        NumberInt = GetNumberofFromUser(len(Ip_counter))        
        FnPrintIP(Ip_counter,NumberInt)
        input("Press Enter to continiue ...")
    elif UserInput == 2:
        NumberInt = GetNumberofFromUser(len(url_counter))
        PrintURL(url_counter,NumberInt)
        input("Press Enter to continiue ...")
    elif UserInput == 3:
        FnPrintBrowser(browser_counter)
        input("Press Enter to continiue ...")
    elif UserInput == 4:
        printStatusCode()
        input("Press Enter to continiue ...")
    elif UserInput == 5:
        NumberInt = GetNumberofFromUser(len(Unknown_Agent_counter))
        FnPrintAgent(Unknown_Agent_counter,NumberInt)
        input("Press Enter to continiue ...")
    elif UserInput == 6:
        NumberInt = GetNumberofFromUser(len(Unknown_Agent_counter))
        FnPrintReferer(REFERER_COUNTER,NumberInt)
        input("Press Enter to continiue ...")
    elif UserInput == 7:
        NumberInt = GetNumberofFromUser(len(Ip_counter))        
        PrintIt = PrinCityandRegion()
        FnPrintCountry(COUNTRY_COUNTER,MaxPrint=NumberInt,printIt=PrintIt)    
        input("Press Enter to continiue ...")
    elif UserInput == 8:
        NumberInt = GetNumberofFromUser(len(Ip_counter))        
        FnPrintTimeZone(TIMEZONE_COUNTER,MaxPrint=NumberInt)
        input("Press Enter to continiue ...")
    elif UserInput == 9:
        FilterMenuLuncher(FilterMenu())
    elif UserInput == 10:    
        if LogsMode == 'docker':
            dockerCheck()        
        LoadLogFile(ReloadLog=True)
        #LoadVaraiableFromLogs(logs_df)    
    elif UserInput == 11:
        ExportMenuLuncher()
    elif UserInput == 'proxy':
        if len(Ip_counter) < 5:
                if CountLogs > 1000 :        
                    if Proxy_or_LoadBalance:
                        Proxy_or_LoadBalance = False
                    else:
                        Proxy_or_LoadBalance = True            
                    LoadLogFile()
    base.clearScreen()    
    PrimaryMainMenuLuncher()

def FilterMenu():
    global ManualScope    
    global FILTER_IP
    base.clearScreen()
    Banner.ParsingLogo()    
    while True:
        if AllFilterStatus():
            print("")
            print(f'{_B}{_bm }  [  Filter is Enabled  ]  {_reset}')            
        else:    
            print(f'{_w}All Filter is OFF{_reset}')                    
        print("")
        print(f'{_w}Search Method : {_by} {GLOBAL_SEARCH_METHOD_ALIAS.upper()} {_reset}{_w} : {_y}{SEARCHDISCRIPTION}{_reset}')                
        print(f"{_w}The search method affects {_b}IP{_w}, {_b}URL{_w}, and {_b}agent{_w} filters.")


        if ManualScope == '':
            StrTimeRange = f' is {_w}OFF{_reset}' 
        else:
            StrTimeRange = f' is {_bb} ON {_reset}{_w} : {_y}{ManualScope}'         
        
        if FILTER_IP == []:
            StrIP = f' is {_w}OFF{_reset}' 
        else:            
            StrIP = f' is {_bb} ON {_reset}{_w} : {_y}{FILTER_IP}' 
            
        if FILTER_URL == []:
            StrURL = f' is {_w}OFF{_reset}' 
        else:
            StrURL = f' is {_bb} ON {_reset}{_w} : {_y}{FILTER_URL}' 
        
        if FILTER_AGENT == []:
            BrwsStr = f' is {_w}OFF{_reset}'
        else:
            BrwsStr = f' is {_bb} ON {_reset}{_w} : {_y}{FILTER_AGENT}' 
                
        if FILTER_CODE == []:
            CodeStr = f' is {_w}OFF{_reset}'
        else:
            CodeStr = f' is {_bb} ON {_reset}{_w} : {_y}{FILTER_CODE}'
        
        if FILTER_UNKNOW_AGENT == []:
            UnknowStr = f' is {_w}OFF{_reset}'
        else:
            UnknowStr = f' is {_bb} ON {_reset}{_w} : {_y}{FILTER_UNKNOW_AGENT}'

        if FILTER_COUNTRY == []:
            COUNTRYStr = f' is {_w}OFF{_reset}'
        else:
            COUNTRYStr = f' is {_bb} ON {_reset}{_w} : {_y}{FILTER_COUNTRY}'

        if FILTER_REFERER == []:
            StrReferer = f' is {_w}OFF{_reset}'
        else:
            StrReferer = f' is {_bb} ON {_reset}{_w} : {_y}{FILTER_REFERER}'

        
        print(f"{_w}")
        print(f"press [ {_D}{_w}Enter{_N}{_w} ] for back to main menu{_reset}")            
        print(f"type  [ {_D}{_w}0{_N}{_w}  ] quit{_reset}")                        
        print(f"      [ {_b}1{_w}  ] {_b} Filter on IP{StrIP}{_reset}")
        print(f"      [ {_b}2{_w}  ] {_b} Filter on url{StrURL}{_reset}")
        print(f"      [ {_b}3{_w}  ] {_b} Filter on Browser{BrwsStr}{_reset}")
        print(f"      [ {_b}4{_w}  ] {_b} Filter on Status Code{CodeStr}{_reset}")
        print(f"      [ {_b}5{_w}  ] {_b} Filter on Unknow Agent{UnknowStr}{_reset}")        
        print(f"      [ {_b}6{_w}  ] {_b} Filter on Country{COUNTRYStr} {_reset}")                
        print(f"      [ {_b}7{_w}  ] {_b} Filter on Time range{StrTimeRange} {_reset}")        
        print(f"      [ {_b}8{_w}  ] {_b} Filter on Referer{StrReferer} {_reset}")        
        print(f"      [ {_r}9{_w}  ] {_r} All Filter Set OFF{_reset}")        
        print(f"      [ {_c}10{_w} ] {_c} Change search Method {_reset}")        
        print("")
        UserInput = input(f"{_B}{_w}Enter Command :{_reset}")
        
        if UserInput.strip() == '':      
            return ''
        try:            
            _intUserInpt = int(UserInput) 
            if _intUserInpt <= 10:
                return _intUserInpt
        except:            
            base.PrintMessage(messageString=f'Value ({UserInput}) not valid',MsgType="error", AddLine = True, addSpace = 0)        

        
        
        #for _i in ['q','i','u','b','c','a','t','off','']:
        #    if _i == UserInput.strip().lower():
        #        return _i.lower()
        
def FilterMenuLuncher(UserInput):        
    global ManualScope
    global FILTER_IP
    global FILTER_URL
    global FILTER_CODE
    global FILTER_UNKNOW_AGENT
    global filterStatus
    global Code_1xx
    global Code_2xx 
    global Code_3xx 
    global Code_4xx 
    global Code_5xx 
    global Code_4xx_nginx
    if UserInput == 0:
        base.FnExit()
    elif UserInput == 1: ############## FILTER IP
        IpFilterMenuLuncher()
#        if IP_Filter == 'off':
#            FILTER_IP = []
#        elif IP_Filter != []:
#            FILTER_IP = IP_Filter
        base.clearScreen()
        Banner.ParsingLogo()
        FilterMenuLuncher(FilterMenu())                
    elif UserInput == 2: ############## FILTER URL
        UrlFilterMenuLuncher()
        base.clearScreen()
        Banner.ParsingLogo()
        FilterMenuLuncher(FilterMenu())    
    elif UserInput == 3: ############## FILTER BRWOSER
        BrowserFilterMenuLuncher(BrowserFilterMenu())
    elif UserInput == 4: ############## FILTER CODE
        Code_Filter = StatusCodeFilterMenu()
        if Code_Filter == 'off':
            FILTER_CODE = []
            Code_1xx = []
            Code_2xx = []
            Code_3xx = []
            Code_4xx = []
            Code_5xx = []
            Code_4xx_nginx = []
        base.clearScreen()
        Banner.ParsingLogo()
        FilterMenuLuncher(FilterMenu())                
    elif UserInput == 5: ############## FILTER UnKnow AGENT
        UnknowAgentMenuFilterLuncher()                
        base.clearScreen()
        Banner.ParsingLogo()
        FilterMenuLuncher(FilterMenu())    

    elif UserInput == 6: ############## FILTER_COUNTRY
        CountryMenuLuncher()
        base.clearScreen()
        Banner.ParsingLogo()
        FilterMenuLuncher(FilterMenu())                
    elif UserInput == 7: ############## FILTER TIME
        base.clearScreen()
        Banner.ParsingLogo()
        global NEW_Date
        userInputTime = ChangeScopeMainMenu()        
        if userInputTime == 'off':
            ManualScope = ''
            AllFilterStatus()
        elif userInputTime != '':            
            ManualScope = userInputTime
            NEW_Date = FnGetNewDateRange(To_Date,ManualScope)                
        base.clearScreen()
        Banner.ParsingLogo()        
        FilterMenuLuncher(FilterMenu())
    elif UserInput == 8: ############## FILTER IS Referer
        RefererFilterMenuLuncher()
        base.clearScreen()
        Banner.ParsingLogo()                
        FilterMenuLuncher(FilterMenu())
    elif UserInput == 9: ############## FILTER IS OFFFFFFF
        base.clearScreen()
        Banner.ParsingLogo()
        filterStatus = False
        AllFilterStatus(AllFilterOff=True)
        FilterMenuLuncher(FilterMenu())
    elif UserInput == 10: ############## Change Search Method
        ChangeSearchModeLuncher(GLOBAL_SEARCH_METHOD)
        base.clearScreen()
        Banner.ParsingLogo()
        FilterMenuLuncher(FilterMenu())    

    elif UserInput == '': # Back to main Menu
        base.clearScreen()
        Banner.ParsingLogo()    
        if filterStatus:
            LoadLogFile()    
        printStatus()
        PrimaryMainMenuLuncher()        
def StatusCodeFilterMenu():
    global FILTER_CODE
    while True:
        base.clearScreen()
        Banner.ParsingLogo()    
        if FILTER_CODE != []:
            print("")
            print(f"{_B}{_w}Filter for code/s [ {_y}{FILTER_CODE}{_w} ] is Enabled{_reset}")            
        print(f"{_w}")
        print(f"type [ {_D}{_w}q{_N}{_w}     ] quit{_reset}")        
        print(f"     [ {_D}{_w}Enter{_N}{_w} ] for back to Filter Menu{_reset}")            
        print(f"     [ {_D}{_w}off{_N}{_w}   ] All Filter OFF{_reset}")        
        print(f"     [ {_b}1x{_w}    ] {_b} For all {_y}Information responses{_b} codes{_reset}")
        print(f"     [ {_b}2x{_w}    ] {_b} For all {_y}Successful responses{_b} codes{_reset}")
        print(f"     [ {_b}3x{_w}    ] {_b} For all {_y}Redirection responses{_b} codes{_reset}")        
        print(f"     [ {_b}4x{_w}    ] {_b} For all {_y}Client error responses{_b} codes{_reset}")
        print(f"     [ {_b}5x{_w}    ] {_b} For all {_y}Server error responses{_b} codes{_reset}")
        print(f"     [ {_b}nginx{_w} ] {_b} For all {_y}Expands Codes by Nginx{_reset}")
        
        print("")
        UserInput = input(f"{_B}{_w}or type Status Code :{_reset}")
        _rstCode = StatusCodeUpdater(UserInput.strip().lower())
        if _rstCode == None:
            print(f"{_reset}")
            base.PrintMessage(messageString="Code Not Found ", MsgType="error", AddLine = True, addSpace = 3)  
            input('Press Enter ....')
        elif _rstCode == 'off':
            return _rstCode
        elif _rstCode == '':
            return _rstCode
            

def StatusCodeUpdater(UserInput):
    global Code_1xx
    global Code_2xx 
    global Code_3xx 
    global Code_4xx 
    global Code_5xx 
    global Code_4xx_nginx
    global FILTER_CODE
    
    if UserInput == '':
        return ''
    elif UserInput == 'off':
        return 'off'

    if UserInput == '1x':
        Code_1xx = All_StatusCode_1x
    elif UserInput == '2x':
        Code_2xx = All_StatusCode_2x
    elif UserInput == '3x':
        Code_3xx = All_StatusCode_3x
    elif UserInput == '4x':
        Code_4xx = All_StatusCode_4x
    elif UserInput == '5x':
        Code_5xx = All_StatusCode_5x
    elif UserInput == 'nginx':
        Code_4xx_nginx = All_NginxStatusCode
    else:
        try:
            intUserinput = int(UserInput)            
        except:
            return None    
                        
        if intUserinput in All_StatusCode_1x:
            if intUserinput in Code_1xx:
                Code_1xx.remove(int(UserInput))
            else:
                Code_1xx.append(int(UserInput))            
        elif intUserinput in All_StatusCode_2x:
            if intUserinput in Code_2xx:
                Code_2xx.remove(int(UserInput))
            else:
                Code_2xx.append(int(UserInput))                                
        elif intUserinput in All_StatusCode_3x:
            if intUserinput in Code_3xx:
                Code_3xx.remove(int(UserInput))
            else:
                Code_3xx.append(int(UserInput))                                            
        elif intUserinput in All_StatusCode_4x:
            if intUserinput in Code_4xx:
                Code_4xx.remove(int(UserInput))
            else:
                Code_4xx.append(int(UserInput))                                            
        elif intUserinput in All_StatusCode_5x:
            if intUserinput in Code_5xx:
                Code_5xx.remove(int(UserInput))
            else:
                Code_5xx.append(int(UserInput))
        elif intUserinput in All_NginxStatusCode:
            if intUserinput in Code_4xx_nginx:
                Code_4xx_nginx.remove(int(UserInput))
            else:
                Code_4xx_nginx.append(int(UserInput))                                                        
        else:
            return None    

    FILTER_CODE = []
    if Code_1xx != []:
        FILTER_CODE = Code_1xx

    if Code_2xx != []:
        FILTER_CODE  = FILTER_CODE + Code_2xx

    if Code_3xx != []:
        FILTER_CODE  = FILTER_CODE + Code_3xx
        
    if Code_4xx != []:
        FILTER_CODE  = FILTER_CODE + Code_4xx

    if Code_5xx != []:
        FILTER_CODE  = FILTER_CODE + Code_5xx

    if Code_4xx_nginx != []:
        FILTER_CODE  = FILTER_CODE + Code_4xx_nginx        
    
    return FILTER_CODE
        
        
        


        
def BrowserFilterMenu():
    base.clearScreen()
    Banner.ParsingLogo()    
    while True:
        Chrome_Active = ''
        Firefox_Active = ''
        Safari_Active = ''
        Opera_Active = ''
        Edge_Active = ''
        Trident_Active = ''
        
        for x in FILTER_AGENT:
            if x.lower() == 'chrome':
                Chrome_Active = f' - {_bbw} ON {_reset}'
            elif x.lower() == 'firefox':
                Firefox_Active = f' - {_bbw} ON {_reset}'
            elif x.lower() == 'safari':
                Safari_Active = f' - {_bbw} ON {_reset}'
            elif x.lower() == 'opera':
                Opera_Active = f' - {_bbw} ON {_reset}'
            elif x.lower() == 'edge':
                Edge_Active = f' - {_bbw} ON {_reset}'
            elif x.lower() == 'trident':
                Trident_Active = f' - {_bbw} ON {_reset}'

                
        print(f"{_w}")
        print(f"type [ {_D}{_w}q{_N}{_w}     ] quit{_reset}")        
        print(f"     [ {_D}{_w}Enter{_N}{_w} ] for back to Filter Menu{_reset}")            
        print(f"     [ {_D}{_w}off{_N}{_w}   ] All Filter OFF{_reset}")        
        print(f"     [ {_b}Chrome{_w}  ] {_b} To add Chrome browser{Chrome_Active}{_reset}")
        print(f"     [ {_b}Firefox{_w} ] {_b} To add Firefox browser{Firefox_Active}{_reset}")
        print(f"     [ {_b}Safari{_w}  ] {_b} To add Safari browser{Safari_Active}{_reset}")
        print(f"     [ {_b}Opera{_w}   ] {_b} To add Opera browser{Opera_Active}{_reset}")
        print(f"     [ {_b}Edge{_w}    ] {_b} To add Edge browser{Edge_Active}{_reset}")
        print(f"     [ {_b}Trident{_w} ] {_b} To add Trident browser{Trident_Active}{_reset}")     
        print("")
        UserInput = input(f"{_B}{_w}Enter Browser name or code :{_reset}")
        for _i in ['q','chrome','firefox','safari','opera','edge','trident','off','']:
            if _i == UserInput.strip().lower():
                return _i.lower()
    
def BrowserFilterMenuLuncher(UserInput):        
    global FILTER_AGENT    
    #TempFilterList = list(FILTER_AGENT)
    if UserInput == 'q':
        base.FnExit()
    elif UserInput == 'off':
        FILTER_AGENT = []
        base.clearScreen()
        Banner.ParsingLogo()    
        FilterMenuLuncher(FilterMenu())
    elif UserInput == '':
        base.clearScreen()
        Banner.ParsingLogo()    
        FilterMenuLuncher(FilterMenu())
    else:
        removeItem = False
        for x in FILTER_AGENT:            
            if x.lower() == UserInput.strip().lower():
                removeItem = True
                break
        if removeItem:
            FILTER_AGENT.remove(x)
        else:    
            FILTER_AGENT.append(UserInput)    
        #FILTER_AGENT = tuple(TempFilterList)
        BrowserFilterMenuLuncher(BrowserFilterMenu())    
        
def FnGetNewDateRange(Date,range):        
    _range = int(range[:-1])
    if range[-1].lower() == 'm':
        NewDate = Date - timedelta(minutes=_range)
    elif range[-1].lower() == 'h':
        NewDate = Date - timedelta(hours=_range)
    elif range[-1].lower() == 'd':
        NewDate = Date - timedelta(days=_range)
    elif range[-1].lower() == 's':
        NewDate = Date - timedelta(seconds=_range)
    elif range[-1].lower() == 'w':
        NewDate = Date - timedelta(weeks=_range)
        
    return NewDate
        
    
def GetNumberofFromUser(MaxNumber: int):
    UserNumberInput = input(f"{_B}{_w}Maximum number of lines default [{_b}{MAX_LINE}{_w}] : ")
    if UserNumberInput.strip() == '':
        IntInput = MAX_LINE
    else:    
        try:
            IntInput = int(UserNumberInput)            
        except:            
            base.PrintMessage(messageString="The entered value must be a logical number between", MsgType="error", AddLine = True, addSpace = 0, BackgroudMsg = False)  
            base.FnExit()
        if IntInput == 0:
            IntInput = MAX_LINE
        elif IntInput > MaxNumber:
            IntInput = MaxNumber
    return IntInput

def PrinCityandRegion():    
    userInput = input(f'{_B}{_w}To view the names of cities and states of each country, enter {_g}yes{_w} or any other key to not display it :')
    if userInput.lower().strip() == 'yes':
        return True
    else:
        return False
        

def PrintURL(url_couter,MaxPrint):
    #print(len(url_couter))
    base.clearScreen()
    Banner.ParsingLogo()
    printStatus()
    if filterStatus is False:
        print("")
        print('-------------------------------------    Result    -------------------------------------')        
        print("")
    print (_w + _B +"{:<5} {:<10} {:<150}".format("No.","Count","URL") + _reset )    
    print("")
    xI = 1
    for url, count in url_counter.most_common() :        
        if xI <= 5:
            ClmnColor = _r
        elif xI <= 10:
            ClmnColor = _y
        elif xI <= 15:
            ClmnColor = _g
        elif xI <= 20:
            ClmnColor = _b
        elif xI <= 25:
            ClmnColor = _c            
        else:
            ClmnColor = _w            
        if xI <= MaxPrint:            
            print (_B + _w + "{:<5} {:<10} {:<150}".format(str(xI), ClmnColor + str(count), url ) + _reset )
            xI += 1
        else:
            break    
    base.PrintMessage(messageString="End of List ...", MsgType="notif", AddLine = True, addSpace = 0, BackgroudMsg = False)  
    
def printStatusCode():
    base.clearScreen()
    Banner.ParsingLogo()    
    printStatus()
    if filterStatus is False:
        print("")
        print('-------------------------------------    Result    -------------------------------------')
        print("")
    
    for status_code, count in status_code_counter.most_common():
        CodeColor = _w
        occurrencesMSg = "occurrences"
        if status_code in All_StatusCode_1x:
            CodeColor = _m
        elif status_code in All_StatusCode_2x:
            CodeColor = _g
        elif status_code in All_StatusCode_3x:
            CodeColor = _y
        elif status_code in All_StatusCode_4x:
            CodeColor = _r
        elif status_code in All_StatusCode_5x:
            CodeColor = _c
        elif status_code in All_NginxStatusCode:
            CodeColor = _r
            occurrencesMSg = f"expands by Nginx"
        
        print(f"{_w}Status Code [ {CodeColor}{status_code}{_reset}{_w} ] : {_b}{count}{_w} {occurrencesMSg}")
    
def ConvertDateinLog2RealTime(DateMatch):
    """
    Convert month abbreviation to number
    #Req
    DateMatch = Data and time extracted from log
    # Return
    DataAndTime
    """
    L_day, L_month, L_year, L_hour, L_minute, L_second = DateMatch.groups()
    months = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
            'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}
    L_month = months[L_month]
    log_date = datetime(int(L_year), L_month, int(L_day), int(L_hour), int(L_minute), int(L_second))
    return log_date

def RefererFilterMenu():
    base.clearScreen()
    Banner.ParsingLogo()    
    if FILTER_REFERER != []:
        print("")
        print(f"{_B}{_w}Filter for Referer is Enabled{_reset}")            
        print(f"{_B}{_w}List of Referer:{_reset}")            
        for _ in FILTER_REFERER:
            print(f"{_B}{_w}            [ {_bm}{_}{_reset}{_w} ]{_reset}")            
        
        print(f"{_B}{_g}To remove a Referer from the filter list, re-warp it. {_reset}")                        
        print("")

    print(f"{_w}type  [ {_N}{_w}q{_reset}{_w}     ] for quit{_reset}")        
    print(f"{_w}      [ {_N}{_w}enter{_reset}{_w} ] for back{_reset}")                    
    print(f"{_w}      [ {_N}{_w}off{_reset}{_w} ] To disable the filter on URL {_reset}")                    
    UserInput = input(f'{_B}{_w}Enter Referer or part of it: ')
    return UserInput.strip().lower()


def RefererFilterMenuLuncher():
    global FILTER_REFERER
    while True:
        RefererInput = RefererFilterMenu()
        if RefererInput == 'q':
            base.FnExit()
        elif RefererInput == 'off':
            FILTER_REFERER = []
        elif RefererInput == '':            
            break        
        removeItem = False
        if FILTER_REFERER != []:
            for x in FILTER_REFERER:
                if x.lower() == RefererInput:
                    removeItem = True
                    break
        if removeItem:
            FILTER_REFERER.remove(x)
        else:
            if RefererInput != 'off':
                FILTER_REFERER.append(RefererInput)



def UrlFilterMenu():
    base.clearScreen()
    Banner.ParsingLogo()    
    if FILTER_URL != []:
        print("")
        print(f"{_B}{_w}Filter for URLs is Enabled{_reset}")            
        print(f"{_B}{_w}List of URLs:{_reset}")            
        for _ in FILTER_URL:
            print(f"{_B}{_w}            [ {_bm}{_}{_reset}{_w} ]{_reset}")            
        
        print(f"{_B}{_g}To remove a URL from the filter list, re-warp it. {_reset}")                        
        print("")

    print(f"{_w}type  [ {_N}{_w}q{_reset}{_w}     ] for quit{_reset}")        
    print(f"{_w}      [ {_N}{_w}enter{_reset}{_w} ] for back{_reset}")                    
    print(f"{_w}      [ {_N}{_w}off{_reset}{_w} ] To disable the filter on URL {_reset}")                    
    UserInput = input(f'{_B}{_w}Enter URL or part of it: ')
    return UserInput.strip().lower()


def UrlFilterMenuLuncher():
    global FILTER_URL
    while True:
        UrlInput = UrlFilterMenu()
        if UrlInput == 'q':
            base.FnExit()
        elif UrlInput == 'off':
            FILTER_URL = []
        elif UrlInput == '':            
            break        
        removeItem = False
        if FILTER_URL != []:
            for x in FILTER_URL:            
                if x.lower() == UrlInput:
                    removeItem = True
                    break
        if removeItem:
            FILTER_URL.remove(x)
        else:
            if UrlInput != 'off':
                FILTER_URL.append(UrlInput)    



def UnknowAgentMenuFilter():
    base.clearScreen()
    Banner.ParsingLogo()    
    if FILTER_UNKNOW_AGENT != []:
        print("")
        print(f"{_B}{_w}Filter for Unknow agent is Enabled{_reset}")            
        print(f"{_B}{_w}List of Agent:{_reset}")            
        for _ in FILTER_UNKNOW_AGENT:
            print(f"{_B}{_w}            [ {_bm}{_}{_reset}{_w} ]{_reset}")            
        
        print(f"{_B}{_g}To remove an Agent from the filter list, re-warp it. {_reset}")                        
        print("")

    print(f"{_w}Press [ {_N}{_w}enter{_reset}{_w} ] for back{_reset}")                    
    print(f"{_w}type  [ {_N}{_w}q{_reset}{_w}     ] for quit{_reset}")            
    print(f"{_w}      [ {_N}{_w}off{_reset}{_w} ] To disable the filter on Unknow Agent {_reset}")                    
    UserInput = input(f'{_B}{_w}Enter Unknow Agent or part of it: ')
    return UserInput.strip().lower()


def UnknowAgentMenuFilterLuncher():
    global FILTER_UNKNOW_AGENT
    while True:
        AgentInput = UnknowAgentMenuFilter()
        if AgentInput == 'q':
            base.FnExit()
        elif AgentInput == 'off':
            FILTER_UNKNOW_AGENT = []
        elif AgentInput == '':            
            break        
        removeItem = False
        if FILTER_UNKNOW_AGENT != []:
            for x in FILTER_UNKNOW_AGENT:            
                if x.lower() == AgentInput:
                    removeItem = True
                    break
        if removeItem:
            FILTER_UNKNOW_AGENT.remove(x)
        else:
            if AgentInput != 'off':
                FILTER_UNKNOW_AGENT.append(AgentInput)    

def CountryFilterMenu():
    base.clearScreen()
    Banner.ParsingLogo()    
    if FILTER_COUNTRY != []:
        print("")
        print(f"{_B}{_w}Filter for Country is Enabled{_reset}")            
        print(f"{_B}{_w}List of Country:{_reset}")            
        for _ in FILTER_COUNTRY:
            print(f"{_B}{_w}            [ {_bm}{_}{_reset}{_w} ]{_reset}")            
        
        print(f"{_B}{_g}To remove an Country from the filter list, re-warp it. {_reset}")                        
        print("")

    print(f"{_w}Press [ {_N}{_w}enter{_reset}{_w} ] for back{_reset}")                    
    print(f"{_w}Type  [ {_N}{_w}q{_reset}{_w}     ] for quit{_reset}")            
    print(f"{_w}      [ {_N}{_w}off{_reset}{_w} ] To disable the filter on Country {_reset}")                    
    print("")
    UserInput = input(f'{_B}{_w}Enter Country Name or a part of it (starts with it) : ')
    return UserInput.strip().lower()


def CountryMenuLuncher():
    global FILTER_COUNTRY
    while True:
        CountryInput = CountryFilterMenu()
        if CountryInput == 'q':
            base.FnExit()
        elif CountryInput == 'off':
            FILTER_COUNTRY = []
        elif CountryInput == '':            
            break        
        removeItem = False
        if FILTER_COUNTRY != []:
            for x in FILTER_COUNTRY:            
                if x.lower() == CountryInput:
                    removeItem = True
                    break
        if removeItem:
            FILTER_COUNTRY.remove(x)
        else:
            if CountryInput != 'off':
                FILTER_COUNTRY.append(CountryInput)    
        #FILTER_AGENT = tuple(TempFilterList)







def IpFilterMenu():    
    base.clearScreen()
    Banner.ParsingLogo()    
    if FILTER_IP != []:
        print("")
        print(f"{_B}{_w}Filter for IPs is Enabled{_reset}")            
        print(f"{_B}{_w}List of Ips:{_reset}")            
        for _ in FILTER_IP:
            print(f"{_B}{_w}            [ {_bm}{_}{_reset}{_w} ]{_reset}")            
        
        print(f"{_B}{_g}To remove an IP from the filter list, re-warp it. {_reset}")                        
        print("")
    print(f"{_w}Press [ {_N}{_w}enter{_reset}{_w} ] for back{_reset}")                    
    print(f"{_w}Type  [ {_N}{_w}q{_reset}{_w}     ] for quit{_reset}")            
    print(f"{_w}      [ {_N}{_w}off{_reset}{_w} ] To disable the filter on IP Address {_reset}")                    
    print(f"{_w}eg.   [ {_y}192.168.100.10{_w} ]{_b} To filter a specific IP Address{_reset}")    
    print(f"{_w}      [ {_y}192.168{_w} ]{_b} To filter a range of IP Address{_reset}")
    print("")
    UserInput = input(f'{_B}{_w}Enter IP or a part of it (starts with it) : ')
    return UserInput.strip().lower()
    


def IpFilterMenuLuncher():
    global FILTER_IP     
    while True:
        IpInput = IpFilterMenu()
        if IpInput == 'q':
            base.FnExit()
        elif IpInput == 'off':
            FILTER_IP = []
        elif IpInput == '':            
            break        
        removeItem = False
        if FILTER_IP != []:
            for x in FILTER_IP:            
                if x.lower() == IpInput:
                    removeItem = True
                    break
        if removeItem:
            FILTER_IP.remove(x)
        else:
            if IpInput != 'off':
                FILTER_IP.append(IpInput)    
        #FILTER_AGENT = tuple(TempFilterList)

        
    
def AllFilterStatus(AllFilterOff = False):
    global filterStatus
    global FILTER_IP 
    global FILTER_URL
    global FILTER_AGENT
    global FILTER_CODE
    global FILTER_UNKNOW_AGENT
    global FILTER_COUNTRY
    global FILTER_REFERER
    global ManualScope
    
    global Code_1xx
    global Code_2xx 
    global Code_3xx 
    global Code_4xx 
    global Code_5xx 
    global Code_4xx_nginx
    

    if AllFilterOff:
        FILTER_IP = []
        FILTER_URL = []
        FILTER_AGENT = []
        FILTER_CODE = []
        #
        Code_1xx = []
        Code_2xx = []
        Code_3xx = []
        Code_4xx = []
        Code_5xx = []
        Code_4xx_nginx = []
        #

        FILTER_COUNTRY = []
        ManualScope = ''
        FILTER_UNKNOW_AGENT = []       
        FILTER_REFERER = []
    _filterStatus = False
    if ManualScope != '':
        _filterStatus = True
    if FILTER_IP != []:
        _filterStatus = True
    if FILTER_URL != []:
        _filterStatus = True
    if FILTER_AGENT != []:
        _filterStatus = True
    if FILTER_CODE != []:
        _filterStatus = True
    if FILTER_UNKNOW_AGENT != []:
        _filterStatus = True
    if FILTER_COUNTRY != []:
        _filterStatus = True
    if FILTER_REFERER != []:
        _filterStatus = True
    filterStatus = _filterStatus    
    return _filterStatus

##

def ChangeScopeMainMenu():    
    global ManualScope
    print(f"{_w}press [ {_N}{_w}q{_reset}{_w}     ] for quit{_reset}")        
    print(f"{_w}      [ {_N}{_w}enter{_reset}{_w} ] for back{_reset}")        
    print(f"{_w}eg.   [ {_y}40s{_w} ]{_b} for 40 seconds past{_reset}")    
    print(f"{_w}      [ {_y}20m{_w} ]{_b} for 20 minutes past{_reset}")
    print(f"{_w}      [ {_y}5h{_w}  ]{_b} for 4 hours past{_reset}")
    print(f"{_w}      [ {_y}7d{_w}  ]{_b} for 7 days past{_reset}")
    print(f"{_w}      [ {_y}2w{_w}  ]{_b} for 2 weeks past{_reset}")    
    print(f"{_w}      [ {_c}c{_w}   ]{_c} for custom Time{_reset}")
    print("")
    print(f"{_B}{_w}The entered time will be calculated from the last recorded log.{_reset}")
    while True:
        #print(f"{_B}{_w}    or Enter time as This Format ({_b}YYYY-MM-DD HH:MM:SS{_w}) for get Current Time {_reset}")
        userInput = input(f"{_B}{_w}Command :").strip()        
        if userInput:
            if AnylyseUserInput(userInput):
                break
            else:
                print(f"{_r}Input cannot Not be Valid. Please enter a Valid Value.{_reset}")    
        else:
            break
    try:
        _int = int(userInput)
        userInput = userInput + 'm'
    except:    
        pass
    return userInput
    
    
    
def AnylyseUserInput(UserInput:str):
    try:
        _min = int(UserInput)
        return True
    except:
        pass

    if UserInput.lower() == 'c':
        #AnylyseUserInputDate()
        return False
    elif UserInput.lower() == 'off':                
        return True

    if len(UserInput) > 1:
        if UserInput[:-1].isdigit():
            if UserInput[-1].lower() == 'm':
                return True
            elif UserInput[-1].lower() == '':
                return True
            elif UserInput[-1].lower() == 'h':
                return True
            elif UserInput[-1].lower() == 'd':
                return True
            elif UserInput[-1].lower() == 'y':
                return True        
            elif UserInput[-1].lower() == 's':
                return True        
            elif UserInput[-1].lower() == 'w':                
                return True
    return False

#def AnylyseUserInputDate():
#    a = GetCustomDate()

def PrintContainterStatus():
    global CONTAINER_NAME
    global CONTAINER_SHORT_ID
    if DOCKER_IS_LOCAL:
        containerNameStr = f'{_w}Container Name : {_B}{_b} {CONTAINER_NAME} {_reset}'
    else:
        server = base.GetValue(jsonConfig,'Docker_Api_Server','Ip',verbus=False,ReturnValueForNone='')
        ServerDetail = f'{_w}Server : {_B}{_by} {server} {_reset}'
        containerNameStr = f'{ServerDetail} {_w}Container Name : {_B}{_c} {CONTAINER_NAME} {_reset}'
    containerIDStr = f'{_w}Short ID : {_B}{_c} {CONTAINER_SHORT_ID} {_reset}'    
    if CONTAINER_STATUS.lower() == 'pause':
        _Sts_Color = _m
        _Sts_Color1 = _bm        
    elif CONTAINER_STATUS.lower() == 'exited':
        _Sts_Color = _r
        _Sts_Color1 = _br
    elif CONTAINER_STATUS.lower() == 'running':
        _Sts_Color = _g
        _Sts_Color1 = _blg
    else:
        _Sts_Color = _y
        _Sts_Color1 = _by

    containerStatusStr = f'{_Sts_Color}Status : {_Sts_Color1} {CONTAINER_STATUS.upper()} {_reset}'

    containerStr = f'{containerNameStr}  /  {containerIDStr} / {containerStatusStr}'

    print("")
    print(containerStr)
    print("")

def dockerCheck():
    global CONTAINER
    global CONTAINER_NAME
    global CONTAINER_STATUS
    global CONTAINER_SHORT_ID
    global DOCKER_IS_LOCAL

    _CONTAINER = dockerLib.CheckContainerStatus()
    CONTAINER = _CONTAINER[0]
    CONTAINER_NAME = _CONTAINER[1]
    CONTAINER_STATUS = _CONTAINER[2]
    CONTAINER_SHORT_ID = _CONTAINER[3]
    DOCKER_IS_LOCAL = _CONTAINER[4]
    


####################################################
####################################################
####################################################
####################################################

if __name__ == '__main__':            
    if LogsMode == 'local':
        if base.CheckExistFile(LOG_FILE,"",PrintIt=True) is False:
            base.FnExit()
    elif LogsMode == 'docker':
        import docker
        dockerCheck()        
#        CONTAINER_NAME = ''
#        CONTAINER_STATUS = ''
#        CONTAINER_SHORT_ID = ''
#        DOCKER_IS_LOCAL = False



    All_StatusCode_1x = base.GetValue(jsonConfig,"StatusCodes",'1x')
    All_StatusCode_2x = base.GetValue(jsonConfig,"StatusCodes",'2x')
    All_StatusCode_3x = base.GetValue(jsonConfig,"StatusCodes",'3x')
    All_StatusCode_4x = base.GetValue(jsonConfig,"StatusCodes",'4x')
    All_StatusCode_5x = base.GetValue(jsonConfig,"StatusCodes",'5x')
    All_NginxStatusCode = base.GetValue(jsonConfig,"StatusCodes",'NginxStatusCode')
    
    filterStatus = False    
    UNKNOW_AGENT_Str = ''
    ## Load Filter From Config File

    FilterDict = base.GetValue(jsonConfig,"Filter",verbus=False,ReturnValueForNone={})
    FILTER_IP = base.GetValue(FilterDict,"ip",verbus=False,ReturnValueForNone=[])
    FILTER_URL = base.GetValue(FilterDict,"url",verbus=False,ReturnValueForNone=[])
    FILTER_AGENT = base.GetValue(FilterDict,"Browser",verbus=False,ReturnValueForNone=[])
    FILTER_CODE = base.GetValue(FilterDict,"Status_Code",verbus=False,ReturnValueForNone=[])
    FILTER_UNKNOW_AGENT = base.GetValue(FilterDict,"unknow_agent",verbus=False,ReturnValueForNone=[])
    FILTER_COUNTRY = base.GetValue(FilterDict,"Country",verbus=False,ReturnValueForNone=[])    
    FILTER_REFERER = base.GetValue(FilterDict,"Referer",verbus=False,ReturnValueForNone=[])        
    ManualScope = base.GetValue(FilterDict,"time",verbus=False,ReturnValueForNone='')
    GEO_IS_DISABLE = False
    Date_pattern = r'\[(\d{2})/(\w{3})/(\d{4}):(\d{2}):(\d{2}):(\d{2}) [+-]\d{4}\]'

    
    Code_1xx = []    
    Code_2xx = []
    Code_3xx = []
    Code_4xx = []
    Code_5xx = []
    Code_4xx_nginx = []
    
    #sys.argv.append("a")
    
    

    if len(sys.argv) == 1:
        AllFilterStatus()
        CheckSearchMode(GLOBAL_SEARCH_METHOD)
        LoadLogFile(ReloadLog=True)
        PrimaryMainMenuLuncher()
    else:
        print("---------")    
        

