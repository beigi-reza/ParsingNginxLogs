# Config file

```sh
vim config/config.json
```



### Defualt line

```json
Default value for the number of lines when displaying information
{
    "Max_Line_view" : 60,
}
```
### Export Path 

The path to creating the requested reports and outputs
```json
{
    "ExportPath" : "/var/tmp",
}
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