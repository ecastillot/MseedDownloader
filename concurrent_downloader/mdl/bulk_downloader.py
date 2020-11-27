#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Concurrent bulk downloader based on obspy's Mass Downloader class:
Download potentially big data sets across a number of FDSN web
services in an automated fashion. 

Author:
    Emmanuel Castillo (ecastillot@unal.edu.co), 2020
"""

import time
import itertools
import concurrent.futures 
from obspy.clients.fdsn.client import Client
from obspy.core.utcdatetime import UTCDateTime

from .mass_downloader import MassDownloader
from obspy.clients.fdsn.mass_downloader import Restrictions

def _run_subprocess(mdl,domain,restriction,
                    mseed_storage,stationxml_storage):
    print("in subprocess")
    
    print("\n** loading -->"
    f"\t{restriction.network} -- {restriction.station}")
    try:
        tic = time.time()
        mdl.download(domain=domain,
                restrictions=restriction, 
                download_chunk_size_in_mb=50, 
                threads_per_client=1, 
                mseed_storage=mseed_storage,
                stationxml_storage=stationxml_storage)
        toc = time.time()
        print("\n** done with -->"
            f"\t{restriction.network} -- {restriction.station} --> "
            f"\ttime: {round(toc-tic,2)} s")                 

    except Exception:
        print("\n!! failed downloading -->"
            f"\t{restriction.network} -- {restriction.station} !")
        pass

def process(args):
    print("in process")
    
    mdl,domain,restriction,\
    mseed_storage,stationxml_storage = args


    print("\n** loading -->"
    f"\t{restriction.network} -- {restriction.station}")
    try:
        tic = time.time()
        mdl.download(domain=domain,
                restrictions=restriction, 
                download_chunk_size_in_mb=50, 
                threads_per_client=1, 
                mseed_storage=mseed_storage,
                stationxml_storage=stationxml_storage)
        toc = time.time()
        print("\n** done with -->"
            f"\t{restriction.network} -- {restriction.station} --> "
            f"\ttime: {round(toc-tic,2)} s")                 

    except Exception:
        print("\n!! failed downloading -->"
            f"\t{restriction.network} -- {restriction.station} !")
        pass

class BulkDownloader(object):
    def __init__(self,client_dict):
        self.client_dict= client_dict

    """Concurrent bulk downloader based on obspy's Mass Downloader class.

    parameters
    ----------
    client_dict: dictionary

        Specific 'base_url', 'user', 'password' keys in the dictionary
        of the client object.
        example:
        {"base_url":"IRIS",
        "user":"gaprietogo@unal.edu.co",
        "password":"DaCgmn3hNjg"}  

    returns
    -------
        BulkDownloader object"""

    @property
    def client(self):
        """
        Returns
        -------
        client object
            Returns the client object according to the 'base_url' 
            'user' 'password' client parameters
        """
        return Client(base_url=self.client_dict["base_url"],
                    user=self.client_dict["user"],
                    password=self.client_dict["password"])

    def _get_stations_info(self,bulk):


        inv = self.client.get_stations_bulk(bulk,level="response")

        stations_info = [(net.code, sta.code) 
                        for net in inv
                        for sta in net ]
        return stations_info

    def _build_station_restrictions(self,restrictions,
                                    stations_info):
        rest_dict = restrictions.__dict__
        new_rest_dict = {}
        for key,value in rest_dict.items():
            if key[0] == '_':
                pass
            elif key == 'chunklength':
                new_rest_dict[key+'_in_sec'] = value
            else:
                new_rest_dict[key] = value

        rest_list = []
        for info in stations_info:
            net,sta = info

            new_rest_dict['network'] = net
            new_rest_dict['station'] = sta
            station_rest = Restrictions(**new_rest_dict)
            rest_list.append(station_rest)

        return rest_list

    def _prepare_args_for_process(self,domain,many_restrictions,
                                    mseed_storage,stationxml_storage):
        mdl = MassDownloader(providers=[self.client])
        args = zip(itertools.repeat(mdl), 
            itertools.repeat(domain),
            many_restrictions,
            itertools.repeat(mseed_storage),  
            itertools.repeat(stationxml_storage))
        return list(args)

    def download_by_station(self,domain,restrictions,
                        mseed_storage,stationxml_storage,
                        workers=None,parallel_mode="thread"):
        """
        Parallel download by each station. 

        Parameters
        ----------
        domain: class:'obspy.mass_downloader.domain'
            The download domain.
        restrictions: class:'obspy.mass_downloader.restrictions.Restrictions'
            Non-spatial downloading restrictions.
        mseed_storage: str
            Where to store the waveform files. 
            If it has '{<SDSdir>}:' then it is going to save in SDS format.
            key parameters for controlling the store: {network}, {station},  
            {location},{channel}, {starttime}, and {endtime}
        stationxml_storage: str
            Where to store the StationXML files.
            key parameters for controlling the store: {network}, {station},  
            {location},{channel}, {starttime}, and {endtime}
        workers: int
            Number of subprocess that will be used.
        parallel_mode: str
            It can be 'thread' or 'process'. However It's recommended
            to use 'process'because by 'thread' you only can use 6 workers
            because for greater workers the downloading is not complete 
            due to no FDSN response.

        returns
        -------
        mseed files and xml files in mseed_storage and stationxml_storage
        respectively.
        """



        ##Check that chunklength_in_sec and time in restrictions
        ## are according with the SDS format
        SDS_key = "{<SDSdir>}:"
        deltat = restrictions.endtime - restrictions.starttime
        chunklength_in_sec = restrictions.chunklength
        if (mseed_storage.find(SDS_key) != -1) and \
            (deltat < 86400):
            raise Exception("Downloading more than one " 
                            "waveform with the same SDS name. "
                            "Please check in restrictions: "
                            f"endtime-starttime={deltat} "
                            "< 86400. In SDS format must be "
                            "greater than 86400")
        elif (mseed_storage.find(SDS_key) != -1) and \
            (chunklength_in_sec < 86400):
            raise Exception("Downloading more than one " 
                            "waveform with the same SDS name. "
                            "Please check in restrictions: "
                            f"chunklength_in_sec={chunklength_in_sec} "
                            "< 86400. In SDS format must be "
                            "greater than 86400")

        ## get the stations information and prepare the restrisctions_list
        ## for the parallel downloading
        bulk = [(restrictions.network, restrictions.station,
                restrictions.location, restrictions.channel,
                 restrictions.starttime, restrictions.endtime) ]
        stations_info = self._get_stations_info(bulk)
        restrictions_list = self._build_station_restrictions(restrictions,
                                                            stations_info)

        ## Go to the downloading: 
        if workers == 1:
            for rest in restrictions_list:
                print(f'======= Working on {rest.station} station.')
                process(rest)
        elif workers == 0:
            raise Exception("workers must be grater than 1")
        else:
            total_tic = time.time()

            #Thread mode
            if parallel_mode == "thread":
                mdl = MassDownloader(providers=[self.client])

                def subprocess(restriction):
                    _run_subprocess(mdl,domain,restriction,
                                    mseed_storage, stationxml_storage)

                with concurrent.futures.ThreadPoolExecutor(
                    max_workers=workers) as executor:
                    executor.map(subprocess,restrictions_list)

            #Process mode
            elif parallel_mode == "process":
                args = self._prepare_args_for_process(domain,
                                    restrictions_list,
                                    mseed_storage,
                                    stationxml_storage)
                with concurrent.futures.ProcessPoolExecutor(
                    max_workers=workers) as executor:
                    executor.map(process,args)
                
            else:
                raise Exception(f"Doesn't exist {parallel_mode} mode"
                                "only 1)thread or 2)process")

            total_toc = time.time()
            print("\n** TOTAL DOWNLOAD TIME"
                    f"\t{round(total_toc-total_tic,2)} s") 

if __name__ == "__main__":
    from obspy.clients.fdsn.mass_downloader.domain import RectangularDomain

    IRIS_client = {"base_url":"IRIS", "user":"gaprietogo@unal.edu.co",
                        "password":"DaCgmn3hNjg"}  

    YU_restrictions = Restrictions(starttime=UTCDateTime(2016, 8, 1),
                            endtime=UTCDateTime(2016, 8, 2),
                            network="YU", 
                            station="CS*",
                            location="*", channel="*",
                            chunklength_in_sec=86400,
                            reject_channels_with_gaps=False,
                            minimum_length=0.0,
                            minimum_interstation_distance_in_m=0.0,
                            channel_priorities=[],
                            location_priorities=[""])
    domainR = RectangularDomain(minlatitude=6, maxlatitude=14,
                           minlongitude=-80, maxlongitude=-68)

    mseed_storage = ("{<SDSdir>}:/home/ecastillo/download/CARMA2/waveforms")
    stationxml_storage = "/home/ecastillo/download/CARMA2/stations/{network}/{station}.xml"

    bdl = BulkDownloader(client_dict=IRIS_client)
    bdl.download_by_station(domain=domainR,
                        restrictions=YU_restrictions, 
                        mseed_storage=mseed_storage,
                        stationxml_storage=stationxml_storage,
                        workers=4,parallel_mode="process")
