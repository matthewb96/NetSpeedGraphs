"""
    Main module for running NetSpeedGraphs.
"""

##### IMPORTS #####
# Standard imports
from pathlib import Path
from datetime import datetime, timedelta

# Third party imports
import speedtest
import numpy as np
import pandas as pd
from bokeh.plotting import figure, output_file, show
from bokeh.models.formatters import DatetimeTickFormatter
from bokeh.models import (ColumnDataSource, DataTable, TableColumn,
                          NumberFormatter, DateFormatter)
from bokeh.layouts import grid

##### CONSTANTS #####
HTML_PATH = Path('network_graphs.html')
DATA_PATH = Path('network_data.csv')
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

def plotGraph(data):
    """ Plots a graph with the download and upload speeds and pings.

    Parameters
    ----------
    data: pandas.DataFrame
        Containing index column of datetime objects and 3 columns:
            - Ping
            - Download
            - Upload
    """
    # output to static HTML file
    output_file(HTML_PATH)

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
    show(layout)
    return

def storeResults(results):
    """ Save the network speed results to CSV containing all results.

    Will create a CSV if it doesn't exist, or append results to it if it does.

    Parameters
    ----------
    results: list-like of floats
        The results from a single run of the network test in the following
        order: ping (miliseconds), download speed (Mbs) and upload speed (Mbs).

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
    header = not DATA_PATH.exists()
    with open(DATA_PATH, 'at') as out:
        if header:
            out.writelines(', '.join(DATA_HEADER) + '\n')
        out.write(', '.join(row) + '\n')
    return

##### MAIN #####
if __name__ == '__main__':
    netRes = allTests()
    storeResults(netRes)
    print(f'Ping:\t{netRes[0]:.2f}ms')
    print(f'Download:\t{netRes[1]:.2f}Mbs')
    print(f'Upload:\t{netRes[2]:.2f}Mbs')

    # Create test data
    N = 100
    times = np.array([datetime.now() + i * timedelta(minutes=30) for i in range(N)])
    # times = np.arange(N)
    # Create random array +/- d around x
    randomArray = lambda x, d: x + (2 * d * (np.random.rand(N) - 0.5))
    pings = randomArray(netRes[0], 2)
    downloads = randomArray(netRes[1], 10)
    uploads = randomArray(netRes[2], 5)
    # Create dataframe of test data
    test = pd.DataFrame(index=times, data={'Ping': pings,
                                           'Download': downloads,
                                           'Upload': uploads})
    test.index.name = 'Time'
    # Plot the graph
    plotGraph(test)
