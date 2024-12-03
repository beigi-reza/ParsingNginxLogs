from colorama import Fore, Back, Style
import docker
import requests
import lib.BaseFunction as base
import Banner

####################################################
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
####################################################


def FetchListDockerContainers(Server:str,port:str,DockerIsLocal:str ):    
    DOCKER_API_URL_CONTAINER = f"http://{Server}:{port}/v1.41/containers/json"   
    if DockerIsLocal:
        try:
            client = docker.DockerClient(base_url='unix://var/run/docker.sock')
            containers = client.containers.list(all=True)
        except:
            print(f"Error: Unable to fetch containers from localhost (Docker on this machine).")            
            return None
        return containers
    else:    
        try:
            params = {"all": "true"}
            response = requests.get(DOCKER_API_URL_CONTAINER,params, timeout = 5)
            if response.status_code == 200:
                containers = response.json()
                return containers
            else:
                print(f"Error: Unable to fetch containers (Status Code: {response.status_code})")
                print(response.text)
                return None
        except Exception as e:
            print(f"Exception occurred: {e}")
            return None
def CheckContainerExists(ContainerName,dockerIsLocal):
    Server= base.GetValue(jsonConfig,'Docker_Api_Server','Ip',verbus=False,ReturnValueForNone='127.0.0.1')
    port = base.GetValue(jsonConfig,'Docker_Api_Server','Port',TerminateApp=True)    
    if Server in ['localhost','127.0.0.1','','local','.']:
        dockerIsLocal = True
    else:
        dockerIsLocal = False

    ListofContainer = FetchListDockerContainers(Server,port,dockerIsLocal)
    if ListofContainer == None:
        base.PrintMessage('An error occurred',TreminateApp=True)
    elif len(ListofContainer) == 0:
        print("")
        print(f"{_B}{_r}No running containers found.")
        base.FnExit()
    else:
        if dockerIsLocal:
            for _ in ListofContainer:
                _ContanerName = _.name
                if _ContanerName.startswith("/"):
                    _ContanerName = _ContanerName[1:]
                if _ContanerName == ContainerName:
                    return _
        else:    
            for _ in ListofContainer:
                _ContanerName = _["Names"][0]
                if _ContanerName.startswith("/"):
                    _ContanerName = _ContanerName[1:]
                if _ContanerName == ContainerName:
                    return _
            return None

def CheckContainerStatus():
    _Server = base.GetValue(jsonConfig,'Docker_Api_Server','Ip',verbus=False,ReturnValueForNone='127.0.0.1')
    _ContainerName =  base.GetValue(jsonConfig,"Docker_Api_Server","container_name",verbus=False)
    if _Server in ['localhost','127.0.0.1','','local','.']:
        _Localserver = True
    else:
        _Localserver = False

    _Container = CheckContainerExists(_ContainerName,_Localserver)
    if _Localserver:    
        Container_name = _Container.name
        Container_status = _Container.status
        Container_short_id = _Container.short_id            
    else:
        Container_name = _Container["Names"][0].lstrip("/")        
        Container_status = _Container["State"]
        Container_short_id = _Container["Id"][:12]
    return _Container,Container_name,Container_status,Container_short_id,_Localserver
        

def LoadContainerLog(container_name,dockerIsLocal):
#    print("")
#    print("Please Wait For fetch log from Docker ...")
#    print("")
    if dockerIsLocal:
        try:
            logs = container_name.logs().decode("utf-8")
        except:
            return None    
    else:
        _Server = base.GetValue(jsonConfig,'Docker_Api_Server','Ip',TerminateApp=True)
        _port = base.GetValue(jsonConfig,'Docker_Api_Server','Port',TerminateApp=True)        
        client = docker.DockerClient(base_url=f"tcp://{_Server}:{_port}")
        try:
            _Name = container_name["Names"][0]
            _container = client.containers.get(_Name)
            logs = _container.logs().decode("utf-8")
        except docker.errors.NotFound:
            print(f"Container '{container_name}' not found.")
            return None
        except Exception as e:
            print(f"An error occurred: {e}")            
            return None
    return logs


#####################################

if __name__ == "__main__":        
    print(f"{Style.NORMAL + Fore.YELLOW}You should not run this file directly")  
else:
    from parsing import jsonConfig

