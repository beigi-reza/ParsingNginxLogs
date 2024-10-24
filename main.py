#! /usr/bin/python3
from colorama import Fore, Back, Style
import signal
import lib.BaseFunction as base
#import Filter_Time as ChangeScope
import re
import os
import shlex
#import pandas as pd
from datetime import datetime, timedelta
import Banner
from collections import OrderedDict,Counter
from datetime import datetime

#from collections import Counter



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
LOG_FILE  = jsonConfig["Log_File"]
MAX_LINE = jsonConfig["Max_Line"]
####################################################



signal.signal(signal.SIGINT, base.handler)

####################################################
####################################################
####################################################
####################################################

class Parser:
    IP = 0
    TIME = 3
    TIME_ZONE = 4
    REQUESTED_URL = 5
    STATUS_CODE = 6
    USER_AGENT = 9

    def parse_line(self, line):
        try:
            line = re.sub(r"[\[\]]", "", line)
            data = shlex.split(line)
            result = {
                "ip": data[self.IP],
                "time": data[self.TIME],
                "status_code": data[self.STATUS_CODE],
                "requested_url": data[self.REQUESTED_URL],
                "user_agent": data[self.USER_AGENT],
            }
            return result
        except Exception as e:
            raise e

#def LoadVaraiableFromLogs(LogsDf):
#    global list_IP_Unique   
#    global list_IP          
#    global User_Agent_Unique
#    global User_Agent       
#    list_IP_Unique     = LogsDf["ip"].unique()
#    list_IP            = LogsDf["ip"].value_counts().to_dict()
#    User_Agent_Unique  = LogsDf["user_agent"].unique()
#    User_Agent         = LogsDf["user_agent"].value_counts().to_dict()

def LoadLogFile():
    base.clearScreen()
    #Banner.RonixLogo()    
    Banner.PleaseWait()
    print("")
    print(f"{_B}{_w} Please Wait for analyze log File{_reset}")        
    global url_counter
    #url_counter = ParingLogFile()
    url_counter = ParingLogFileWithFilter()
    print(status_code_counter)


def ParingLogFileWithFilter():
    global TimeofReadLogFile
    global CountLogs
    global To_Date
    global From_Date 
        
    TimeofReadLogFile = datetime.now()        
    # Regex        
    #url_pattern = re.compile(r'"GET\s(\/[^\s]*)')
    Date_pattern = r'\[(\d{2})/(\w{3})/(\d{4}):(\d{2}):(\d{2}):(\d{2}) [+-]\d{4}\]'

    global Ip_counter
    global url_counter    
    global Agent_counter
    global Unknown_Agent_counter
    global browser_counter
    global status_code_counter
    url_counter = Counter()
    Ip_counter = Counter()    
    Agent_counter = Counter()
    Unknown_Agent_counter = Counter()
    browser_counter = Counter()
    status_code_counter = Counter()

    CountLogs = 0    
    
    with open(LOG_FILE, 'r') as f:
            FirstLine = True
            for line in f:
                AddThisLine = True                
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
                    
                url = GetUrlFromLine(line,FILTER_URL)
                if url == None:
                    AddThisLine = False
                
                agent = getAgentFromLine(line,FILTER_AGENT)
                if agent == None:
                    AddThisLine = False                
                    
                if FILTER_UNKNOW_AGENT != '':
                    AllAgent = FilterByAllAgent(line,FILTER_UNKNOW_AGENT)
                    if AllAgent == None:
                        AddThisLine = False
                        
                StatusCode = GetCodeFromLine(line,FILTER_CODE)
                if StatusCode == None:
                    AddThisLine = False

                if AddThisLine:
                    Ip_counter[ip_address] +=1
                    url_counter[url] += 1
                    status_code_counter[StatusCode] += 1
                    if agent != 'unknow':
                        browser_counter[agent] += 1
                    #Unknown_Agent_counter[AllAgent] += 1
    return url_counter            


def GetCodeFromLine(line,CodeFilter = []):
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


def GetIpFromLine(line,IpFilter = ''):
    IP_pattern = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
    IpMatch = re.search(IP_pattern, line)            
    if IpMatch: 
        ip_address = IpMatch.group(1)
        if IpFilter == '':
            return ip_address
        else:            
            FindIp = re.findall(f"^{IpFilter}",ip_address)
            if FindIp:
                return ip_address
            else:
                return None
    return None        

def GetUrlFromLine(line,URLFilter = ''):
    url_pattern = re.compile(r'"GET\s(\/[^\s]*)')
    matchURL = url_pattern.search(line)
    if matchURL:        
        url = matchURL.group(1)  # Get the matched URL
        if URLFilter == '':
            return url
        else:            
            if URLFilter in line:            
                return url
    return None

def getAgentFromLine(line,AgentFilter = []):
    browser_regex = r"(Chrome|Firefox|Safari|Opera|Edge|Trident)"
    user_agent = line.split('"')[-4]
    matchBrowser = re.search(browser_regex, user_agent)    
    if matchBrowser:
        Browser = matchBrowser.group(1)
        if AgentFilter == []:
            return Browser
        else:
            for _agent in AgentFilter:
                if Browser.lower() in _agent:
                    return Browser                
            else:
                return None    
    
    Unknown_Agent_counter[user_agent] +=1                                                
    return 'unknow'

def FilterByAllAgent(line,AgentFilter):
    if AgentFilter != "":
        agentName = line.split('"')[-4]    
        FindAgent = re.findall(f"^{AgentFilter}",agentName)
        if FindAgent:
            return agentName        
    return None 

def printStatus():    
    RowAnalyzed = f"{_B}{_b}Row analyzed {_bb} {CountLogs} {_reset}"    
    CountIP = f"{_y}Uniq ip detected  {_by} {len(Ip_counter)} {_w}{_reset}"    
    CountAgent = f"{_g} Unknown agent detected {_blg} {len(Unknown_Agent_counter)} {_w}{_reset}"    
    CountURL = f"{_c} Uniq URL detected {_bc} {len(url_counter)} {_w}{_reset}"    
    LastSync = f'{_B}{_b} at {_bb} {TimeofReadLogFile.strftime("%I:%M:%S %p")} {_w}{_reset}'
    TimeofLog = f'{_w}Log Found From [ {_B}{_w}{From_Date.strftime("%a %d %b %Y - %I:%M:%S %p")}{_reset}{_w} ] to [ {_B}{_w}{To_Date.strftime("%a %d %b %Y - %I:%M:%S %p" )}{_reset}{_w} ]{_reset}'    
#    if ManualScope == '':        
#        TimeofLog = f'{_w}Log Found From [ {_B}{_w}{From_Date.strftime("%a %d %b %Y - %I:%M:%S %p")}{_reset}{_w} ] to [ {_B}{_w}{To_Date.strftime("%a %d %b %Y - %I:%M:%S %p" )}{_reset}{_w} ]{_reset}'    
#    else:
#        TimeofLog = f'{_w}Time Range Changed for ( {_B}{_br} {ManualScope.upper()} {_reset}{_w} ) from [ {_B}{_bm}{From_Date.strftime("%a %d %b %Y - %I:%M:%S %p")}{_reset}{_w} ] to [ {_B}{_bm}{To_Date.strftime("%a %d %b %Y - %I:%M:%S %p" )}{_reset}{_w} ] {_reset}'



    print ("{:<30}".format(RowAnalyzed + LastSync))
    print("")
    print("{:<30} {:<30} {:<30}".format(CountIP,CountAgent,CountURL))
    print("")
    print ("{:<100}".format(TimeofLog))
    
    

    if filterStatus:
        print("")
        print(f'{_w}-------------------------- Filter information --------------------------{_reset}')
        print("")
        print(f"{_w}Filter on :{_reset}")
        print("")
        if ManualScope != '':                    
            print(f'{_g}{_B}TIME: {_reset}{_w} Time Range for ( {_B}{_br} {ManualScope.upper()} {_reset}{_w} ) from [ {_B}{_bm}{From_Date.strftime("%a %d %b %Y - %I:%M:%S %p")}{_reset}{_w} ] to [ {_B}{_bm}{To_Date.strftime("%a %d %b %Y - %I:%M:%S %p" )}{_reset}{_w} ] {_reset}')        
            print("")
        if FILTER_IP != '':            
            print(f'{_w} IP : Including logs with ( {_B}{_bm} {FILTER_IP} {_reset} ) in IP Address')
            print("")
        if FILTER_URL != '':            
            print(f'Filter on URL is {_blg} ON {_reset}{_w} Including logs with ( {_B}{_bm} {FILTER_URL} {_reset} ) in Requset URL')
            print("")
        if FILTER_AGENT != []:
            print(f'Filter on Browser is {_blg} ON {_reset}{_w} including items received from one of the browsers {_B}{_bm} {FILTER_AGENT} {_reset}.')
            print("")
        if FILTER_CODE != []:
            print(f'Filter on HTTP response status codes is {_blg} ON {_reset}{_w} including items received from one of the browsers {_B}{_bm} {FILTER_CODE} {_reset}.')
            print("")





        print(f'{_w}-------------------------- Filter information --------------------------{_reset}')


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
    print("")
    print (_w + _B +"{:<5} {:<20} {:<10}".format("No.","IP","Count") + _reset )    
    print("")
    xI = 1
    for _ in ordered_dict :        
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
            print (_B + _w + "{:<5} {:<20} {:<10}".format(str(xI),ClmnColor + _ , str(ordered_dict[_])) + _reset )
            xI += 1
        else:
            break    
    base.PrintMessage(messageString="End of List ...", MsgType="notif", AddLine = True, addSpace = 0, BackgroudMsg = False)  
def FnPrintAgent(ListOfAgent,MaxPrint = 50):
    ordered_dict = order_dict_by_value(ListOfAgent)
    base.clearScreen()
    Banner.ParsingLogo()
    print("")
    print (_w + _B +"{:<5} {:<10} {:<100}".format("No.","Count","Agent") + _reset )    
    print("")
    xI = 1
    for _ in ordered_dict :        
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
            print (_B + _w + "{:<5} {:<10} {:<100}".format(str(xI),ClmnColor + str(ordered_dict[_]) ,_ ) + _reset )
            xI += 1
        else:
            break    
    base.PrintMessage(messageString="End of List ...", MsgType="notif", AddLine = True, addSpace = 0, BackgroudMsg = False)  

def FnPrintBrowser(ListofBrowser):   
    order_dict = order_dict_by_value(ListofBrowser)
    base.clearScreen()
    Banner.ParsingLogo()
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
    base.clearScreen()
    Banner.ParsingLogo()    
    printStatus()    
    if filterStatus:
        FilterStr = f'{_y}[ {_br}{_B} ENABLE {_reset}{_y} ]'
    else:
        FilterStr = f'{_y}[ {_w}Disable {_y}]'    
        
    while True:        
        print(f"{_w}")
        print(f"type [ {_D}{_w}q{_N}{_w} ] quit{_reset}")        
        print(f"     [ {_c}i{_w} ] {_c}list of IP{_reset}")
        print(f"     [ {_c}u{_w} ] {_c}list of url{_reset}")
        print(f"     [ {_c}b{_w} ] {_c}list of Browser{_reset}")
        print(f"     [ {_c}c{_w} ] {_c}list of Status Code{_reset}")
        print(f"     [ {_c}a{_w} ] {_c}list of Unknown Agent{_reset}")
        print(f"     [ {_y}f{_w} ] {_y}Filter/s - {FilterStr}{_reset}")        
        print(f"     [ {_r}reload{_w} ] {_r}Reload Log file{_reset}")
    
    
        print("")
        UserInput = input(f"{_B}{_w}Enter Command :{_reset}")
        if UserInput.strip() == '':
            UserInput = 'i'
        for _i in ['q','i','u','b','c','a','f','reload']:
            if _i == UserInput.strip().lower():
                return _i
        
        
    
def PrimaryMainMenuLuncher():
    UserInput = MainMenu()
    if UserInput == 'q':
        base.FnExit()
    elif UserInput == 'i':
        NumberInt = GetNumberofFromUser(len(Ip_counter))
        FnPrintIP(Ip_counter,NumberInt)
        input("Press Enter to continiue ...")
    elif UserInput == 'u':
        NumberInt = GetNumberofFromUser(len(url_counter))
        PrintURL(url_counter,NumberInt)
        input("Press Enter to continiue ...")
    elif UserInput == 'b':
        FnPrintBrowser(browser_counter)
        input("Press Enter to continiue ...")
    elif UserInput == 'c':
        printStatusCode()
        input("Press Enter to continiue ...")
    elif UserInput == 'a':
        NumberInt = GetNumberofFromUser(len(Unknown_Agent_counter))
        FnPrintAgent(Unknown_Agent_counter,NumberInt)
        input("Press Enter to continiue ...")
    elif UserInput == 'f':
        FilterMenuLuncher(FilterMenu())
    elif UserInput == 'reload':    
        LoadLogFile()
        #LoadVaraiableFromLogs(logs_df)    
    StartHome()

def FilterMenu():
    global ManualScope
    base.clearScreen()
    Banner.ParsingLogo()    
    while True:
        if AllFilterStatus():
            print(f'{_r}Filter is {_w}Enabled{_reset}')            
        else:    
            print(f' {_B}{_bb}All Filter is OFF{_reset}')            

        if ManualScope == '':
            StrTimeRange = f' is {_w}OFF{_reset}' 
        else:
            StrTimeRange = f' is {_bb} ON {_reset}{_w} : {_y}{ManualScope}'         
        
        if FILTER_IP == '':
            StrIP = f' is {_w}OFF{_reset}' 
        else:            
            StrIP = f' is {_bb} ON {_reset}{_w} : {_y}{FILTER_IP}' 
            
        if FILTER_URL == '':
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
        
        if FILTER_UNKNOW_AGENT == '':
            UnknowStr = f' is {_w}OFF{_reset}'
        else:
            UnknowStr = f' is {_bb} ON {_reset}{_w} : {_y}{FILTER_UNKNOW_AGENT}'
            
        print(f"{_w}")
        print(f"type [ {_D}{_w}q{_N}{_w}     ] quit{_reset}")        
        print(f"     [ {_D}{_w}Enter{_N}{_w} ] for back to main menu{_reset}")            
        print(f"     [ {_D}{_w}off{_N}{_w}   ] All Filter OFF{_reset}")        
        print(f"     [ {_b}i{_w} ] {_b} Filter on IP{StrIP}{_reset}")
        print(f"     [ {_b}u{_w} ] {_b} Filter on url{StrURL}{_reset}")
        print(f"     [ {_b}b{_w} ] {_b} Filter on Browser{BrwsStr}{_reset}")
        print(f"     [ {_b}c{_w} ] {_b} Filter on Status Code{CodeStr}{_reset}")
        print(f"     [ {_b}a{_w} ] {_b} Filter on Agent{UnknowStr}{_reset}")        
        print(f"     [ {_b}t{_w} ] {_b} Filter on Time range{StrTimeRange} {_reset}")        
        
    
        print("")
        UserInput = input(f"{_B}{_w}Enter Command :{_reset}")
        for _i in ['q','i','u','b','c','a','t','off','']:
            if _i == UserInput.strip().lower():
                return _i.lower()
        
def FilterMenuLuncher(UserInput):        
    global ManualScope
    global FILTER_IP
    global FILTER_URL
    global FILTER_CODE
    global FILTER_UNKNOW_AGENT
    global filterStatus
    if UserInput == 'q':
        base.FnExit()
    elif UserInput == 'i':
        base.clearScreen()
        Banner.ParsingLogo()
        IP_Filter = IpFilterMenu()        
        if IP_Filter == 'off':
            FILTER_IP = ''    
        elif IP_Filter != '':
            FILTER_IP = IP_Filter
        base.clearScreen()
        Banner.ParsingLogo()
        FilterMenuLuncher(FilterMenu())                
    elif UserInput == 'u':
        base.clearScreen()
        Banner.ParsingLogo()
        Url_Filter = UrlFilterMenu()
        if Url_Filter == 'off':
            FILTER_URL = ''
        else:
            FILTER_URL = Url_Filter
        base.clearScreen()
        Banner.ParsingLogo()
        FilterMenuLuncher(FilterMenu())    
    elif UserInput == 'b':
        BrowserFilterMenuLuncher(BrowserFilterMenu())
    elif UserInput == 'c':
        Code_Filter = StatusCodeFilterMenu()
        if Code_Filter == 'off':
            FILTER_CODE = []        

        base.clearScreen()
        Banner.ParsingLogo()
        FilterMenuLuncher(FilterMenu())    
            
    elif UserInput == 'a':
        base.clearScreen()
        Banner.ParsingLogo()
        UnkhowAgent = UnknowAgentMenuFilter()        
        if UnkhowAgent == 'off':
            FILTER_UNKNOW_AGENT = ''
        else:
            FILTER_UNKNOW_AGENT = UnkhowAgent
        base.clearScreen()
        Banner.ParsingLogo()
        FilterMenuLuncher(FilterMenu())    
    elif UserInput == 't':
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
    elif UserInput.strip().lower() == 'off':
        base.clearScreen()
        Banner.ParsingLogo()
        filterStatus = False
        AllFilterStatus(AllFilterOff=True)
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
            Code_1xx.append(int(UserInput))
        elif intUserinput in All_StatusCode_2x:
            Code_2xx.append(int(UserInput))
        elif intUserinput in All_StatusCode_3x:
            Code_3xx.append(int(UserInput))
        elif intUserinput in All_StatusCode_4x:
            Code_4xx.append(int(UserInput))
        elif intUserinput in All_StatusCode_5x:
            Code_5xx.append(int(UserInput))
        elif intUserinput in All_NginxStatusCode:
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

def PrintURL(url_couter,MaxPrint):
    #print(len(url_couter))
    Banner.ParsingLogo()
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


def UrlFilterMenu():
    print(f"{_w}type  [ {_N}{_w}q{_reset}{_w}     ] for quit{_reset}")        
    print(f"{_w}      [ {_N}{_w}enter{_reset}{_w} ] for back{_reset}")                    
    print(f"{_w}      [ {_N}{_w}off{_reset}{_w} ] To disable the filter on URL {_reset}")                    
    UserInput = input(f'{_B}{_w}Enter URL or part of it: ')
    if UserInput.strip().lower() == "q":
        base.FnExit()
    else:    
    #elif UserInput.strip().lower() == "":
        return UserInput.strip().lower()

def UnknowAgentMenuFilter():
    print(f"{_w}type  [ {_N}{_w}q{_reset}{_w}     ] for quit{_reset}")        
    print(f"{_w}      [ {_N}{_w}enter{_reset}{_w} ] for back{_reset}")                    
    print(f"{_w}      [ {_N}{_w}off{_reset}{_w} ] To disable the filter on Unknow Agent {_reset}")                    
    UserInput = input(f'{_B}{_w}Enter Unknow Agent or part of it: ')
    if UserInput.strip().lower() == "q":
        base.FnExit()
    else:    
    #elif UserInput.strip().lower() == "":
        return UserInput.strip().lower()


def IpFilterMenu():
    print(f"{_w}type  [ {_N}{_w}q{_reset}{_w}     ] for quit{_reset}")        
    print(f"{_w}      [ {_N}{_w}enter{_reset}{_w} ] for back{_reset}")                    
    print(f"{_w}      [ {_N}{_w}off{_reset}{_w} ] To disable the filter on IP Address {_reset}")                    
    print(f"{_w}eg.   [ {_y}192.168.100.10{_w} ]{_b} To filter a specific IP Address{_reset}")    
    print(f"{_w}      [ {_y}192.168{_w} ]{_b} To filter a range of IP Address{_reset}")
    UserInput = input(f'{_B}{_w}Enter IP or a part of it (starts with it) : ')
    if UserInput.strip().lower() == "q":
        base.FnExit()
    else:    
    #elif UserInput.strip().lower() == "":
        return UserInput.strip().lower()


    
def AllFilterStatus(AllFilterOff = False):
    global filterStatus
    global FILTER_IP 
    global FILTER_URL
    global FILTER_AGENT
    global FILTER_CODE
    global FILTER_UNKNOW_AGENT
    global ManualScope
    
    if AllFilterOff:
        FILTER_IP = ''
        FILTER_URL = ''
        FILTER_AGENT = []
        FILTER_CODE = []
        ManualScope = ''
        FILTER_UNKNOW_AGENT = ''        
    _filterStatus = False
    if ManualScope != '':
        _filterStatus = True
    if FILTER_IP != '':
        _filterStatus = True
    if FILTER_URL != '':
        _filterStatus = True
    if FILTER_AGENT != []:
        _filterStatus = True
    if FILTER_CODE != []:
        _filterStatus = True
    if FILTER_UNKNOW_AGENT != '':
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


def StartHome():
    base.clearScreen()
    Banner.ParsingLogo()    
    printStatus()
    PrimaryMainMenuLuncher()


####################################################
####################################################
####################################################
####################################################

if base.CheckExistFile(LOG_FILE,"",PrintIt=True) is False:
    base.FnExit()


if __name__ == '__main__':        
    
    All_StatusCode_1x = [100,101,102,103]
    All_StatusCode_2x = [200, 201, 202, 203, 204, 205, 206, 207, 208, 226]
    All_StatusCode_3x = [300,301,302,303,304,305,306,307,308]
    All_StatusCode_4x = [400,401,402,403,404,405,406,407,408,409,410,411,412,413,414,415,416,417,418,421,422,423,424,425,426,428,429,431,451]
    All_StatusCode_5x = [500,501,502,503,504,505,506,507,508,510,511]
    All_NginxStatusCode = [444,494,495,496,497,499]
        
    filterStatus = False
    ManualScope = '' 
    FILTER_IP = ''
    FILTER_URL = ''
    FILTER_UNKNOW_AGENT = ''
    FILTER_AGENT = []
    FILTER_CODE = []    
    
    Code_1xx = []    
    Code_2xx = []
    Code_3xx = []
    Code_4xx = []
    Code_5xx = []
    Code_4xx_nginx = []
    
    LoadLogFile()
    #LoadVaraiableFromLogs(logs_df)    
    StartHome()

