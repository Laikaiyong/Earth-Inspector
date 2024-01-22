import math as m
import datetime
import requests
import csv
from io import BytesIO

from PIL import Image

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import astropy.coordinates as coord
import astropy.units as u
from astropy.io import ascii
from astropy.coordinates import SkyCoord

from shapely.geometry import Point, Polygon
import geopandas as gpd
import pandas as pd
import geopy
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

import streamlit as st

API_KEY = st.secrets["nasa"]["api"]

# API fetching and data processing
def fetch_natural_earth(date):
    api_path = f'https://api.nasa.gov/EPIC/api/natural/date/{date}?api_key={API_KEY}'
    print(f"Fetching {api_path}")
    response = requests.get(api_path)
    
    data = response.json()
    image = fetch_earth_image(date, data[0]["image"])
    
    return (
        image,
        data[0]
    )

def fetch_earth_image(date, indicator):
    api_path = f'https://api.nasa.gov/EPIC/archive/natural/{date.year}/{"0" + str(date.month) if (date.month < 10) else date.month}/{"0" + str(date.day) if (date.day < 10) else date.day}/png/{indicator}.png?api_key={API_KEY}'
    print(f"Fetching {api_path}")
    response = requests.get(api_path)
    
    byteImg = Image.open(BytesIO(response.content))
    print("-----DONE Earth Image-----")
    return byteImg

@st.cache_data
def fetch_satelite_earth(date, lat, lon, dim):
    api_path = f'https://api.nasa.gov/planetary/earth/imagery?lon={lon}&lat={lat}&date={date}&dim={dim}&api_key={API_KEY}'
    print(f"Fetching {api_path}")
    response = requests.get(api_path)
    
    byteImg = Image.open(BytesIO(response.content))
    print("-----DONE Satelite Image-----")
    return byteImg

# UI Stuffs
def create_galactic_plot(lat, lon):
    data = pd.DataFrame({
        "lon": [lon],
        "lat": [lat]
    })

    xarr = np.array(data.iloc[:,0])
    yarr = np.array(data.iloc[:,1])
    eq = SkyCoord(xarr[:], yarr[:], unit=u.deg)
    gal = SkyCoord(xarr[:], yarr[:], frame='galactic', unit=u.deg)

    plt.figure(figsize=(6,5))
    fig = plt.figure()
    ax = fig.add_subplot(111, projection="aitoff")
    plt.plot(gal.l.wrap_at(180*u.deg), gal.b.wrap_at(180*u.deg), linestyle='None')
    ax.scatter(gal.l, gal.b, linestyle='None')

    plt.subplot(111, projection='aitoff')
    plt.grid(True)
    ax.scatter(gal.l.wrap_at('180d').radian, gal.b.radian)

    st.subheader("Galactic coordinate")
    st.pyplot(fig)
    
def earth_data_view(date):
    image, data = fetch_natural_earth(date)
    col1, col2, col3 = st.columns([5, 1, 2])

    col1.image(
        image,
        caption=data["caption"], 
        output_format="PNG"
    )

    for key in [
        "caption",
        "image",
        "coords",
        "attitude_quaternions",
        "sun_j2000_position",
        "lunar_j2000_position",
        "dscovr_j2000_position"
    ]:
        data.pop(key)
    col3.json(data)
    
    create_galactic_plot(
        data["centroid_coordinates"]["lat"],
        data["centroid_coordinates"]["lon"]
    )

def load_view():
    date = st.sidebar.date_input("Date", datetime.date(2018, 1, 1))
    st.sidebar.divider()
    lat = st.sidebar.number_input('Latitude', value=29.78)
    lon = st.sidebar.number_input('Longitude', value=-95.33)
    dim = st.sidebar.number_input('Dimension', value=0.15)
    # street = st.sidebar.text_input("Street", "75 Bay Street")
    # city = st.sidebar.text_input("City", "Toronto")
    # province = st.sidebar.text_input("Province", "Ontario")
    # country = st.sidebar.text_input("Country", "Canada")
        
    st.title("Earth Inspector")
    
    earth_data_view(date)
    st.divider()
    st.image(
        fetch_satelite_earth(date, lat, lon, dim),
        caption=f"Satelite earth image on {str(date)} at [{str(lat)}, {str(lon)}]", 
        output_format="PNG"
    )
    
    
load_view()