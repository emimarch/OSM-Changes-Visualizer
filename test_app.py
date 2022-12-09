from dash import Dash, dcc, html, Input, Output
import os
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import geopandas as gpd
import json
import shapely
from shapely.geometry import Point, Polygon

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets) #external_stylesheets=external_stylesheets)

all_options = {
    'Bolivia': [-90, 90, -180, 180], 
    #'GCC-States': [-90, 90, -180, 180], 
    'Philippines': [-90, 90, -180, 180], 
    'Ghana': [-90, 90, -180, 180], 
    #'Italy Nord': [-90, 90, -180, 180], 
    #'Germany':[-90, 90, -180, 180]

    #'Philippines': [50, 100, 10, 20]

}
app.layout = html.Div([
    html.H4('Animated OSM road network changes'),
    html.P("Select a country:"),
    dcc.RadioItems(
        list(all_options.keys()),
        'Bolivia',
        id='country',
    ),

    html.Hr(),

    
    html.Label('Centroid latitude: '),
    #dcc.Input(id = 'lat_input', min = 0, type='number', required=True, debounce = True),
    dcc.Input(id = 'lat_input', type = 'number', required=True, debounce = True),
    html.Br(),
    html.Label('Centroid longitude: '),
    dcc.Input(id = 'lon_input', type='number', required=True, debounce = True),

    html.Hr(),
    #html.Button(id='submit-button-state', n_clicks=0, children='Submit'),
    html.Div(id='display-selected-values'),
    dcc.Graph(
        id='network_graph')

    ])


@app.callback(
    [Output('lat_input', 'min'), Output('lat_input', 'max')],
    Input('country', 'value'))
def set_lat_options(selected_country):
    minx = all_options[selected_country][0]
    maxx= all_options[selected_country][1]
    #return {'min': minx, 'max': maxx}
    return minx, maxx

@app.callback(
    [Output('lon_input', 'min'), Output('lon_input', 'max')],
    Input('country', 'value'))
def set_lon_options(selected_country):
    miny = all_options[selected_country][2]
    maxy= all_options[selected_country][3]
    return miny, maxy


#@app.callback(
    #Output('cities-radio', 'value'),
    #Input('cities-radio', 'options'))
#def set_cities_value(available_options):
    #return available_options[0]['value']


@app.callback(
    Output('display-selected-values', 'children'),
    Input('lon_input', 'value'),
    Input('lat_input', 'value'),
    Input('country', 'value'))
def set_display_children(lon, lat, country):
    return u'You selected {} with latitude {} and longitude {}!\nPlease be patient while the network loads :)'.format(
        country, lat, lon
    )


@app.callback(
    Output('network_graph', 'figure'),
    Input('lon_input', 'value'),
    Input('lat_input', 'value'),
    Input('country', 'value'))

def draw_graph(lon, lat, country): 

    rectangle = prep_data(lon, lat, country)
    df2014 = gpd.read_file('yearly/2014.geojson')[['amenity', 'name', 'geometry']]
    df2015 = gpd.read_file('yearly/2015.geojson')[['amenity', 'name', 'geometry']]
    df2016 = gpd.read_file('yearly/2016.geojson')[['amenity', 'name', 'geometry']]
    df2017 = gpd.read_file('yearly/2017.geojson')[['amenity', 'name', 'geometry']]
    df2018 = gpd.read_file('yearly/2018.geojson')[['amenity', 'name', 'geometry']]
    df2019 = gpd.read_file('yearly/2019.geojson')[['amenity', 'name', 'geometry']]
    df2020 = gpd.read_file('yearly/2020.geojson')[['amenity', 'name', 'geometry']]
    df2021 = gpd.read_file('yearly/2021.geojson')[['amenity', 'name', 'geometry']]
    df2022 = gpd.read_file('yearly/2022.geojson')[['amenity', 'name', 'geometry']]

    y14, x14 = lat_lon_names(df2014)
    y15, x15 = lat_lon_names(df2015)
    y16, x16 = lat_lon_names(df2016)
    y17, x17 = lat_lon_names(df2017)
    y18, x18 = lat_lon_names(df2018)
    y19, x19 = lat_lon_names(df2019)
    y20, x20 = lat_lon_names(df2020)
    y21, x21 = lat_lon_names(df2021)
    y22, x22 = lat_lon_names(df2022)

    dfs = [df2014, df2015, df2016, df2017, df2018, df2019, df2020, df2021, df2022]
    s_lons = [get_amenities(df)['s_lons'] for df in dfs]
    s_lats = [get_amenities(df)['s_lats'] for df in dfs]
    s_names = [get_amenities(df)['s_names'] for df in dfs]
    h_lons = [get_amenities(df)['h_lons'] for df in dfs]
    h_lats = [get_amenities(df)['h_lats'] for df in dfs]
    h_names = [get_amenities(df)['h_names'] for df in dfs]
    r_lons = [get_amenities(df)['r_lons'] for df in dfs]
    r_lats = [get_amenities(df)['r_lats'] for df in dfs]
    r_names = [get_amenities(df)['r_names'] for df in dfs]

    bounds = rectangle.bounds
    xm = bounds[0]
    xM = bounds[2]
    ym = bounds[1]
    yM = bounds[3]

    lats = [y14, y15, y16, y17, y18, y19, y20, y21, y22]
    lons = [x14, x15, x16, x17, x18, x19, x20, x21, x22]
    N = 9

    x = np.linspace(xm,xM, num=300)
    y = np.linspace(ym,yM, num=300)


    update_menus = [
        {
            "buttons": [
                {
                    "args": [None, {"frame": {"duration": 1000, "redraw": False},
                                    "fromcurrent": True, "transition": {"duration": 1,
                                                                        "easing": "quadratic-in-out"}}],
                    "label": "Play",
                    "method": "animate"
                },
                {
                    "args": [[None], {"frame": {"duration": 0, "redraw": False},
                                    "mode": "immediate",
                                    "transition": {"duration": 0}}],
                    "label": "Pause",
                    "method": "animate"
                }
            ],
            "direction": "left",
            "pad": {"r": 10, "t": 87},
            "showactive": False,
            "type": "buttons",
            "x": 0.1,
            "xanchor": "right",
            "y": 0,
            "yanchor": "top"
        }
    ]


    sliders_dict = {
        "active": 0,
        "yanchor": "top",
        "xanchor": "left",
        "currentvalue": {
            "font": {"size": 20},
            "prefix": "Year:",
            "visible": True,
            "xanchor": "right"
        },
        "transition": {"duration": 1, "easing": "cubic-in-out"},
        "pad": {"b": 10, "t": 50},
        #"len": 0.9,
        "len": 0.9,
        "x": 0.1,
        "y": 0,
        "steps": []
    }

    for i in range(N):
        year = 2014 + i
        slider_step = {"args": [
            [year],
            {"frame": {"duration": 1000, "redraw": False},
            "mode": "immediate",
            "transition": {"duration": 0}}
        ],
            "label": year,
            "method": "animate"}

        sliders_dict["steps"].append(slider_step)

    frames = []
    for k in range(N):
        year = str(2014 + k)
        frame = {"data": [], "name":year}
        
        school_dict = {
            "x": s_lons[k],
            "y": s_lats[k],
            "mode": "markers",
            #"text": list(dataset_by_year_and_cont["country"]),
            "text": s_names[k],
            "marker": dict(color ="red"),
            "name": "Schools"
        }
        
        hospital_dict = {
            "x": h_lons[k],
            "y": h_lats[k],
            "mode": "markers",
            #"text": list(dataset_by_year_and_cont["country"]),
            "text": h_names[k],
            "marker": dict(color ="blue"),
            "name": "Hospitals"
        }


        restaurant_dict = {
            "x": r_lons[k],
            "y": r_lats[k],
            "mode": "markers",
            #"text": list(dataset_by_year_and_cont["country"]),
            "text": r_names[k],
            "marker": dict(color ="yellow"),
            "name": "Restaurants"
        }

        network_dict = {
            "x": lons[k],
            "y": lats[k],
            "mode": "lines",
            "line":dict(color="black"),
            "name": 'Network'
        }
        frame["data"].append(network_dict)
        frame["data"].append(school_dict)
        frame["data"].append(hospital_dict)
        frame["data"].append(restaurant_dict)

        frames.append(frame)

    data = []

    data_hospital = {
            "x": x,
            "y": y,
            "mode": "markers",
            #"text": list(dataset_by_year_and_cont["country"]),
            "marker": dict(color ="blue", size = 3, line = dict(color = 'black', width = 0.5)),
            "name": "Hospitals"}
    data_school = {
            "x": x,
            "y": y,
            "mode": "markers",
            #"text": list(dataset_by_year_and_cont["country"]),
            "marker": dict(color ="red", size = 3, line = dict(color = 'black', width = 0.5)),
            "name": "Schools"
        }

    data_restaurant = {
            "x": x,
            "y": y,
            "mode": "markers",
            #"text": list(dataset_by_year_and_cont["country"]),
            "marker": dict(color ="yellow", size = 3, line = dict(color = 'black', width = 0.5)),
            "name": "Restaurants"
        }

    data_network = {
            "x": x,
            "y": y,
            "mode": "lines",
            "line":dict(color="black", width = 1),
            "name": 'Network'
        }
    data.append(data_network)
    data.append(data_school)
    data.append(data_hospital)
    data.append(data_restaurant)








    fig = go.Figure(
        data= data,

        layout=go.Layout(width=600, height=650,
                        xaxis=dict(range=[xm, xM], autorange=False, zeroline=False, title = "Longitude"),
                        yaxis=dict(range=[ym, yM], autorange=False, zeroline=False, title = "Latitude"),
                        title="OSM Network",
                        hovermode="closest",
                        updatemenus= update_menus,
                        sliders = [sliders_dict]),
        frames = frames)

    return fig
    



def prep_data(lon, lat, country):
    lat = lat
    lon = lon
    dict = {'Bolivia': 'bolivia-internal', 'Philippines': 'philippines-internal', 'Ghana':'ghana-internal', 'GCC-States':'gcc-states-internal', 'Italy Nord': 'nord-ovest-internal', 'Germany': 'bayern-internal'}
    filename = dict[country]
    return cut_polygon(lat, lon, filename)


def cut_polygon(lat, lon, filename):
    center = Point((lon, lat))
    eps_degrees = "epsg:4326"
    gpf = gpd.GeoDataFrame([[center]], columns = ['geometry'])
    gpf.crs = eps_degrees
    eps_meters = "epsg:3857"
    d = 2000 # 2 km radius
    gpf = gpf.to_crs(eps_meters)
    gpf['geometry'] = gpf.geometry.buffer(d)
    gpf = gpf.to_crs(eps_degrees)
    gpf['geometry'] = gpf.geometry[0].envelope # rectangle
    gpf = gpf.to_crs(eps_degrees)

    rectangle = gpf.geometry[0]
    #print(gpf.geometry[0])

    gpf.to_file('boundary/geojson_boundary.geojson', driver = 'GeoJSON') # saving geojson

    osmium_cut(filename)
    osmium_timeseries()
    return rectangle




def osmium_cut(filename):
    filename = filename
    os.system('osmium extract --polygon boundary/geojson_boundary.geojson -H data/{}.osh.pbf -o output_hist/output.osh.pbf --overwrite'.format(filename))
    #os.system('osmium tags-filter output_hist/output.osh.pbf -t nw/highway a/building n/amenity n/public_transport -o output_hist/filtered_output.osh.pbf -O')

def osmium_timeseries():
    for i in range(2014, 2023):
        os.system('osmium time-filter output_hist/output.osh.pbf {}-01-01T00:00:00Z -o yearly/{}.pbf --overwrite'.format(str(i), str(i)))
        #os.system('osmium tags-filter yearly/{}.osm nw/highway a/building n/amenity n/public_transport -o yearly/{}.pbf --overwrite'.format(str(i), str(i)))
        os.system('osmium export yearly/{}.pbf -o yearly/{}.geojson --overwrite'.format(str(i), str(i)))

def lat_lon_names(gpdf):
    gpdf = gpdf[gpdf.geometry.type.eq('LineString')|gpdf.geometry.type.eq('MultiLineString')]
    gpdf = gpdf.explode()
    gpdf['x'] = gpdf.geometry.apply(lambda item: item.xy[0])
    gpdf['y'] = gpdf.geometry.apply(lambda item: item.xy[1])
    gpdf['y_none'] = gpdf.y.apply(lambda x: list(np.append(x, None)))
    gpdf['x_none'] = gpdf.x.apply(lambda x: list(np.append(x, None)))
    lons = np.concatenate(gpdf.x_none.values)
    lats = np.concatenate(gpdf.y_none.values)
    return lats, lons


def get_amenities(df):
    df = df[df['amenity'].notna()]
    df = df.explode()
    # Transform polygons to centroid point
    df['geometry'] = df.geometry.apply(lambda x: x.centroid if x.type=='Polygon' else x)
    #print(df.geometry.type.value_counts())
    # Take first coordinate point for linestring or multilinestrings as the amenity coordinate
    df['geometry'] = df.geometry.apply(lambda x: shapely.geometry.Point(x.coords[0]) if x.type!='Point' else x)
    df['x'] = df.geometry.x
    df['y'] = df.geometry.y
    schools = df[df['amenity']=='school']
    hospitals = df[df['amenity'] == 'hospital']
    restaurants = df[df['amenity'] == 'restaurant']
    dfs = [schools, hospitals, restaurants]
    names = ['s', 'h', 'r']
    lons_lats_names = {}


    for df, name in zip(dfs, names):
        df['y_none'] = df.y.apply(lambda x: list(np.append(x, None)))
        df['x_none'] = df.x.apply(lambda x: list(np.append(x, None)))
        df['name_none'] = df.apply(lambda row: np.array(row['name']), axis=1)
        df['name_none'] = df.name.apply(lambda x: list(np.append(x, None)))
        lons = np.concatenate(df.x_none.values)
        lats = np.concatenate(df.y_none.values)
        names = np.concatenate(df.name_none.values)
        lons_lats_names[str(name + '_lats')] = lats
        lons_lats_names[str(name + '_lons')] = lons
        lons_lats_names[str(name) + '_names'] = names


    return lons_lats_names

if __name__ == '__main__':
    app.run_server(debug=True)