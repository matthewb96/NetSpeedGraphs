"""
    Main module for running NetSpeedGraphs.
"""

##### IMPORTS #####
# Standard imports

# Third party imports
import speedtest

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


##### MAIN #####
if __name__ == '__main__':
    netRes = allTests()
    print(f'Ping:\t{netRes[0]:.2f}ms')
    print(f'Download:\t{netRes[1]:.2f}Mbs')
    print(f'Upload:\t{netRes[2]:.2f}Mbs')

