#! /usr/bin/python3
from colorama import Fore, Back, Style
import signal
import lib.BaseFunction as base
import re
import os
import shlex
#import pandas as pd
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
_bbw = Back.WHITE + Fore.BLACK

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
    #global logs_df
    global url_counter
    global DateString    
    now = datetime.now()
    DateString = now.strftime("%d/%m/%Y %H:%M:%S")    
    #logs_df = ParsingLogFileByParser() 
    url_counter = ParingLogFile()
    
#def ParsingLogFileByParser():
#    parser = Parser()    
#    with open(LOG_FILE, "r") as f:
#        log_entries = [parser.parse_line(line) for line in f]        
#    _logs_df = pd.DataFrame(log_entries)            
#    return _logs_df

def ParingLogFile():
    #            
    global CountLogs
    global L_day
    global L_month
    global L_year
    global L_hour
    global L_minute
    global L_second
    
    global F_day
    global F_month
    global F_year
    global F_hour
    global F_minute
    global F_second

    # Regex
    Agent_pattern = r'"[^"]*" "[^"]*" "([^"]+)"'
    IP_pattern = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
    url_pattern = re.compile(r'"GET\s(\/[^\s]*)')
    Date_pattern = r'\[(\d{2})/(\w{3})/(\d{4}):(\d{2}):(\d{2}):(\d{2}) [+-]\d{4}\]'
    # Dictionary to store URLs and their counts
    global Ip_counter
    global url_counter
    global Agent_counter
    url_counter = Counter()
    Ip_counter = Counter()
    Agent_counter = Counter()
    
    # Read the log file and parse URLs
    CountLogs = 0
    with open(LOG_FILE, 'r') as f:
        FirstLine = True
        for line in f:
            CountLogs += 1
            DateMatch = re.search(Date_pattern, line)
            if DateMatch:
                L_day, L_month, L_year, L_hour, L_minute, L_second = DateMatch.groups()
                if FirstLine: # ثبت تاریخ اولین خط
                    F_day, F_month, F_year, F_hour, F_minute, F_second = DateMatch.groups()
                    FirstLine = False                
            
            IpMatch = re.search(IP_pattern, line)
            ## list_IP
            if IpMatch: 
                ip_address = IpMatch.group(1)
                Ip_counter[ip_address] +=1
            ## list_URL
            matchURL = url_pattern.search(line)
            if matchURL:
                url = matchURL.group(1)  # Get the matched URL
                url_counter[url] += 1
            
            AgentMatch = re.search(Agent_pattern, line)
            if AgentMatch:
                user_agent = AgentMatch.group(1)
                Agent_counter[user_agent] += 1

                
    return url_counter


def printStatus():    
    RowAnalyzed = f"{_B}{_b}Row analyzed {_bb} {CountLogs} {_reset}"    
    CountIP = f"{_y}Uniq ip detected  {_by} {len(Ip_counter)} {_w}{_reset}"
    CountAgent = f"{_g} Uniq agent detected {_blg} {len(Agent_counter)} {_w}{_reset}"    
    CountURL = f"{_c} Uniq URL detected {_bc} {len(url_counter)} {_w}{_reset}"    
    LastSync = f"{_w}Parsing log File at {_bbw} {DateString} {_w}{_reset}"    
    TimeofLog = f"{_w} Between [ {_b}{F_day} {F_month} {F_year} / {F_hour}:{F_minute}:{F_second}{_w} ] and [ {_b}{L_day} {L_month} {L_year} / {L_hour}:{L_minute}:{L_second} {_w}]"
    #print(f"{_w}[ {_y}{len(logs_df.index)} {_w}] Row analyzed{_reset}")
    print ("{:<30}".format(RowAnalyzed,LastSync))
    print ("{:<30}{:<100}".format(LastSync,TimeofLog))
    print("")
    print("{:<30} {:<30} {:<30}".format(CountIP,CountAgent,CountURL))

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
    """
    لیست مرورگرها و تعداد تکرار آن را پرینت می کتد
    
    Args: 
        ListOfIP :  received from parser
        MaxPrint :  It should not be printed smaller than what amount        
    """
    ordered_dict = order_dict_by_value(User_Agent)
    base.clearScreen()
    Banner.ParsingLogo()
    print("")
    print (_w + _B +"{:<5} {:<10} {:<150}".format("No.","Count","Agent") + _reset )    
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
            print (_B + _w + "{:<5} {:<10} {:<150}".format(str(xI), ClmnColor + str(ordered_dict[_]), _ ) + _reset )
            xI += 1
        else:
            break    
    base.PrintMessage(messageString="End of List ...", MsgType="notif", AddLine = True, addSpace = 0, BackgroudMsg = False)  

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
        

def MainMenu():
    print(f"{_w}")
    print(f"type [ {_D}{_w}q{_N}{_w}     ] quit{_reset}")
    print(f"     [ {_D}{_w}enter{_N}{_w} ] for Main Menu")
    print(f"     [ {_b}ip{_w}    ] list of IP")
    print(f"     [ {_b}url{_w}   ] list of url")
    print(f"     [ {_b}Agent{_w} ] list of Agent")
    print(f"     [ {_y}code{_w} ] list of Status Code")
    print(f"     [ {_r}reload{_w} ] Reload Log file")
    
    
    print("")
    UserInput = input(f"{_B}{_w}Enter Command :{_reset}")
    if UserInput.strip() == "":
        base.clearScreen()
        Banner.ParsingLogo()    
        printStatus()
        MainMenu()        
        
    if UserInput.strip().lower() == "ip":
        NumberInt = GetNumberofFromUser(len(list_IP_Unique))
        FnPrintIP(list_IP,NumberInt)
        MainMenuIP()
    elif UserInput.strip().lower() == "agent":
        NumberInt = GetNumberofFromUser(len(User_Agent_Unique))
        FnPrintAgent(User_Agent,NumberInt)
        MainMenu()
    elif UserInput.strip().lower() == "url":
        NumberInt = GetNumberofFromUser(len(url_counter))
        PrintURL(url_counter,NumberInt)
        MainMenu()
    elif UserInput.strip().lower() == "code":
        printStatusCode()
        print("")
        MainMenu()
    elif UserInput.strip().lower() == "reload":
        LoadLogFile()
        LoadVaraiableFromLogs(logs_df)    
        base.clearScreen()
        Banner.ParsingLogo()    
        printStatus()
        MainMenu()
    
    
    

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
    log_pattern = re.compile(r'"GET\s(\/[^\s]*)\sHTTP/1\.\d"\s(\d{3})')
    status_code_counter = Counter()
    with open(LOG_FILE, 'r') as f:
        for line in f:
            match = log_pattern.search(line)
            if match:
                url = match.group(1)  # Extract the URL
                status_code = int(match.group(2))  # Extract the status code
                status_code_counter[status_code] += 1  # Increment the count for this status code
    base.clearScreen()
    Banner.ParsingLogo()    
    print("")    
    for status_code, count in status_code_counter.most_common():
        CodeColor = _w
        occurrencesMSg = "occurrences"
        if status_code in [200, 201, 202, 203, 204, 205, 206, 207, 208, 226]:
            CodeColor = _g
        elif status_code in [300,301,302,303,304,305,306,307,308]:
            CodeColor = _y
        elif status_code in [400,401,402,403,404,405,406,407,408,409,410,411,412,413,414,415,416,417,418,421,422,423,424,425,426,428,429,431,451]:
            CodeColor = _r
        elif status_code in [500,501,502,503,504,505,506,507,508,510,511]:
            CodeColor = _c
        elif status_code in [444,494,495,496,497,499]:
            CodeColor = _r
            occurrencesMSg = f"expands by Nginx"
        
        print(f"{_w}Status Code [ {CodeColor}{status_code}{_reset}{_w} ] : {_b}{count}{_w} {occurrencesMSg}")
    


    
####################################################
####################################################
####################################################
####################################################

if base.CheckExistFile(LOG_FILE,"",PrintIt=True) is False:
    base.FnExit()


if __name__ == '__main__':    
    LoadLogFile()
    #LoadVaraiableFromLogs(logs_df)    
    base.clearScreen()
    Banner.ParsingLogo()    
    printStatus()
    MainMenu()


