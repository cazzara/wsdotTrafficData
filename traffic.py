import requests
import gmplot
import json
import argparse


"""
Author : Chris Azzara
Purpose : This commandline script plots real-time traffic conditions along I-5 and I-90. The information is gathered from the WSDOT traffic API
          which is updated every 90 secs in most cases. For more info on the API visit:
          http://wsdot.com/traffic/api/Documentation/class_traffic_flow.html
          Each traffic monitoring station is then plotted based on its lat/long coordinates on a Google maps overlay using the gmplot module
          and is colorized based on the serverity of the traffic.
          The result is output in an HTML file in the current working directory
"""

## Use the argparse module to take in user input
# Home -- plots Westbound I-90 and Northbound I-5
# Work -- plots Eastbound I-90 and Southbound I-5
def parseArgs(): 
    parser = argparse.ArgumentParser(prog="trafficPlot", description="Plot traffic data on Google maps to get up-to-date travel info")
    parser.add_argument("--direction", help="Choose either home or work", choices=['home', 'work'], required=True)
    args = parser.parse_args()
    return args

def getTrafficFlowData():
    ## This is the end point we will be hitting on WSDOT's API
    API_KEY = "0f65f85d-ae8f-4be7-bdd8-8d0a9b98c77f"
    url_base = "http://wsdot.com/Traffic/api/TrafficFlow/TrafficFlowREST.svc/"
    get_flows = "GetTrafficFlowsAsJson?AccessCode={}"
    
    # http://wsdot.com/Traffic/api/TrafficFlow/TrafficFlowREST.svc/etTrafficFlowsAsJson?AccessCode=0f65f85d-ae8f-4be7-bdd8-8d0a9b98c77f
    url = url_base + get_flows.format(API_KEY)
    
    print("Gathering traffic station data...")
    resp = requests.get(url)
    flowData = json.loads(resp.text)
    """
    {
    Variable flowData contains a list of stations in the following format:
    
       'FlowDataID':2482,
       'FlowReadingValue':1,  <----------- This will be a value 1-4 which describes the severity of the traffic 
       'FlowStationLocation':{
          'Description':'Homeacres Rd',
          'Direction':'EB',
          'Latitude':47.978415632,    <--|----------- Lat and long coordinates, self explanitory 
          'Longitude':-122.174701738, <--|
          'MilePost':0.68,
          'RoadName':'002' <-------------- This identifies the road we're looking for (I-5 or I-90 in this case)
       },
       'Region':'Northwest', <------------- We're only concerned with stations in the Northwest Region
       'StationName':'002es00068',
       'Time':'/Date(1527543562000-0700)/'
    }
    
    """
    print("{} total stations found".format(len(flowData)))
    return flowData




## Iterate through the list of flow stations and sort them out by region
# If the region is Northwest, further divide them by road and direction 
# After the for loop terminates, we will have a list of traffic stations for I-90 and I-5 in the home or work direction

def getDataStations(direction):    
    north, south, east, olympic = [], [], [], []
    i5, i90 = [], []
    for sta in flowData:
        if sta['Region'] == "Northwest":
            north.append(sta)
            if sta['FlowStationLocation']['RoadName'] == "005":
                if direction == "home" and sta['FlowStationLocation']['Direction'] == "NB":
                    i5.append(sta) 
                elif direction == "work" and sta['FlowStationLocation']['Direction'] == "SB":
                    i5.append(sta)
            elif sta['FlowStationLocation']['RoadName'] == "090":
                if direction == "home" and sta['FlowStationLocation']['Direction'] == "WB":
                    i90.append(sta)
                elif direction == "work" and sta['FlowStationLocation']['Direction'] == "EB":
                    i90.append(sta)
        elif sta['Region'] == "Southwest":
            south.append(sta)
        elif sta['Region'] == "Eastern":
            east.append(sta)
        elif sta["Region"] == "Olympic":
            olympic.append(sta)
        else:
            print("Unknown Station: ", sta)
    
    print("Northwest: {} Southwest: {} Eastern: {} Olympic: {}".format(len(north), len(south), len(east), len(olympic)))
    return [i5, i90]



def getLatLong(sta):
    return sta['FlowStationLocation']['Latitude'], sta['FlowStationLocation']['Longitude']

#def plotRoute(roads, gmap):
#    for road in roads:
#        lats, longs = [], []
#        for sta in road:
#            lat, lon = getLatLong(sta)
#            flow = sta['FlowReadingValue']
#            if flow == 1: # Light Traffic
#                gmap.scatter([lat], [lon], 'cornflowerblue', size=60, marker=False)    
#            elif flow == 2: # Moderate Traffic
#                gmap.scatter([lat], [lon], 'orange', size=60, marker=False)    
#            elif flow == 3: # Heavy Traffic
#                gmap.scatter([lat], [lon], 'red', size=60, marker=False)   
#            elif flow == 4: # Stop and Go Traffic 
#                gmap.scatter([lat], [lon], 'black', size=60, marker=False)
#            lats.append(lat)
#            longs.append(lon)
#        gmap.plot(lats, longs, 'white', edge_width=10)


def plotRoute(roads, gmap):
    for road in roads:
        i = 0
        last = len(road) - 1
        while i < last:
            sta_lat, sta_long = getLatLong(road[i])
            next_sta_lat, next_sta_long = getLatLong(road[i+1])
            lats = [sta_lat, next_sta_lat]
            longs = [sta_long, next_sta_long]
            trafficFlow = road[i]['FlowReadingValue']
            if trafficFlow == 1:
               # gmap.scatter([lats[0]], [longs[0]], 'cornflowerblue', size=60, marker=False)
                gmap.plot(lats, longs, 'cornflowerblue', edge_width=10)
            elif trafficFlow == 2:
               # gmap.scatter([lats[0]], [longs[0]], 'orange', size=60, marker=False)
                gmap.plot(lats, longs, 'orange', edge_width=10)
            elif trafficFlow == 3:
                #gmap.scatter([lats[0]], [longs[0]], 'red', size=60, marker=False)
                gmap.plot(lats, longs, 'red', edge_width=10)
            elif trafficFlow == 4:
               # gmap.scatter([lats[0]], [longs[0]], 'black', size=60, marker=False)
                gmap.plot(lats, longs, 'black', edge_width=10)
            i += 1
            
            
            
def writeToMap(gmap):
    gmap.marker(work_loc[0], work_loc[1], title="Work")
    gmap.marker(home_loc[0], home_loc[1], title="Home")
    gmap.draw('wsdotTrafficMap.html')


if __name__ == "__main__":
    args = parseArgs()
    flowData = getTrafficFlowData()
    roads = getDataStations(args.direction)
    print("Generating map data...")
    ## Create a new Google map overlay centered on Seattle, 12 is the zoom level
    gmap = gmplot.GoogleMapPlotter(47.609722, -122.333056, 12)
    # TLG Learning!
    work_loc = (47.582584, -122.168620)
    # U-District!
    home_loc = (47.660399, -122.320479)
    
    if args.direction == "home":
        print("[+] Selected route HOME")
        print("Plotting Westbound Stations on I-90")
        print("Plotting Northbound Stations on I-5")
    else:
        print("[+] Selected route WORK")
        print("Plotting Eastbound Stations on I-90")
        print("Plotting Southbound Stations on I-5")
    
    plotRoute(roads, gmap)
    writeToMap(gmap)


