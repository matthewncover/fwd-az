# data manipulation imports
import numpy as np, pandas as pd
import re

# geojson imports
import json

# web scraping imports
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager


# local imports
from maps_section_search import MapsSectionSearch
from state_search_path import PathSearch

class StateSearch:

    ZOOM_FACTOR = 15
    # LONLAT_DELTA = 0.0307
    LONLAT_DELTA = 0.1

    def __init__(self, state_name = "Arizona", use_existing_data=True, custom_grid_path=False):

        self.use_existing_data = use_existing_data
        self.state_name = state_name

        self.get_state_abr()
        self.read_geojson()

        self.init_lon_lat()
        self.init_webdriver()

        if custom_grid_path:
            self.init_custom_grid_path()
        else:
            self.init_grid_path()


    def get_state_abr(self):

        state_abr_dict = {
            "Arizona": "AZ"
        }

        self.state_abr = state_abr_dict[self.state_name]


    def read_geojson(self):
        """read in polygon coordinates
        """

        try:
            state_geojsons = json.load(open("./us-state-boundaries.json"))
        except FileNotFoundError:
            state_geojsons = json.load(open("./google-maps-search/us-state-boundaries.json"))

        state_geojson = [
            x for x in state_geojsons
            if x["fields"]["name"] == self.state_name
        ][0]

        geojson_data = state_geojson["fields"]
        self.center_lat, self.center_lon = geojson_data["centlat"], geojson_data["centlon"]
        
        # (longitude, latitude)
        self.state_boundary = np.array(
            geojson_data["st_asgeojson"]["coordinates"][0]
        )

    def init_webdriver(self):
        """initialize headless chrome webdriver
        """

        browser_options = webdriver.ChromeOptions()
        browser_options.add_argument("headless")

        # self.driver = webdriver.Chrome(
        #     executable_path="C:\chromedriver_win32\chromedriver.exe",
        #     options=browser_options
        # )

        self.driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()),
            options=browser_options
            )


    def create_maps_url(self, search_term, lon, lat):
        """google maps url

        Parameters:
            search_term (str): single term to search google maps
            lat (float): latitude center of search
            lon (float): longitude center of search

        Returns:
            (str): google maps url
        """

        # warning: not tested for more 2+ terms in search_term
        
        url = f"https://www.google.com/maps/search/{search_term}/@{lat},{lon},{self.ZOOM_FACTOR}z"

        return url

    def init_lon_lat(self):
        """start grid search at most north-east point
        for AZ, this is the four corners monument
        """

        lon_lat_sum = self.state_boundary[:, 0] + self.state_boundary[:, 1]

        north_east_ind = np.where(
            lon_lat_sum == lon_lat_sum.max()
        )

        self.lon0, self.lat0 = self.state_boundary[north_east_ind][0]

    def search_one_section(self, search_term, lon, lat):
        """make url, initiate maps search centered at lat and lon for search_term
        """

        url = self.create_maps_url(search_term, lon, lat)

        search_results = MapsSectionSearch(self.driver, self.state_abr, url, self.df)

        return search_results

    def business_search(self, search_term):

        search_term = search_term.replace(" ", "+")

        if self.use_existing_data:
            self.read_df(search_term)
        else:
            self.init_df()

        for lon, lat in self.search_centers:
            print(round(lon, 4), round(lat, 4))
            search_results = self.search_one_section(search_term, lon, lat)

            if search_results.businesses:
                print("New Businesses")
                print([x.business_name for x in search_results.businesses])
                self.add_business_data(search_results.businesses)

        self.save_data(search_term)

    def search_filename(self, search_term):

        return f"{self.state_abr}_{search_term}.csv"

    def read_df(self, search_term):

        filename = self.search_filename(search_term)
        self.df = pd.read_csv(filename)

    def save_data(self, search_term):

        filename = self.search_filename(search_term)
        self.df.to_csv(filename, index=False)


    def init_df(self):

        self.df = pd.DataFrame(columns=["business_name", "href_url"])

    def add_business_data(self, businesses):

        expected_attrs = businesses[0].single_data_attrs.keys()

        for business in businesses:
            for attr in expected_attrs:
                if attr not in business.single_data_attrs.keys():
                    business.single_data_attrs[attr] = np.nan


        new_data = pd.DataFrame({
            attr: [
                business.single_data_attrs[attr]
                for business in businesses
            ]
            for attr in businesses[0].single_data_attrs.keys()
        })

        self.df = pd.concat([self.df, new_data]).reset_index(drop=True)

    def init_grid_path(self):

        self.search_centers = (
            PathSearch(
                self.state_boundary, 
                self.lon0, self.lat0, 
                self.LONLAT_DELTA
                ).find_path()
            )

    def init_custom_grid_path(self):

        self.search_centers = (
            PathSearch(
                self.state_boundary,
                self.lon0, self.lat0,
                LONLAT_DELTA=0.03
            ).create_custom_grid_path()
        )


if __name__ == "__main__":

    x = StateSearch(use_existing_data=False, custom_grid_path=False)

    search_terms = [
        # "church", "temple", "house of worship",
        # "park", "whole foods", "sprouts",
        # "community center", "public library",
        # "bookstore", "farmers market", "high end coffee shop",
        # "yoga studio", "coworking space", "food co-op",
        # "post office", "dispensary",
        "trailhead"
        ]
    for search_term in search_terms:
        print(search_term)
        search_results = x.business_search(search_term)

    print("done")