if __name__ == "__main__":

    import sys
    module_path = "/home/ecastillo/repositories/AIpicker"
    sys.path.insert(0,module_path)

    from obspy.clients.fdsn import Client as FDSN_Client
    from obspy.clients.filesystem.sds import Client as SDS_Client
    from obspy.core.utcdatetime import UTCDateTime
    from AIpicker.concurrent_downloader.sdl.restrictions import DownloadRestrictions
    from AIpicker.concurrent_downloader.sdl.restrictions import PreprocRestrictions
    from AIpicker.concurrent_downloader.sdl.downloader import MseedDownloader


    client = FDSN_Client('http://sismo.sgc.gov.co:8080')
    # client = FDSN_Client('http://10.100.100.232:8091')
    # client = SDS_Client('/mnt/sc232',
    #                    sds_type='D', format='MSEED',)

    dld_restrictions = DownloadRestrictions(network="CM",
                            station="BAR2,RUS,URMC",
                            location="*",
                            channel="*",
                            starttime=UTCDateTime("2019-04-23T00:00:00.0"),
                            endtime=UTCDateTime("2019-04-23T02:00:00.0"),
                            chunklength_in_sec=3600,
                            overlap_in_sec=None,
                            groupby='{network}.{station}.{channel}')

    ppc_restrictions = PreprocRestrictions(seed_ids=['CM.BAR2'],
                            order=['detrend','taper','applyfilter'],
                            detrend={'type':'simple'},
                            taper={'max_percentage':0.05,
                                        'type':"hann"},
                            applyfilter={'type':'highpass', 'freq':1.3})

    mseed_storage = ("/home/ecastillo/downloads/"
                    "{network}/{station}/{network}.{station}.{location}.{channel}__{starttime}__{endtime}{ppc}.mseed")

    MseedDownloader(mseed_storage,client,dld_restrictions,
                    ppc_restrictions,
                    n_processor=4,concurrent_feature="t")

    # import obspy
    # st = obspy.read("/home/ecastillo/downloads/CM/BAR2/CM.BAR2.10.HNE__20190423T010000Z__20190423T020000Z.ppc.mseed")
    # st.plot()