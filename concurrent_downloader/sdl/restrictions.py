#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 12 20:00:00 2020
@author: Emmanuel_Castillo
last update: 15-11-2020 
"""

from obspy.clients.fdsn.mass_downloader import Restrictions

class DownloadRestrictions(Restrictions):
    def __init__(self,network,station,location,channel,
              starttime,endtime,
              chunklength_in_sec=None,
              overlap_in_sec=0,
              groupby='{network}.{station}.{channel}'):
        """
        Restrictions to download mseed 
        
        Parameters:
        -----------
        network: str
            Select one or more network codes. 
            Multiple codes are comma-separated (e.g. "IU,TA"). 
            Wildcards are allowed.
        station: str
            Select one or more SEED station codes. 
            Multiple codes are comma-separated (e.g. "ANMO,PFO"). 
            Wildcards are allowed.
        location: str
            Select one or more SEED location identifiers. 
            Multiple identifiers are comma-separated (e.g. "00,01"). 
            Wildcards are allowed.
        channel: str
            Select one or more SEED channel codes. 
            Multiple codes are comma-separated (e.g. "BHZ,HHZ").
        starttime: obspy.UTCDateTime
            Limit results to time series samples on or 
            after the specified start time.
        endtime: obspy.UTCDateTime
            Limit results to time series samples on or 
            before the specified end time.
        chunklength_in_sec: None or int
            The length of one chunk in seconds. 
            If set, the time between starttime and endtime will be divided 
            into segments of chunklength_in_sec seconds.
        overlap_in_sec: None or int
            For more than one chunk, each segment will have overlapping seconds
        groupby: str
            Download group traces together which have the same metadata given by this parameter. 
            The parameter should name the corresponding keys of the stats object, e.g. '{network}.{station}'. 
            This parameter can take the value 'id' which groups the traces by SEED id.
        """
        Restrictions.__init__(self,network=network,station=station,
                            location=location,channel=channel,
                            starttime=starttime,endtime=endtime,
                            chunklength_in_sec=chunklength_in_sec)
        self.overlap_in_sec = overlap_in_sec
        self.groupby = groupby

class PreprocRestrictions(object):
    def __init__(self,seed_ids,order=['merge','detrend','taper','normalized'],
                decimate=None,detrend=None,applyfilter=None,
                merge=None,normalize=None,remove_response=None,
                resample=None,taper=None):
        """
        Restrictions to preprocess a stream selected by seed_ids
        
        Parameters:
        -----------
        seed_ids: list
            Contains each seed_id in the next way: network.station"
            ex: ["IU.ANMO","CM.BAR2"]
        order: list of str
            Order to preprocess the stream.
            ex: ['merge','detrend','taper','normalized']
        decimate: dict
            Contains the parameters of the decimate Stream method 
        detrend: dict 
            Contains the parameters of the detrend Stream method 
        filter: dict
            Contains the parameters of the filter Stream method 
        merge: dict
            Contains the parameters of the merge Stream method 
        normalize: dict
            Contains the parameters of the normalize Stream method 
        remove_response: dict
            Contains the parameters of the remove_response Stream method 
        resample: dict
            Contains the parameters of the resample Stream method 
        taper: dict
            Contains the parameters of the taper Stream method 

        --------
        """
        self.seed_ids = seed_ids
        self.order = order
        self.decimate = decimate
        self.detrend = detrend
        self.applyfilter = applyfilter
        self.merge = merge
        self.normalize = normalize
        self.remove_response = remove_response
        self.resample = resample
        self.taper = taper
