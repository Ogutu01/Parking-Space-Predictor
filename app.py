import streamlit as st
import pandas as pd
import pydeck as pdk
import pickle
import folium

# MAPBOX_STYLE = "mapbox://styles/mmm97/cl2m0aoax00a214kszmx0eefu"
MAPBOX_STYLE = "mapbox://styles/mapbox/streets-v12"

# Mock car park data
car_parks_data = {
    "CarParkName": ["Warriewood Car Park", "Narrabeen Car Park", "Mona Vale Car Park", "Dee Why Car Park", "West Ryde Car Park", "Sutherland East Parade Car Park", "Leppington Car Park", "Edmondson Park South Car Park", "St Marys Car Park", "Campbelltown Farrow Rd North Car Park", "Campbelltown Hurley Street South Car Park", "Penrith Combewood At-Grade Car Park", "Penrith Combewood Multi-Level Car Park", "Warwick Farm Car Park", "Schofields Car Park", "Hornsby Jersey St Car Park", "Tallawong P1 Car Park", "Tallawong P2 Car Park", "Tallawong P3 Car Park", "Kellyville North Car Park", "Kellyville South Car Park", "Bella Vista Car Park", "Hills Showground Car Park", "Cherrybrook Car Park", "Gordon Henry St North Car Park", "Kiama Car Park", "Gosford Car Park", "Revesby Car Park"],
    "latitude": [151.300667, 151.297315, 151.305146, 151.286485, 151.090229, 151.05719, 150.8081, 150.8587, 150.776029, 150.813929, 150.813929, 150.696135, 150.696135, 150.935036, 150.873817, 151.098494, 150.906022, 150.906022, 150.906022, 150.935304, 150.935304, 150.944024, 150.987345, 151.031977, 151.154528, 150.854695, 151.341711, 151.014838],
    "longitude": [-33.697777, -33.713514, -33.677276, -33.752797, -33.807172, -34.031787, -33.9544, -33.9693, -33.762256, -34.063835, -34.063835, -33.750055, -33.750055, -33.91345, -33.704477, -33.702801, -33.69163, -33.69163, -33.69163, -33.713514, -33.713514, -33.730592, -33.72782, -33.736703, -33.756009, -34.672518, -33.423883, -33.95246]
}

# Including spot data
spots_data = {
    "facility_name": ["Tallawong Station Car Park", "Warriewood Car Park", "Narrabeen Car Park", "Mona Vale Car Park", "Dee Why Car Park", "West Ryde Car Park", "Sutherland East Parade Car Park", "Leppington Car Park", "Edmondson Park South Car Park", "St Marys Car Park", "Campbelltown Farrow Rd North Car Park", "Kellyville Station Car Park", "Campbelltown Hurley Street South Car Park", "Penrith Combewood At-Grade Car Park", "Penrith Combewood Multi-Level Car Park", "Warwick Farm Car Park", "Schofields Car Park", "Hornsby Jersey St Car Park", "Tallawong P1 Car Park", "Tallawong P2 Car Park", "Tallawong P3 Car Park", "Kellyville North Car Park", "Bella Vista Station Car Park", "Kellyville South Car Park", "Bella Vista Car Park", "Hills Showground Car Park", "Cherrybrook Car Park", "Hills Showground Station Car Park", "Ashfield Car Park", "Kogarah Car Park", "Seven Hills Car Park", "Manly Vale Car Park", "Brookvale Car Park", "Cherrybrook Station Car Park", "Gordon Henry St North Car Park", "Kiama Car Park", "Gosford Car Park", "Revesby Car Park"],
    "spots": [1004, 244, 46, 68, 117, 151, 373, 1884, 1429, 682, 68, 1374, 118, 230, 1144, 910, 700, 145, 121, 455, 397, 351, 800, 964, 777, 584, 384, 600, 228, 259, 1613, 142, 246, 400, 213, 42, 1057, 934]
}

car_parks_data['latitude'] = [round(lat, 3) for lat in car_parks_data['latitude']]
car_parks_data['longitude'] = [round(lon, 3) for lon in car_parks_data['longitude']]

df_spots = pd.DataFrame(spots_data)
df_carparks = pd.DataFrame(car_parks_data)

# Specifying custom map theme
map_layer = pdk.Deck(
  map_style=MAPBOX_STYLE,
  initial_view_state=pdk.ViewState(latitude=-33.8, longitude=151.07, zoom=10.2, bearing=0, pitch=0),
  layers=[])

# Display car park locations on a map
main_map = st.pydeck_chart(map_layer)

st.divider()

# Streamlit app
st.sidebar.title("Car Park Finder")
st.sidebar.write("""
    Welcome to the Car Park Finder app. 
    Select a future date and click on 'Process Data' to find available car parks and the likelihood of finding a parking spot.
""")

# Carpark
selected_carpark = st.sidebar.selectbox("Select Car Park", df_carparks['CarParkName'])

# Date picker
input_date = st.sidebar.date_input('Select a date:', pd.to_datetime('today'))

# Button to process data
if st.sidebar.button("Process Data"):
    model_path = f"./model/{selected_carpark}.pkl"
    
    # Loading model
    with open(model_path, 'rb') as f:
        forecast_model = pickle.load(f)
    # Combine date and time into a single datetime object
    input_datetime = pd.to_datetime(str(input_date) + ' ' + str(pd.to_datetime("00:00:00").time()))

    # Display predictions for each facility
    st.header('Predictions:')
    result = forecast_model.loc[forecast_model['ds_forecast'] == input_datetime]
    
    # Necessary dataframes
    df_carpark_result = df_carparks[df_carparks['CarParkName'] == selected_carpark]
    df_spots_result = df_spots[df_spots['facility_name'] == selected_carpark]
    
    # Display predictions
    aval = round(result[f'yhat_{selected_carpark}'],0)
    total = df_spots_result['spots'].iloc[0]
    occupancy = total-aval
    
    
    col1,col2 = st.columns(2)
    
    col1.metric("Number of parking spots available",round(result[f'yhat_{selected_carpark}'],0))
    col1.metric("Total Parking Spots in Parking Lot",df_spots_result['spots'].iloc[0])
    
    col2.metric("Occupancy",occupancy)
    # col2.metric("Likelihood?",likelihood)
    # Refreshing map
    
    layer_2 = pdk.Layer(
        "ScatterplotLayer",
        data=df_carpark_result,
        get_position=["longitude", "latitude"],
        auto_highlight=True,
        get_radius=100,
        get_fill_color=[255, 0, 0],
        pickable=True,
    )
    
    map_deck_2 = pdk.Deck(
        map_style=MAPBOX_STYLE,
        initial_view_state=pdk.ViewState(
            latitude=df_carpark_result["latitude"].iloc[0],
            longitude=df_carpark_result["longitude"].iloc[0],
            zoom=10.2,
            bearing=0,
            pitch=0),
        layers=[layer_2])
    st.balloons()
    
    # Update main_map with the new map layer
    main_map.pydeck_chart(map_deck_2)

