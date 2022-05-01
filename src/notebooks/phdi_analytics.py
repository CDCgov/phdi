import csv
import datetime as dt
import os
from pathlib import Path
import random

import censusgeocode as cg
from concurrent.futures import ThreadPoolExecutor
from geopy import Point
from geopy.distance import geodesic
import geopandas as gpd
import matplotlib.ticker as mtick
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy as np
import pandas as pd
import seaborn as sns
from tqdm.notebook import tqdm

NOTEBOOK_PATH = os.path.abspath('')
HOME_DIR = os.path.expanduser('~')
INVENTORY_DIR = os.path.join(HOME_DIR, 'inventory')

# Changing to "hardcode" path based on comment from Bryan
# https://github.com/CDCgov/prime-public-health-data-infrastructure/pull/
# 56#discussion_r847258818
FILE_DIR = Path(__file__).parent.absolute()
OUTPUTS_DIR = os.path.join(FILE_DIR, 'outputs')

# Approximate center of Fairfax County chosen on Google Maps
FAIRFAX_COUNTY_CENTER = Point(38.845262, -77.307035)

# Link to VA CBG Shapefile is here:
# https://data.virginia.gov/Government/2019-Virginia-Census-Block-Groups/
# gtta-aa5t/data
# I downloaded to a local directory called "inventory". You will to do this
# as well for your code to run
VA_CBG_MAP_PATH = os.path.join(
    INVENTORY_DIR,
    '2019 Virginia Census Block Groups',
    'geo_export_64de6806-7ef0-4c39-97f1-b52e5d986702.shp'
)

# Link to download VA Census Tract Shapefile:
# https://catalog.data.gov/dataset/
# tiger-line-shapefile-2018-state-virginia-current-census-tract-state-based
VA_TRACT_MAP_PATH = os.path.join(INVENTORY_DIR, 'tl_2018_51_tract')

FAIRFAX_COUNTY_ZIPS = [
    22003, 22030, 20171, 22015, 20170, 20120, 22033, 22309, 22079,
    22306, 22031, 22042, 22312, 22310, 22153, 22032, 22315, 22152,
    20191, 20121, 22101, 22150, 22041, 22182, 22043, 20151, 22180,
    22102, 22311, 20190, 22124, 22046, 22151, 22039, 22066, 20124,
    22303, 22181, 22308, 22044, 20194, 22307, 22060, 22027, 22185,
    22035, 22081, 22092, 22082, 22095, 22096, 22103, 22107, 22106,
    22109, 22108, 22118, 22116, 22120, 22119, 22122, 22121, 22158,
    22156, 22160, 22159, 22161, 22183, 22184, 22199, 22009, 22037,
    22036, 22047, 22067, 20122, 20153, 20172, 20193, 20192, 20195,
    20196, 20511
]


def geocode(row):
    """
    Placeholder geocoder for now, real data would come geocoded

    Comment for the future -- it would be helpful, in addition,
    to geocoding with SmartyStreets, to also pull in data,
    e.g. socioeconomic data, that can be joined at census geography
    levels (e.g. https://www.neighborhoodatlas.medicine.wisc.edu/
    Area Deprivation Index created at Census Block Group Level)
    """
    index, lat, lng = row
    try:
        census = cg.coordinates(lng, lat)['2020 Census Blocks'][0]

        data = dict(geoid=census['GEOID'],
                    state=census['STATE'],
                    county=census['COUNTY'],
                    tract=census['TRACT'],
                    block=census['BLOCK'],
                    lat=lat,
                    lng=lng)

    except Exception:
        data = dict(lat=lat, lng=lng)

    return data


def generate_point(center: Point, radius: int) -> Point:
    """
    This is from

    https://stackoverflow.com/questions/31192451/
    """
    radius_in_kilometers = radius * 1e-3
    random_distance = random.random() * radius_in_kilometers
    random_bearing = random.random() * 360
    return geodesic(kilometers=random_distance).destination(center, random_bearing)


def write_points(points, filename='synthetic_locations.csv'):
    """
    Output a CSV so that you can upload to Google Maps

    This is to just check the synthetic points
    """
    output_file = os.path.join(OUTPUTS_DIR, filename)
    with open(output_file, 'w', encoding='UTF8', newline="") as f:
        writer = csv.writer(f)
        writer.writerow(['latitude', 'longitude'])
        for p in points:
            writer.writerow([p[0], p[1]])


def generate_random_date(start_date, end_date):
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    random_date = start_date + dt.timedelta(days=random_number_of_days)

    return random_date


def generate_covid_positive(row):
    if row['is_fully_vax'] == 0:
        covid_positive = random.choices([0, 1], weights=(0.97, 0.03), k=1)
        return covid_positive[0]
    else:
        covid_positive = random.choices([0, 1], weights=(0.99, 0.01), k=1)
        return covid_positive[0]


def create_dataframe(radius, number_of_points, center):
    start_date = dt.date(2021, 6, 1)
    end_date = dt.date(2022, 3, 31)

    points = [generate_point(center, radius) for _ in range(number_of_points)]

    # Generating the synthetic data as a dataframe
    latitudes = []
    longitudes = []
    personids = random.sample(range(len(points)), len(points))
    first_names = []
    last_names = []
    addresses = []
    zip_codes = []
    event_dates = []
    for p in points:
        latitudes.append(p[0])
        longitudes.append(p[1])
        # Note, to generate fake names you can use the names library
        # https://pypi.org/project/names/
        # Since we're not actually doing anything with names, we'll just put in
        # test names
        first_names.append('Test First Name')
        last_names.append('Test Last Name')
        addresses.append('Test 123 Street')
        zip_codes.append(random.sample(FAIRFAX_COUNTY_ZIPS, 1)[0])
        event_dates.append(generate_random_date(start_date, end_date))

    df = pd.DataFrame({
        'pprl_generated_id': personids,
        'first_name': first_names,
        'last_name': last_names,
        'street_address': addresses,
        'zip_code': zip_codes,
        'latitude': latitudes,
        'longitude': longitudes,
        'event_dt': event_dates,
    })

    with ThreadPoolExecutor() as tpe:
        data = list(
            tqdm(
                tpe.map(geocode, df[['latitude', 'longitude']].itertuples()),
                total=len(df)
            )
        )
    data_df = pd.DataFrame.from_records(data)

    df['census_tract'] = data_df['state'] + data_df['county'] + data_df['tract']
    df['census_block_group'] = data_df['state'] +\
        data_df['county'] + data_df['tract'] + data_df['block'].str[0]
    df['census_block'] = data_df['geoid']

    is_fully_vax = random.choices([0, 1], weights=(0.4, 0.6), k=len(points))
    df['is_fully_vax'] = is_fully_vax
    df['tested_covid_positive'] = df.apply(
        lambda row: generate_covid_positive(row), 1)
    df['breakthrough_infection'] = df['is_fully_vax'] *\
        df['tested_covid_positive']

    df['event_dt'] = pd.to_datetime(df['event_dt'])

    # Write as Pickle File
    df.to_pickle(os.path.join(OUTPUTS_DIR, 'synthetic_df.pkl'))

    return df


def _aggregate_df(df, window='30D', metric_label='Breakthrough Infection'):
    df.sort_values(by='event_dt', ascending=True, inplace=True)

    if metric_label.lower() == 'breakthrough infection':
        metric = 'breakthrough_infection'

    if metric_label.lower() == 'covid infection':
        metric = 'tested_covid_positive'

    df['rolling_sum'] = df.rolling(window, on='event_dt')[metric].sum()
    df['rolling_count'] = df.rolling(window, on='event_dt')[metric].count()
    df['rolling_rate'] = df['rolling_sum'] / df['rolling_count']

    return df


def plot_time_series_metric(df, window, metric_label):
    """
    Plot a metric as a time series

    Keyword Args:
      - df: Dataframe
      - window: A Python DateOffset Object. Valid values are documented here:
        https://pandas.pydata.org/pandas-docs/stable/user_guide/
        timeseries.html#dateoffset-objects

        For this prototype we are assuming only rolling days ('D').
        However, in theory, we could support multiple rolling time frames
      - metric_label: The label for the metric. Will be used to label
        y-axis
    """
    assert window[-1] in ['D'], 'Enter a time window that is in Days'
    window_length_label = window[:-1]

    df_agg = _aggregate_df(df, window=window, metric_label=metric_label)

    fig, ax_lst = plt.subplots(nrows=1, ncols=1, figsize=(15, 8))

    sns.lineplot(
        data=df_agg,
        x='event_dt',
        y='rolling_rate',
        ax=ax_lst,
        ci=None
    )

    ax_lst.set_ylabel(metric_label, fontsize=14)
    ax_lst.set_xlabel('Date', fontsize=14)

    ax_lst.set_title('{} Rate ({} Day Rolling)'.format(
        metric_label,
        window_length_label
    ), fontsize=22)
    ax_lst.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))

    plt.tight_layout(h_pad=6)

    return fig, ax_lst


def create_map(geography, shapefile_path, metric, df):
    """
    Create spatial analytics map
    """
    shapefile_map = gpd.read_file(shapefile_path)
    shapefile_map.columns = shapefile_map.columns.str.lower()

    fairfax_map = shapefile_map.loc[shapefile_map.countyfp == '059']

    if geography == 'census_block_group':
        geography_label = 'Census Block Groups'
    elif geography == 'census_tract':
        geography_label = 'Census Tracts'

    # Creating a simple breakthrough metric
    df_agg = df.groupby([geography], as_index=False).agg({
        'pprl_generated_id': 'count',
        'is_fully_vax': np.sum,
        'tested_covid_positive': np.sum,
        'breakthrough_infection': np.sum,
    })
    df_agg.rename(
        columns={'pprl_generated_id': 'number_of_people'}, inplace=True)
    df_agg['infection_rate'] =\
        df_agg['tested_covid_positive'] / df_agg['number_of_people']
    df_agg['breakthrough_infection_rate'] =\
        df_agg['breakthrough_infection'] / df_agg['is_fully_vax']

    fairfax_map = fairfax_map.merge(
        right=df_agg[[
            geography, 'infection_rate', 'breakthrough_infection_rate']],
        left_on='geoid',
        right_on=geography,
    )

    fig, ax = plt.subplots(figsize=(10, 10))
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.1)
    fairfax_map.plot(
        ax=ax,
        column='breakthrough_infection_rate',
        cmap='Purples',
        legend=True,
        cax=cax,
        missing_kwds={"color": "lightgrey"},
    )
    fairfax_map.plot(ax=ax, facecolor='none', edgecolor='grey', linewidth=.5)
    ax.set_title('Fairfax County Breakthrough Infection Rate (2020 {})'.format(
        geography_label), fontsize=20)
    fig.patch.set_visible(False)
    ax.axis('off')
    plt.tight_layout()

    return ax
