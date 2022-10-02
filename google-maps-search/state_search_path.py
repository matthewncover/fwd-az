import numpy as np
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

class PathSearch:

    def __init__(self, state_boundary, lon0, lat0, LONLAT_DELTA):

        self.state_boundary = state_boundary
        self.state_polygon = Polygon(self.state_boundary)
        self.lon = lon0
        self.lat = lat0
        self.LONLAT_DELTA = LONLAT_DELTA

    def move_multiplier(self, lon, lat, switched):

        # function of population density
        if switched:
            return 1.5

        else:
            return 1

    def move_center(self, lon, lat, how, switched=False):

        assert how in "nsew"

        multiplier = self.move_multiplier(lon, lat, switched)

        move_dict = {
            "n": [lon, lat + self.LONLAT_DELTA*multiplier],
            "s": [lon, lat - self.LONLAT_DELTA*multiplier],
            "e": [lon + self.LONLAT_DELTA*multiplier, lat],
            "w": [lon - self.LONLAT_DELTA*multiplier, lat]
        }

        return move_dict[how]

    def is_point_in_state(self, lon, lat):
        """check if point is within the boundaries of, or touching
            the state polygon

        Parameters:
            lon (float): longitude of point to check
            lat (float): latitude of point to check

        Returns:
            bool
        """

        point = Point(lon, lat)

        if (
            self.state_polygon.contains(point)
            | self.state_polygon.touches(point)
            | point.within(self.state_polygon)
        ):
            return True

        else:
            return False

    
    def find_path(self):
        """lazy path, lazy code
        """

        switch_direction = {
            "e": "w",
            "w": "e"
        }

        current_direction = "e"
        in_state_flag = True
        lon, lat = self.lon, self.lat

        arr_lonlat_path = np.array([lon, lat])
        while (lat > self.state_boundary[:, 1].min()) :

            lon_new, lat = self.move_center(lon, lat, how=current_direction)
            in_state_flag_new = self.is_point_in_state(lon_new, lat)
            if in_state_flag_new:
                lon = lon_new

            lon = lon_new

            # from in-state to out of state, go south, then reversed direction continually
            # until go in-state to out of state again
            if in_state_flag and not in_state_flag_new:
                lon, lat_new = self.move_center(lon_new, lat, how="s")

                current_direction = switch_direction[current_direction]
                lon_new, lat_new = self.move_center(lon, lat_new, how=current_direction, switched=True)

                in_state_flag = in_state_flag_new
                in_state_flag_new = self.is_point_in_state(lon_new, lat_new)
                lon, lat = lon_new, lat_new

            in_state_flag = in_state_flag_new
            arr_lonlat_path = np.vstack([arr_lonlat_path, [lon, lat]])
            

        return arr_lonlat_path