# github-captoneproject
 
## 'Target Weather Stations for Yield Gap Analysis' geoprocessing tool within ArcGIS Pro

This tool is designed for obtaining the target weather stations with their respective buffers required for conducting a yield gap analysis under the Yield Gap Atlas protocol. The output of this tool can be used to asses how much of the crop planted area on a given country is covered by ground weather stations observations. Furthermore the output of this tool lists the weather stations that require quality control for further use on yield gap analysis. 

Any issues with this tool can be addressed to Nicolas Giordano in ngiordano@ksu.edu

### Required parameters: 
1. Output Directory (Geodatabase). User-defined goedatabase where the output features will be stored. 
2. Political Country Boundaries (Polygon Feature Class). Feature class containing countries political boundaries. This feature class can be downloaded from Yield Gap Atlas website (e.g.: 'Countries').
3. Climate Zones (Polygon Feature Class). Feature class containing world climate zones. This feature class can be downloaded from Yield Gap Atlas website (e.g.: ClimateZones).
4. Crops Area Planted (Standalone Table). Standalone table containing crops area planted and the corresponded 'xy' reference. This file can be obtained from the yield gap atlas website. (e.g.: AreaPlanted)
5. Weather Stations (Point Feature Class). Point feature class containing location of weather stations within a given weather station network. This file should be obtained for each country (e.g.: WeatherStations).
6. Target Percentage Area Planted (float). Numeric value specifying the total crop area planted on a given country will be clipped to a given percentage area planted defined by the user. Default is to 70 (%). 
7. Selected Country (string). Desired country where the yield gap analysis will be conducted. Default is to 'Argentina'.
8. Crop (string). Desired crop used in the yield gap analysis. Default is to 'Wheat'.

## Procedures

Below I explain step by step procedures performed by the tool:

- Step 1: Define output file names.
- Step 2: Select target country and filter rows of the selected country. Save output to memory. 
- Step 3: Select crop area planted based on target country. 
- Step 4: Filter total crop planted area to desired percentage of planted crop planted area specified by the user. 
- Step 5: Select the target climate zones and save climate zones selected output to memory.
- Step 6: Generate weather stations buffers and clip buffers based on climate zone in which the weather station is located.
- Step 7: Delete unnecesary temporary files.

## Output


There are 4 output feature class generated after running the tool:

1. Feature class containing the selected country boundaries (e.g.: 'Argentina_Boundaries').
2. Feature class containing the climate zones that cover the desired percentage of the crop planted area (e.g.: 'Argentina_Wheat_Area_Climate_Zones').
3. Feature class containing the crop planted area (e.g.: 'Argentina_Wheat_Planted_Area').
4. Feature class containing the weather stations buffered area (e.g.: 'Argentina_Wheat_Area_Weather_Stations_Buffered').


All output files receive specific names based on the selected parameters by the user. 
