import geoip2.database

def get_ip_location_local(ip_address, db_path):
    try:
        # Load the GeoLite2 City database
        with geoip2.database.Reader(db_path) as reader:
            response = reader.city(ip_address)
            
            # Extract location information
            location_data = {
                "IP": ip_address,
                "Country": response.country.name,
                "Region": response.subdivisions.most_specific.name,
                "City": response.city.name,
                "Latitude": response.location.latitude,
                "Longitude": response.location.longitude,
                "Time Zone": response.location.time_zone
            }
            return location_data
    except Exception as e:
        return {"Error": str(e)}

# Example usage
db_path = "/home/beigi/myApp/ParsingNginxLogs/geoLocation/GeoLite2-City_20241126/GeoLite2-City.mmdb"  # Replace with your actual path
ip = "8.8.8.8"  # Replace with the IP address you want to check
location = get_ip_location_local(ip, db_path)
print(location)


