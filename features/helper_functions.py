"""
    This module contains all the helper functions for the parallel calculators in
    the spatial and temporal features classes.
    WARNING: These functions may not be used directly as they would result in a
             slower calculation and execution times. They are meant to be used
             only as helpers. For calculation of features, use the ones in the
             features package.
"""
import numpy
import numpy as np
import pandas

import utilities.constants as const
import utilities.exceptions as exc
from utilities.DistanceCalculator import DistanceFormulaLog as calc


class Helpers:
    @staticmethod
    def _date_helper(dataframe):
        """
            This function is a helper method for the create_date_column(). The create_date_helper()
            methods delegates the actual task of creating the date to date_helper() function. What
            this function does is that it extracts the date from the DateTime column present in the
            DF and then adds a column to the DF itself, containing the date.

            Parameters
            ----------
                dataframe: NumPandasTraj
                    The DaskTrajectoryDF on which the creation of the date column is to be done.

            Returns
            -------
                pandas.core.dataframe.DataFrame
                    The dataframe containing the date column.

        """
        date_format = "%Y-%m-%d"  # Format of the date.

        # Reset the index of the DF in order to access the date time column and then generate
        # an iterable list of the items inside the column.
        gen = dataframe.reset_index()['DateTime'].iteritems()
        gen = list(gen)

        # Now, we extract the Date from all the time values.
        for i in range(len(gen)):
            gen[i] = gen[i][1].strftime(date_format)

        dataframe['Date'] = gen  # Assign the date column to the dataframe.
        return dataframe  # Return the dataframe with the date column inside it.

    @staticmethod
    def _time_helper(dataframe):
        """
            This function is a helper method for the create_time_column(). The create_time_helper()
            methods delegates the actual task of creating the time to time_helper() function. What
            this function does is that it extracts the time from the DateTime column present in the
            DF and then adds a column to the DF itself, containing the time.

            Parameters
            ----------
                dataframe: NumPandasTraj
                    The DaskTrajectoryDF on which the creation of the time column is to be done.

            Returns
            -------
                pandas.core.dataframe.DataFrame
                    The dataframe containing the resultant time column.

        """
        time_format = "%H:%M:%S"

        # Reset the index of the DF in order to access the date time column and then generate
        # an iterable list of the items inside the column.
        datetime = dataframe.reset_index()['DateTime'].iteritems()
        datetime = list(datetime)

        # Now lets extract the time from the DateTime column.
        for i in range(len(datetime)):
            datetime[i] = datetime[i][1].strftime(time_format)

        dataframe['Time'] = datetime
        return dataframe

    @staticmethod
    def _day_of_week_helper(dataframe):
        """
            This function is the helper function of the create_day_of_week() function. The day_of_week()
            function delegates the actual task of calculating the day of the week based on the datetime
            present in the data. This function does the calculation and creates a column called Day_Of_week
            and places it in the dataframe and returns it.

            Parameters
            ----------
                dataframe: NumPandasTraj
                    The dataframe on which calculation is to be performed.

            Returns
            -------
                pandas.core.dataframe
                    The dataframe containing the resultant Day_Of_Week column.
        """
        # First generate a list of the DateTime column of the dataframe using the iteritems()
        # function and then converting it into a python list.
        datetime = dataframe.reset_index()['DateTime'].iteritems()
        datetime = list(datetime)

        # Now extract all the names of the day based on the day.
        for i in range(len(datetime)):
            datetime[i] = datetime[i][1].day_name()

        # Assign the Day_Of_Week column and then return the dataframe.
        dataframe['Day_Of_Week'] = datetime

        return dataframe

    @staticmethod
    def _weekend_helper(dataframe):
        """
             This function is the helper function of the create_weekend_indicator_week() function.
             The create_weekend_indicator() function delegates the actual task of checking whether
             the day of the week is either a Saturday or Sunday based on the datetime present in
             the data. This function does the calculation and creates a column called Weekend
             and places it in the dataframe and returns it.

             Parameters
             ----------
                 dataframe: NumPandasTraj
                     The dataframe on which calculation is to be performed.

             Returns
             -------
                 pandas.core.dataframe
                     The dataframe containing the resultant Day_Of_Week column.
        """
        # First, extract the DateTime column from the dataframe using the iteritems
        # and then convert it into a python list.
        weekend_indicator = dataframe.reset_index()['DateTime'].iteritems()
        weekend_indicator = list(weekend_indicator)

        # Now for each timestamp in the list, check its day and then append True/False
        # to the list based on whether the day is a weekday or weekend.
        for i in range(len(weekend_indicator)):
            weekend_indicator[i] = True if weekend_indicator[i][1].day_name() in const.WEEKEND else False

        # Append the column to the dataframe and return the DF.
        dataframe['Weekend'] = weekend_indicator
        return dataframe

    @staticmethod
    def _time_of_day_helper(dataframe):
        """
             This function is the helper function of the create_time_of_day() function.
             The create_time_of_day() function delegates the actual task of calculating the time
             of the day of the week based on the datetime present in the data.This function does
             the calculation and creates a column called Time_Of_Day and places it in the dataframe
             and returns it.

             Parameters
             ----------
                 dataframe: NumPandasTraj
                     The dataframe on which calculation is to be performed.

             Returns
             -------
                 pandas.core.dataframe
                     The dataframe containing the resultant Day_Of_Week column.
        """
        # First, extract the DateTime column from the dataframe using the iteritems
        # and then convert it into a python list.
        timestamps = dataframe.reset_index()['DateTime'].iteritems()
        timestamps = list(timestamps)

        # Now, lets calculate the Time of the day based on the hour of time present
        # in the timestamp in the data and then append the results in a new column.
        for i in range(len(timestamps)):
            timestamps[i] = const.TIME_OF_DAY[timestamps[i][1].hour]

        # Now append the new column to the dataframe and return the dataframe.
        dataframe['Time_Of_Day'] = timestamps
        return dataframe

    @staticmethod
    def _consecutive_distance_helper(dataframe):
        """
            This function is the helper function of the create_distance_between_consecutive_column() function.
            The create_distance_between_consecutive_column() function delegates the actual task of calculating
            the distance between 2 consecutive points. This function does the calculation and creates a column
            called Distance_prev_to_curr and places it in the dataframe and returns it.

            Parameters
            ----------
                dataframe: NumPandasTraj
                    The dataframe on which calculation is to be performed.

                Returns
                -------
                    pandas.core.dataframe
                        The dataframe containing the resultant Distance_prev_to_curr column.
        """
        # First, lets fetch the latitude and longitude columns from the dataset and store it
        # in a numpy array.
        traj_ids = np.array(dataframe.reset_index()[const.TRAJECTORY_ID])
        latitudes = np.array(dataframe[const.LAT])
        longitudes = np.array(dataframe[const.LONG])
        distances = np.zeros(len(latitudes))

        # Now, lets calculate the Great-Circle (Haversine) distance between the 2 points and store
        # each of the values in the distance numpy array.
        distances[0] = np.NAN
        for i in range(len(latitudes) - 1):
            # If the traj_id is same it calculates its distance from the above mentioned formula.
            if traj_ids[i] == traj_ids[i + 1]:
                distances[i + 1] = calc.haversine_distance(latitudes[i], longitudes[i],
                                                           latitudes[i + 1], longitudes[i + 1])
            # The point at which a new trajectory starts, its distance is set to zero and the calculation
            # for that trajectory id starts from that point.
            else:
                distances[i + 1] = np.NAN

        # Now assign the column 'Distance_prev_to_curr' to the dataframe and return the dataframe.
        dataframe['Distance_prev_to_curr'] = distances
        return dataframe

    @staticmethod
    def _start_distance_helper(dataframe):
        """
            This function is the helper function of the create_distance_from_start_column() function.
            The create_distance_from_start_column() function delegates the actual task of calculating
            the distance between 2 the start point of the trajectory to the current point.This function
            does the calculation and creates a column called Distance_start_to_curr and places it in the
            dataframe and returns it.

            Parameters
            ----------
                dataframe: NumPandasTraj
                    The dataframe on which calculation is to be performed.

                Returns
                -------
                    pandas.core.dataframe
                        The dataframe containing the resultant Distance_start_to_curr column.
        """
        # First, lets create some numpy arrays containing the trajectory ID, latitude,
        # longitudes and distances.
        traj_ids = numpy.array(dataframe.reset_index()[const.TRAJECTORY_ID])
        latitudes = numpy.array(dataframe[const.LAT])
        longitudes = numpy.array(dataframe[const.LONG])
        distances = numpy.zeros(len(traj_ids))

        # Now, lets calculate the Great-Circle (Haversine) distance between the 2 points and store
        # each of the values in the distance numpy array.
        start = 0  # The index of the starting point.
        distances[0] = np.NAN
        for i in range(len(distances) - 1):
            # Check if the 2 points between which the distance is being calculated are
            # of the same trajectory ID, and if so continue with the calculation.
            if traj_ids[i] == traj_ids[i + 1]:
                distances[i + 1] = calc.haversine_distance(latitudes[start], longitudes[start],
                                                           latitudes[i + 1], longitudes[i + 1])
            # Otherwise, when the trajectory ID changes, then assign the distance 0 to the first
            # point and change the start index to that point so that calculation yields correct
            # results
            else:
                distances[i + 1] = np.NAN
                start = i + 1

        # Now, assign the new column to the dataframe and return it.
        dataframe['Distance_start_to_curr'] = distances
        return dataframe

    @staticmethod
    def _given_point_distance_helper(dataframe, coordinates):
        """
            This function is the helper function of the create_distance_from_point() function. The
            create_distance_from_point() function delegates the actual task of calculating distance
            between the given point to all the points in the dataframe to this function. This function
            calculates the distance and creates another column called 'Distance_to_specified_point'.

            Parameters
            ----------
                dataframe: NumPandasTraj
                    The dataframe on which calculation is to be done.
                coordinates: tuple
                    The coordinates from which the distance is to be calculated.

            Returns
            -------
                pandas.core.dataframe.DataFrame
                    The dataframe containing the resultant column.
        """
        # First, lets fetch the latitude and longitude columns from the dataset and store it
        # in a numpy array.
        latitudes = np.array(dataframe[const.LAT])
        longitudes = np.array(dataframe[const.LONG])
        distances = np.zeros(len(latitudes))

        # Now, lets calculate the Great-Circle (Haversine) distance between the 2 points and store
        # each of the values in the distance numpy array.
        for i in range(len(latitudes)):
            distances[i] = calc.haversine_distance(coordinates[0], coordinates[1],
                                                   latitudes[i], longitudes[i])

        dataframe[f'Distance_to_{coordinates}'] = distances
        return dataframe

    @staticmethod
    def _point_within_range_helper(dataframe, coordinates, dist_range):
        """
            This is the helper function for create_point_within_range() function. The
            create_point_within_range_column()

            Parameters
            ----------
                dataframe: NumPandasTraj
                    The dataframe on which the operation is to be performed.
                coordinates: tuple
                    The coordinates from which the distance is to be checked.
                dist_range:
                    The range within which the distance from the coordinates should lie.

            Returns
            -------
                pandas.core.dataframe.DataFrame
                    The dataframe containing the resultant column.
        """
        # First, lets fetch the latitude and longitude columns from the dataset and store it
        # in a numpy array.
        latitudes = np.array(dataframe[const.LAT])
        longitudes = np.array(dataframe[const.LONG])
        distances = []

        # Now, lets calculate the Great-Circle (Haversine) distance between the 2 points and then check
        # whether the distance is within the user specified range and store each of the values in the \
        # distance numpy array.
        for i in range(len(latitudes)):
            distances.append(calc.haversine_distance(coordinates[0], coordinates[1],
                                                     latitudes[i], longitudes[i]) <= dist_range)

        # Now, assign the column containing the results calculated above and
        # return the dataframe.
        dataframe[f'Within_{dist_range}_m_from_{coordinates}'] = distances
        return dataframe

    @staticmethod
    def _bearing_helper(dataframe):
        """
            This function is the helper function of the create_bearing_column(). The create_bearing_column()
            delegates the task of calculation of bearing between 2 points to this function because the original
            functions runs multiple instances of this function in parallel. This function does the calculation
            of bearing between 2 consecutive points in the entire DF and then creates a column in the dataframe
            and returns it.

            Parameters
            ----------
                dataframe: NumPandasTraj
                    The dataframe on which the calculation is to be done.

            Returns
            -------
                NumPandasTraj:
                    The dataframe containing the Bearing column.
        """
        # First, lets create 3 numpy arrays containing latitude, longitude and
        # trajectory ids of the data.
        latitude = np.array(dataframe[const.LAT])
        longitude = np.array(dataframe[const.LONG])
        traj_ids = np.array(dataframe.reset_index()[const.TRAJECTORY_ID])
        bearings = np.zeros(len(latitude))

        # Now, lets loop over the data and calculate the bearing between
        # 2 consecutive points.
        bearings[0] = np.NaN
        for i in range(len(bearings) - 1):
            # Check if the 2 points between which the distance is being calculated are
            # of the same trajectory ID, and if so continue with the calculation.
            if traj_ids[i] == traj_ids[i + 1]:
                bearings[i + 1] = calc.bearing_calculation(latitude[i], longitude[i],
                                                           latitude[i + 1], longitude[i + 1])
            # Otherwise, when the trajectory ID changes, then assign the distance 0 to the first
            # point and change the start index to that point so that calculation yields correct
            # results
            else:
                bearings[i + 1] = np.NaN

        dataframe['Bearing_between_consecutive'] = bearings
        return dataframe

    @staticmethod
    def _start_location_helper(dataframe, ids_):
        """
            This function is the helper function of the get_start_location(). The get_start_location() function
            delegates the task of calculating the start location of the trajectories in the dataframe because the
            original functions runs multiple instances of this function in parallel. This function finds the start
            location of the specified trajectory IDs the DF and then another returns dataframe containing start
            latitude, start longitude and trajectory ID for each trajectory


            Parameter
            ---------
                dataframe: NumPandasTraj
                    The dataframe of which the locations are to be found.dataframe
                ids_: list
                    List of trajectory ids for which the start locations are to be calculated

            Returns
            -------
                pandas.core.dataframe.Dataframe
                    New dataframe containing Trajectory as index and latitude and longitude
        """
        results = []

        # Loops over the length of trajectory ids. Filter the dataframe according to each of the ids
        # and then further filter that dataframe according to the earliest(minimum) time.
        # And then append the start location of that earliest time into a list
        for i in range(len(ids_)):
            filt = (dataframe.loc[dataframe[const.TRAJECTORY_ID] == ids_[i],
                                  [const.DateTime, const.LAT, const.LONG]])
            start_loc = (filt.loc[filt[const.DateTime] == filt[const.DateTime].min(),
                                  [const.LAT, const.LONG]]).reset_index()
            results.append([start_loc[const.LAT][0], start_loc[const.LONG][0], ids_[i]])

        # Make a new dataframe containing Latitude Longitude and Trajectory id
        df = pandas.DataFrame(results).reset_index(drop=True).rename(columns={0: const.LAT,
                                                                              1: const.LONG,
                                                                              2: const.TRAJECTORY_ID})

        # Return the dataframe by setting Trajectory id as index
        return df.set_index(const.TRAJECTORY_ID)

    @staticmethod
    def _end_location_helper(dataframe, ids_):
        """
            This function is the helper function of the get_end_location(). The get_end_location() function
            delegates the task of calculating the end location of the trajectories in the dataframe because the
            original functions runs multiple instances of this function in parallel. This function finds the end
            location of the specified trajectory IDs the DF and then another returns dataframe containing
            end latitude, end longitude and trajectory ID for each trajectory

            Parameter
            ---------
                dataframe: NumPandasTraj
                    The dataframe of which the locations are to be found.dataframe
                ids_: list
                    List of trajectory ids for which the end locations are to be calculated

            Returns
            -------
                pandas.core.dataframe.Dataframe
                    New dataframe containing Trajectory ID as index and latitude and longitude
                    as other 2 columns.
        """
        results = []

        # Loops over the length of trajectory ids. Filter the dataframe according to each of the ids
        # and then further filter that dataframe according to the latest(maximum) time.
        # And then append the end location of that latest time into a list.
        for i in range(len(ids_)):
            filt = (dataframe.loc[dataframe[const.TRAJECTORY_ID] == ids_[i],
                                  [const.DateTime, const.LAT, const.LONG]])
            start_loc = (filt.loc[filt[const.DateTime] == filt[const.DateTime].max(),
                                  [const.LAT, const.LONG]]).reset_index()
            results.append([start_loc[const.LAT][0], start_loc[const.LONG][0], ids_[i]])

        # Make a new dataframe containing Latitude Longitude and Trajectory id
        df = pandas.DataFrame(results).reset_index(drop=True).rename(columns={0: const.LAT,
                                                                              1: const.LONG,
                                                                              2: const.TRAJECTORY_ID})
        # Return the dataframe by setting Trajectory id as index
        return df.set_index(const.TRAJECTORY_ID)

    @staticmethod
    def _start_time_helper(dataframe, ids_):
        """
            This function is the helper function of the get_start_time(). The get_start_time() function
            delegates the task of calculating the end location of the trajectories in the dataframe because the
            original functions runs multiple instances of this function in parallel. This function finds the start
            time of the specified trajectory IDs the DF and then another returns dataframe containing
            end latitude, end longitude, DateTime and trajectory ID for each trajectory

            Parameter
            ---------
                dataframe: NumPandasTraj
                    The dataframe of which the locations are to be found.dataframe
                ids_: list
                    List of trajectory ids for which the end locations are to be calculated

            Returns
            -------
                pandas.core.dataframe.Dataframe
                    New dataframe containing Trajectory ID as index and latitude and longitude
                    as other 2 columns.
        """
        results = []

        # Loops over the length of trajectory ids. Filter the dataframe according to each of the ids
        # and then further filter that dataframe according to the earliest(minimum) time.
        # And then append the data of that latest time into a list.
        for i in range(len(ids_)):
            filt = (dataframe.loc[dataframe[const.TRAJECTORY_ID] == ids_[i],
                                  [const.DateTime, const.LAT, const.LONG]])
            start_time = (filt.loc[filt[const.DateTime] == filt[const.DateTime].min()]).reset_index()
            results.append([start_time[const.DateTime][0],  ids_[i]])

        # Make a new dataframe containing Latitude Longitude and Trajectory id
        df = pandas.DataFrame(results).reset_index(drop=True).rename(columns={0: const.DateTime,
                                                                              1: const.TRAJECTORY_ID})
        # Return the dataframe by setting Trajectory id as index
        return df.set_index(const.DateTime)

    @staticmethod
    def _end_time_helper(dataframe, ids_):
        """
            This function is the helper function of the get_start_time(). The get_start_time() function
            delegates the task of calculating the end location of the trajectories in the dataframe because the
            original functions runs multiple instances of this function in parallel. This function finds the start
            time of the specified trajectory IDs the DF and then another returns dataframe containing
            end latitude, end longitude, DateTime and trajectory ID for each trajectory

            Parameter
            ---------
                dataframe: NumPandasTraj
                    The dataframe of which the locations are to be found.dataframe
                ids_: list
                    List of trajectory ids for which the end locations are to be calculated

            Returns
            -------
                pandas.core.dataframe.Dataframe
                    New dataframe containing Trajectory ID as index and latitude and longitude
                    as other 2 columns.
        """