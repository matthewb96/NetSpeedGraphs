"""
    Main module for running NetSpeedGraphs.
"""

##### IMPORTS #####
# Standard imports
from pathlib import Path
from datetime import datetime, timedelta
from argparse import ArgumentParser

# Third party imports
import speedtest
import numpy as np
import pandas as pd
from bokeh.plotting import figure, output_file, save
from bokeh.models.formatters import DatetimeTickFormatter
from bokeh.models import (ColumnDataSource, DataTable, TableColumn,
                          NumberFormatter, DateFormatter)
from bokeh.layouts import grid

##### CONSTANTS #####
DATA_HEADER = ['Time', 'Ping (ms)', 'Download Speed (Mbs)',
               'Upload Speed (Mbs)']

##### FUNCTIONS #####
def allTests():
    """ Runs ping, download and upload speed tests.

    Returns
    -------
    ping: float
        Ping value in miliseconds.
    download: float
        Download speed in Mbs.
    upload: float
        Upload speed in Mbs.
    """
    st = speedtest.Speedtest()
    server = st.get_best_server()
    down = st.download()
    up = st.upload()
    return server['latency'], down / 1e6, up / 1e6

def plotGraph(data, path):
    """ Plots a graph with the download and upload speeds and pings.

    Parameters
    ----------
    data: pandas.DataFrame
        DataFrame containing 4 columns:
            - Time: datetime objects for the time the test was ran.
            - Ping: ping in milliseconds.
            - Download: download speed in megabits per second.
            - Upload: upload speed in megabits per second.
    path: pathlib Path
        Path to html file for outputting plots to.

    See Also
    --------
    readResults
    """
    # output to static HTML file
    output_file(path)

    # Use the pandas dataframe as the source
    source = ColumnDataSource(data)
    # Create a new plot and set x-axis type as datetime
    netPlot = figure(title="Network Speeds", x_axis_type='datetime',
                     x_axis_label='Time of Test',
                     y_axis_label='Speed (Mbs) / Ping (ms)',
                     tools=['xpan', 'xwheel_zoom', 'box_select', 'reset'],
                     active_drag='xpan', active_scroll='xwheel_zoom',
                     sizing_mode='stretch_both')
    # Change x axis tick format depending on zoom level
    netPlot.xaxis.formatter = DatetimeTickFormatter(hours = ['%H:%M'],
                                                    days = ['%d/%m/%Y'],
                                                    months = ['%m/%Y'])

    # Add the lines to the plot in different colours
    WIDTH = 2
    netPlot.line(x='Time', y='Ping', source=source, legend_label='Ping',
                 line_color='orange', line_width=WIDTH)
    netPlot.line(x='Time', y='Download', source=source, legend_label='Download',
                 line_color='blue', line_width=WIDTH)
    netPlot.line(x='Time', y='Upload', source=source, legend_label='Upload',
                 line_color='green', line_width=WIDTH)

    # Create table
    numFormatter = NumberFormatter(format='0.00')
    columns = [
        TableColumn(field="Time", title='Time',
                    formatter=DateFormatter(format="%Y-%m-%d %H:%M")),
        TableColumn(field='Ping', title='Ping (ms)', formatter=numFormatter),
        TableColumn(field="Download", title='Download Speed (Mbs)',
                    formatter=numFormatter),
        TableColumn(field='Upload', title='Upload Speed (Mbs)',
                    formatter=numFormatter)
    ]
    table = DataTable(source=source, columns=columns, width=400,
                      sizing_mode='stretch_height')

    # Add plot to grid layout
    layout = grid([netPlot, table], ncols=2)

    # show the results
    save(layout)
    return

def storeResults(results, path):
    """ Save the network speed results to CSV containing all results.

    Will create a CSV if it doesn't exist, or append results to it if it does.

    Parameters
    ----------
    results: list-like of floats
        The results from a single run of the network test in the following
        order: ping (miliseconds), download speed (Mbs) and upload speed (Mbs).
    path: pathlib Path
        Path to csv file for saving results to.

    See Also
    --------
    allTests
    """
    # Get current time of results
    now = datetime.now()
    # Create row of results
    row = [now.isoformat(), *[str(i) for i in results]]

    # Check if file exists and create it with header if not
    # then append current results to it
    header = not path.exists()
    with open(path, 'at') as out:
        if header:
            out.writelines(','.join(DATA_HEADER) + '\n')
        out.write(','.join(row) + '\n')
    return

def readResults(path):
    """ Read the csv containing all the results into a DataFrame.
    
    The `DATA_PATH` and `DATA_HEADER` constants are used when reading the csv.
    
    Parameters
    ----------
    path: pathlib Path
        Path to csv file for reading from.

    Returns
    -------
    data: pandas.DataFrame
        DataFrame containing 4 columns:
            - Time: datetime objects for the time the test was ran.
            - Ping: ping in milliseconds.
            - Download: download speed in megabits per second.
            - Upload: upload speed in megabits per second.
    """
    data = pd.read_csv(path, usecols=DATA_HEADER, parse_dates=[0])
    rename = {i: i.split()[0].strip().capitalize() for i in DATA_HEADER}
    data = data.rename(columns=rename)
    return data

def argParser():
    """ Creates an ArgumentParser to get output locations. 
    
    Returns
    -------
    parser: argparse ArgumentParser
        Parser to get the output file locations from the arguments.
    """
    parser = ArgumentParser(description='Run a network test and update html plots.')
    parser.add_argument('data_file', type=Path,
                        help='csv file for storing all network test results.')
    parser.add_argument('html_file', type=Path,
                        help='html file for saving the output plots to.')
    return parser

def main():
    """ Runs the network test to get results then updates the csv and graphs. """
    # Get file locations from arguments
    parser = argParser()
    args = parser.parse_args()
    
    # Run a test and update the graphs
    netRes = allTests()
    storeResults(netRes, args.data_file)
    results = readResults(args.data_file)
    plotGraph(results, args.html_file)
    return

##### MAIN #####
if __name__ == '__main__':
    main()
