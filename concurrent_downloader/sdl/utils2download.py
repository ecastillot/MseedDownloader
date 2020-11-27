#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 12 20:00:00 2020
@author: Emmanuel_Castillo
last update: 14-11-2020 
"""

import os
import time
import datetime as dt

def write_stream(one_st,ppc_restrictions,mseed_storage):
    """
    Write a stream in a specific storage given by mseed_storage

    Parameters:
    -----------
    one_st: obspy.Stream object
        Stream that will be written.
    ppc_restrictions: PreprocRestrictions object
        Restrictions to preprocess a stream.
    mseed_storage:
        Where to store the waveform files.
        The parameter should name the corresponding keys 
        of the stats object,
        e.g. '{network}.{station}.{location}.{channel}__{starttime}__{endtime}

    """
    now = dt.datetime.now().strftime("%Y/%m/%d %H:%M:%S")

    one_st,ppc,comment = preproc_stream(one_st,ppc_restrictions)
    tr = one_st[0]
    mseed_filename = get_mseed_filename(_str=mseed_storage, 
                                    network=tr.stats.network, 
                                    station=tr.stats.station,
                                    location=tr.stats.location, 
                                    channel=tr.stats.channel,
                                    starttime=tr.stats.starttime, 
                                    endtime=tr.stats.endtime,
                                    ppc=ppc)

    filename = os.path.basename(mseed_filename)
    if os.path.isfile(mseed_filename) == False:
        mseed_dir = os.path.dirname(mseed_filename)
        if os.path.isdir(mseed_dir) == False:
            os.makedirs(mseed_dir)
        else:
            pass

        one_st.write(mseed_filename,format="MSEED")
        print(f"{now}[Downloaded]:  {mseed_filename}  {comment}")

    else:
        print(f"{now}[Exist]:  {mseed_filename}  {comment}")

def get_mseed_filename(_str, network, station, location, channel,
                       starttime, endtime,ppc=False):
    """
    Helper function getting the filename of a MiniSEED file.

    If it is a string, and it contains ``"{network}"``,  ``"{station}"``,
    ``"{location}"``, ``"{channel}"``, ``"{starttime}"``, and ``"{endtime}"``
    formatting specifiers, ``str.format()`` is called.

    Otherwise it is considered to be a folder name and the resulting
    filename will be
    ``"FOLDER_NAME/NET.STA.LOC.CHAN__STARTTIME__ENDTIME.mseed"``

    In the last two cases, the times will be formatted with
    ``"%Y%m%dT%H%M%SZ"``.
    """
    strftime = "%Y%m%dT%H%M%SZ"

    if ppc == True:
        ppc_str = ".ppc"
    else:
        ppc_str = ""

    if ("{network}" in _str) and ("{station}" in _str) and \
            ("{location}" in _str) and ("{channel}" in _str) and \
            ("{starttime}" in _str) and ("{endtime}" in _str) and \
            ("{ppc}" in _str):
        
        path = _str.format(
            network=network, station=station, location=location,
            channel=channel, starttime=starttime.strftime(strftime),
            endtime=endtime.strftime(strftime), ppc=ppc_str)
    elif ("{network}" in _str) and ("{station}" in _str) and \
            ("{location}" in _str) and ("{channel}" in _str) and \
            ("{starttime}" in _str) and ("{endtime}" in _str):
        path = _str.format(
            network=network, station=station, location=location,
            channel=channel, starttime=starttime.strftime(strftime),
            endtime=endtime.strftime(strftime))
    else:
        path = os.path.join(
            _str,
            "{network}.{station}.{location}.{channel}__{s}__{e}.{ppc}.mseed".format(
                network=network, station=station, location=location,
                channel=channel, s=starttime.strftime(strftime),
                e=endtime.strftime(strftime), ppc=ppc_str) )
    if path is True:
        return True
    elif not isinstance(path, (str, bytes)):
        raise TypeError("'%s' is not a filepath." % str(path))
    return path

def preproc_stream(st,ppc_restrictions):
    """
    Parameters:
    -----------
    st: obspy.Stream object
        Stream object to preprocessing
    ppc_restrictions: PreprocRestrictions object
        Restrictions to preprocess a stream

    Returns:
    --------
    st: obspy.Stream object
        Preprocessed stream according to the order of the parameters. 
    processed: True or False
        True if was processed, False if not.
    """
    if ppc_restrictions == None:
        processed = False
        comment = ""
    else:
        tr = st[0]
        seed_id = f"{tr.stats.network}.{tr.stats.station}"
        comment = ""
        if seed_id in ppc_restrictions.seed_ids:
            for i,process in enumerate(ppc_restrictions.order):
                try:
                    if process == 'decimate':
                        st.decimate(**ppc_restrictions.decimate)
                    elif process == 'detrend':
                        st.detrend(**ppc_restrictions.detrend)
                    elif process == 'applyfilter':
                        st.filter(**ppc_restrictions.applyfilter)
                    elif process == 'merge':
                        st.merge(**ppc_restrictions.merge)
                    elif process == 'normalize':
                        st.normalize(**ppc_restrictions.normalize)
                    elif process == 'remove_response':
                        st.remove_response(**ppc_restrictions.remove_response)
                    elif process == 'resample':
                        st.resample(**ppc_restrictions.resample)
                    elif process == 'taper':
                        st.taper(**ppc_restrictions.taper)
                    else:
                        str_failed = (f"Failed ppc: {seed_id}-> NO {process}")
                        raise Exception( str_failed)

                    ## only for print comments    
                    if i == len(ppc_restrictions.order)-1:
                        comment += f"({process}:ok)"
                    else:
                        comment += f"({process}:ok)->"
                except:
                    if i == len(ppc_restrictions.order)-1:
                        comment += f"({process}:Failed)"
                    else:
                        comment += f"({process}:Failed)->"
                processed = True
            comment = f"[{comment}]"
        else:
            processed = False

    return st, processed, comment

def get_chunktimes(starttime,endtime,chunklength_in_sec, overlap_in_sec=0):
    """
    Make a list that contains the chunktimes according to 
    chunklength_in_sec and overlap_in_sec parameters.

    Parameters:
    -----------
    starttime: obspy.UTCDateTime object
        Start time
    endtime: obspy.UTCDateTime object
        End time
    chunklength_in_sec: None or int
        The length of one chunk in seconds. 
        The time between starttime and endtime will be divided 
        into segments of chunklength_in_sec seconds.
    overlap_in_sec: None or int
        For more than one chunk, each segment will have overlapping seconds

    Returns:
    --------
    times: list
        List of tuples, each tuple has startime and endtime of one chunk.
    """

    if chunklength_in_sec == 0:
        raise Exception("chunklength_in_sec must be different than 0")
    elif chunklength_in_sec == None:
        return [(starttime,endtime)]

    if overlap_in_sec == None:
        overlap_in_sec = 0

    deltat = starttime
    dtt = dt.timedelta(seconds=chunklength_in_sec)
    overlap_dt = dt.timedelta(seconds=overlap_in_sec)

    times = []
    while deltat < endtime:
        # chunklength can't be greater than (endtime-startime)
        if deltat + dtt > endtime:
            break
        else:
            times.append((deltat,deltat+dtt))
            deltat += dtt - overlap_dt

    if deltat < endtime:    
        times.append((deltat,endtime))
    return times


if __name__ == "__main__":
    from obspy.clients.fdsn import Client as FDSN_Client
    from obspy.core.utcdatetime import UTCDateTime
    from .restrictions import PreprocRestrictions
    client = FDSN_Client('http://sismo.sgc.gov.co:8080')
    st = client.get_waveforms(network="CM",
                          station="BAR2",
                          location="*",
                          channel="*",
                          starttime=UTCDateTime("2019-04-23T00:00:00.0"),
                          endtime=UTCDateTime("2019-04-23T00:02:00.0"))
    ppc_restrictions = PreprocRestrictions(["CM.BAR2"],detrend={'type':'simple'})
    preproc_stream(st,ppc_restrictions)
    ######### inventory
    # json_path = "/home/ecastillo/repositories/AIpicker_modules/onejson.json"
    # client_baseurl = "http://sismo.sgc.gov.co:8080"

    # restrictions = DownloadRestrictions(network="CM",
    #                       station="BAR2",
    #                       location="*",
    #                       channel="*",
    #                       starttime=UTCDateTime("2019-04-23T00:22:34.5"),
    #                       endtime=UTCDateTime("2019-04-25T00:23:39.5"),
    #                       chunklength_in_sec=5000,
    #                       overlap_in_sec=None,
    #                       groupby='{network}.{station}.{channel}')
    # xml = "/home/ecastillo/repositories/AIpicker_modules/CM.xml"

    # makeStationList(json_path,client_baseurl,restrictions,from_xml=xml)

    ######## get stations
    # json_path = "/home/ecastillo/repositories/AIpicker_modules/onejson.json"
    # client_baseurl = "IRIS"
    # restrictions = DownloadRestrictions(network="CI",
    #                   station="BAK,ARV",
    #                   location="*",
    #                   channel="BH*",
    #                   starttime=UTCDateTime("2020-09-01 00:00:00.00"),
    #                   endtime=UTCDateTime("2020-09-02 00:00:00.00"),
    #                   chunklength_in_sec=3600,
    #                   overlap_in_sec=None,
    #                   groupby='{network}.{station}.{channel}')
    # makeStationList(json_path=json_path,client_baseurl="IRIS",restrictions=restrictions)