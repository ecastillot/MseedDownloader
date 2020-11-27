#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 12 20:00:00 2020
@author: Emmanuel_Castillo
last update: 14-11-2020 
"""

import os
import warnings
import concurrent.futures
from functools import partial
from obspy.clients.fdsn.mass_downloader.utils import get_mseed_filename
from . import utils2download as u2d


def run_process(ppc_restrictions,mseed_storage,st):
  u2d.write_stream(st,ppc_restrictions,mseed_storage)

def MseedDownloader(mseed_storage,client,dld_restrictions,
                      ppc_restrictions=None, n_processor=1, 
                      concurrent_feature="thread"):

  times = u2d.get_chunktimes(starttime=dld_restrictions.starttime,
                        endtime = dld_restrictions.endtime,
                        chunklength_in_sec=dld_restrictions.chunklength,
                        overlap_in_sec=dld_restrictions.overlap_in_sec)
  def run_thread(st):
    u2d.write_stream(st,ppc_restrictions,mseed_storage)

  for starttime, endtime in times:
    try:
      st = client.get_waveforms(network=dld_restrictions.network,
                                station=dld_restrictions.station, 
                                location=dld_restrictions.location,
                                channel=dld_restrictions.channel,
                                starttime=starttime,
                                endtime=endtime)
      st_dict = st._groupby(dld_restrictions.groupby)
      st_values = list(st_dict.values())

    except:
      st_warn = (f"{dld_restrictions.network}."
                  f"{dld_restrictions.station}."
                  f"{dld_restrictions.location}."
                  f"{dld_restrictions.channel}."
                  f"{starttime}."
                  f"{endtime}")
      warnings.warn(f"No:\t{st_warn}") 
      st_values = None

    if st_values != None:
      if n_processor == 1:
        for one_st in st_values:
          u2d.write_stream(one_st,ppc_restrictions,mseed_storage)
      else:
        if n_processor > len(st_values):
          n_processor = len(st_values)

        if concurrent_feature in ("thread","Thread","t","T"):
          with concurrent.futures.ThreadPoolExecutor(max_workers=n_processor) as executor:
            executor.map(run_thread,st_values) 

        elif concurrent_feature in ("process","Process","p","P"):
          with concurrent.futures.ProcessPoolExecutor(max_workers=n_processor) as executor:
            executor.map(partial(run_process,ppc_restrictions,mseed_storage),st_values) 

if __name__ == "__main__":
  from obspy.clients.fdsn import Client as FDSN_Client
  from obspy.clients.filesystem.sds import Client as SDS_Client
  from obspy.core.utcdatetime import UTCDateTime
  from .restrictions import DownloadRestrictions
  
  client = FDSN_Client('http://sismo.sgc.gov.co:8080')
  # client = FDSN_Client('http://10.100.100.232:8091')
  # client = SDS_Client('/mnt/sc232',
  #                    sds_type='D', format='MSEED',)
  
  restrictions = DownloadRestrictions(network="CM",
                          station="BAR2",
                          location="*",
                          channel="*",
                          starttime=UTCDateTime("2019-04-23T00:00:00.0"),
                          endtime=UTCDateTime("2019-04-24T00:00:00.0"),
                          chunklength_in_sec=3600,
                          overlap_in_sec=None,
                          groupby='{network}.{station}.{channel}')

  mseed_storage = ("/home/ecastillo/downloads/"
                  "{network}/{station}/{network}.{station}.{location}.{channel}__{starttime}__{endtime}.mseed")
  
  MseedDownloader(mseed_storage,client,restrictions,
                    ppc_restrictions=None,
                    n_processor=4,concurrent_feature="t")

