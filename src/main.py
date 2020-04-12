"""
    Main module for running NetSpeedGraphs.
"""

##### IMPORTS #####
# Standard imports
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
    output_file("test.html")

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


##### MAIN #####
if __name__ == '__main__':
    netRes = allTests()
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
