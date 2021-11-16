"""
    The visualization file contains several data visualization types
    like trajectory visualizer, radar maps, bar charts etc. It is to be noted
    that ipywidgets are used to make the visualizations in this module interactive.

    Warning
    -------
        The visualizations in this module are currently developed with a focus around the
        starkey.csv data as it has been developed as a side project by the developers. It
        will further be integrated into the library as a general class of visualizers in
        the time to come.

    | Authors: Yaksh J Haranwala, Salman Haidri
"""
import random
import folium

import ipywidgets as widgets
from IPython.core.display import display

from ptrail.core.TrajectoryDF import PTRAILDataFrame
import ptrail.utilities.constants as const


class TrajectoryPlotter:
    @staticmethod
    def _create_multi_select(dataset, animal):
        """
            Create the multiple selection widget.
            Parameters
            ----------
                dataset: PTRAILDataFrame
                    The dataset from which the IDs are to be selected.
                animal: str
                    The animal for which the list is to be presented.

            Returns
            -------
                ipywidgets.widgets.SelectMultiple
                    Multiple selection widget.

        """
        dataset = dataset.reset_index()

        # Select the animal based on the parameter passed.
        to_select = None
        if animal.lower() == 'deer':
            to_select = dataset.loc[dataset.Species == 'D', 'traj_id'].unique()
        elif animal.lower() == 'elk':
            to_select = dataset.loc[dataset.Species == 'E', 'traj_id'].unique()
        elif animal.lower() == 'cattle':
            to_select = dataset.loc[dataset.Species == 'C', 'traj_id'].unique()

        # Create the multi select widget and return it.
        ids_ = widgets.SelectMultiple(options=to_select, value=(to_select[0], to_select[1]),
                                      description="Trajectory ID: ", disabled=False)
        return ids_

    @staticmethod
    def _create_radio():
        """
            Create the radio button for selecting the animal.

            Returns
            -------
                ipywidgets.widget.RadioButtons
                    The Radio button for selecting the animal.
        """
        radio = widgets.RadioButtons(options=['Cattle', 'Deer', 'Elk'],
                                     value='Cattle', description='Animal: ',
                                     disabled=False)
        return radio

    @staticmethod
    def _filter_dataset(dataset, _id):
        """
            Filter the dataset based on the ids given by the method below.

            Parameters
            ----------
                dataset: PTRAILDataFrame
                    The dataset from which the data is to be filtered.
                _id: tuple
                    The tuple containing the IDs that are required.

            Return
            ------
                PTRAILDataFrame
                    The filtered dataframe.
        """
        filtered_df = dataset.reset_index().loc[dataset.reset_index()['traj_id'].isin(_id)]
        return PTRAILDataFrame(filtered_df.reset_index(), const.LAT, const.LONG, const.DateTime, const.TRAJECTORY_ID)

    @staticmethod
    def plot_folium_traj(dataset, weight: float = 3, opacity: float = 0.8):
        """
            Use folium to plot the trajectory on a map.

            Parameters
            ----------
                dataset:

                weight: float
                    The weight of the trajectory line on the map.
                opacity: float
                    The opacity of the trajectory line on the map.

            Returns
            -------
                folium.folium.Map
                    The map with plotted trajectory.
        """
        # Create the radio button.
        animal = TrajectoryPlotter._create_radio()

        # Create the multi selection button.
        selector = TrajectoryPlotter._create_multi_select(dataset, animal.value)

        # Display the multi selector and the radio buttons next to each other.
        display(widgets.HBox([animal, selector]))

        # Filter the dataset according the values of the widgets above.
        dataset = TrajectoryPlotter._filter_dataset(dataset, selector.value)

        # The southwest and northeast bouds.
        sw = dataset[['lat', 'lon']].min().values.tolist()
        ne = dataset[['lat', 'lon']].max().values.tolist()

        # Create a map with the initial point.
        map_ = folium.Map(location=(dataset.latitude[0], dataset.longitude[0]))

        ids_ = list(dataset.traj_id.value_counts().keys())
        colors = ["#" + ''.join([random.choice('123456789BCDEF') for j in range(6)])
                  for i in range(len(ids_))]

        for i in range(len(ids_)):
            # First, filter out the smaller dataframe.
            small_df = dataset.reset_index().loc[dataset.reset_index()[const.TRAJECTORY_ID] == ids_[i],
                                                 [const.LAT, const.LONG]]

            # Then, create (lat, lon) pairs for the data points.
            locations = []
            for j in range(len(small_df)):
                locations.append((small_df['lat'].iloc[j], small_df['lon'].iloc[j]))

            # Create text frame.
            iframe = folium.IFrame(f'<font size="1px">Trajectory ID: {ids_[i]} ' + '<br>' +
                                   f'Latitude: {locations[0][0]}' + '<br>' +
                                   f'Longitude: {locations[0][1]} </font>')

            # Create start and end markers for the trajectory.
            popup = folium.Popup(iframe, min_width=180, max_width=200, max_height=75)

            folium.Marker([small_df['lat'].iloc[0], small_df['lon'].iloc[0]],
                          color='green',
                          popup=popup,
                          marker_color='green',
                          icon=folium.Icon(icon_color='green', icon='circle', prefix='fa')).add_to(map_)

            # Create text frame.
            iframe = folium.IFrame(f'<font size="1px">Trajectory ID: {ids_[i]} ' + '<br>' +
                                   f'Latitude: {locations[0][0]}' + '<br>' +
                                   f'Longitude: {locations[0][1]} </font>')

            # Create start and end markers for the trajectory.
            popup = folium.Popup(iframe, min_width=180, max_width=200, max_height=75)

            folium.Marker([small_df['lat'].iloc[-1], small_df['lon'].iloc[-1]],
                          color='green',
                          popup=popup,
                          marker_color='red',
                          icon=folium.Icon(icon_color='red', icon='circle', prefix='fa')).add_to(map_)

            # Add trajectory to map.
            folium.PolyLine(locations,
                            color=colors[i],
                            weight=weight,
                            opacity=opacity).add_to(map_)

        # Fit the map within its bounds and return it.
        map_.fit_bounds([sw, ne])
        return map_
