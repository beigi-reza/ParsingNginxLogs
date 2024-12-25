# Parsing Nginx Logs


Nginx access logs provide valuable insights into website traffic, user behavior, and server performance. To parse these logs effectively, you’ll need to extract relevant information and transform it into a usable format.

This program has tried to check the nginx log from different angles and give you a complete view.

Information extracted from the `logfile`(Access.log) or `docker container` log

- The date range of the log file (the analyzed logs are related to what da.te range).

- IPs 
- URLs 
- Browser 
- Status Code
- Unknown Agent
- Referer
- Country
- Timezone
- Filters: can be created on any of the following items and the above 
information can be received according to the filters
- `Export` Data as `TXT` or `SCV`




### requirement

  - [Python 3.x](https://www.python.org/)

in current directory run this command for install python Requirement package

```sh
pip install requirements.txt
```  

### Attention

To get the correct information, make sure that the **date and time** of the server are correct.

If you run `Nginx` in a container such as **Docker**, the container's time are completely independent from the server and must be set separately and are generally UTC.
 

# Config & Run

```bash
git clone https://github.com/beigi-reza/ParsingNginxLogs.git
```

## Update `config.json`

Edit Config File

```sh
vim config/config.json
```

## ParsingMode

Log entry mode :
 - **`file`** : If Nginx is running normally or there is direct access to the log file (access.log)

 - **`docker`** : If Nginx is running on docker and logs stream on **STDOUT**
```json
{
  "ParsingMode" : "file",
}
```
### File mode

Edit **Log_File** if **ParsingMode** is **`file`**
```json
    "LocalMode":{
        "Log_File" : "/home/beigi/temp/nginx/access.log.1"
    },
```
## Docker Mode
Edit **Docker_Api_Server** if **ParsingMode** is `docker`
```json
    "Docker_Api_Server" : {        
        "container_name" : "nginx",
        "Ip" : ".",
        "Port" : "2375"
    },
```
In Docker mode, it is possible to connect remotely to another server. But you must ***Enable docker remote API*** on docker host

if **Ip** in **Docker_Api_Server** is empty or `localhost`,`127.0.0.1`,`local`,`.` Connecting to Docker via docker daemon instead of an docker API.

## Search Method
When using filters, you can change the type of filter action by changing the search type.
This change affects the **IP**, **url**, **agent**, and **referer** filters.

  - **`start`** :The search term must be at the beginning of the phrase.
  - **`end`**: The search term must be at the end of the phrase.
  - **`all`**: The search term can be anywhere in the phrase.
  - **`exactly`**: Search term exactly matches the phrase

```json
{
  "SearchMode" : "start",
}
```



## Proxy or LoadBalance

If request passed through a proxy or load balancer, nginx log structure changed.
If the number of detected IPs is very low, you may need to change this option.


```json
{
  "Proxy_or_LoadBalance" : false,
}
```

## Location & TimeZone (Geo)

To identify IP information, maxmind services were used.
You can create your own location by adding a location to the location section.


```json
"GeoConfig" : {        
        "GeoDatabasePath" : "/home/beigi/myApp/ParsingNginxLogs/geoLocation/GeoLite2-City.mmdb",
        "location" :{
            "Ronix" : {
                "Name" : "company",
                "IP" : ["10.*.*.*","10.100.*.*","5.160.13.254"],
                "Country" : "Iran",
                "Region" : "Tehran",
                "City" : "Tehran",
                "Latitude": "",
                "Longitude": "",
                "Time Zone": "Asia/Tehran"                
            },
        }
    },
```
## Filters

One or more filters can be set as default values.

```json
    "Filter" : {
        "ip" : [],
        "url" : ["/en","/blog"],
        "Browser" : [],
        "Status_Code" : ["404","403"],
        "unknow_agent" : [],
        "time" : "",
        "Country" : [],
        "Referer" : []
    }

```

## Status Code Group

List of Status codes and groups for each, this category is used in reports and code grouping.

```json
    "StatusCodes" :{
        "1x": [100,101,102,103],
        "2x": [200, 201, 202, 203, 204, 205, 206, 207, 208, 226],
        "3x": [300,301,302,303,304,305,306,307,308],
        "4x": [400,401,402,403,404,405,406,407,408,409,410,411,412,413,414,415,416,417,418,421,422,423,424,425,426,428,429,431,451],
        "5x": [500,501,502,503,504,505,506,507,508,510,511],
        "NginxStatusCode": [444,494,495,496,497,499]
    },

```






















































## RUN

```bash
cd ParsingNginxLogs
./main.py
```

## Filters

Filters can be created on one or all of the following items. These filters affect all reports, and reports are prepared again with the effect of these filters.

If multiple filters are selected, the relationship between them will be **`and`**

### Filter by IP

Filter on a IP or part of IP

example

- `82.79.160.29`  All requests from an IP
- `66.249.64`  All requests from the IP range
- `66.249`  All requests from the IP range
- `212` All requests from the IP range

### Filter by URL

Filter on requests that have gone to a specific URL

- `/`  All Request For Home
- `/en`  All Request for url **/en**
- `/js/jsbase.min.js` All Request for url **/js/jsbase.min.js**


### Filter by Browser

Filter on requests received from one or more browsers

- `[Chrome]` All Request from browser **Chrome**
- `[Firefox,Safari]` All Request from browser **Firefox** and **Safari**

### Filter by Unknow Agent

Filter requests by browser or agent was unknown based on the name or description of the agent.

- `facebookexternalhit` All Request from agent  **facebookexternalhit**
- `Clarity-Bot` All Request from agent  **Clarity-Bot**
- `yandex.com` All Request from **yandex Bot**

### Filter by Time range

Filter information based on date range.

You can specify the range of receiving the report to a time range


- `5` for 5 minutes past
- `15m` for 15 minutes past
- `25s` for 25 seconds past
- `2h` for 2 hours past
- `3d` for 3 Days past
- `1w` for 1 Week past

If the entered date range is greater than the date range of the log file, the entire log file will be parsing


## Export

The Extracted Data can be saved in `Text` and `CSV` file formats

- Filters will affect all Exported Reports
- **Summary Report** Exported as Text File and
- **Summary Report** It is a summary of all information And the `Max_Line` parameter value is effective in it
- Other Report Exported as `CSV` and the value of the `Max_Line` parameter does not affect it, and all information is stored in the file 
