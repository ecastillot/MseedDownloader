if __name__ == "__main__":

    import sys
    module_path = "/home/ecastillo/repositories/MseedDownloader"
    sys.path.insert(0,module_path)

    from concurrent_downloader.mdl.bulk_downloader import BulkDownloader
    from obspy.clients.fdsn.mass_downloader.domain import RectangularDomain
    from obspy.clients.fdsn.mass_downloader import Restrictions
    from obspy.core.utcdatetime import UTCDateTime

    ##Definición del client
    IRIS_client = {"base_url":"IRIS","user":None,"password":None}  

    ##Definición de las restricciones
    YU_restrictions = Restrictions(starttime=UTCDateTime(2010, 2, 25),
                            endtime=UTCDateTime(2016, 2, 27),
                            network="IU", 
                            station="ANMO",
                            location="00", channel="LHZ",
                            chunklength_in_sec=86400,
                            reject_channels_with_gaps=False,
                            minimum_length=0.0,
                            minimum_interstation_distance_in_m=0.0,
                            channel_priorities=[],
                            location_priorities=[""])
    ##Dominio de carma
    domainR = RectangularDomain(minlatitude=-90, maxlatitude=90,
                        minlongitude=-180, maxlongitude=180)

    ## Almacenamiento
    ## Poner {<SDSdir>} al inicio para indicar que es formato SDS
    mseed_storage = ("{<SDSdir>}:/home/ecastillo/downloads/IU/waveforms")
    stationxml_storage = "/home/ecastillo/downloads/IU/stations/{network}/{station}.xml"

    #Instancie objeto y descargue
    bdl = BulkDownloader(client_dict=IRIS_client)

    bdl.download_by_station(domain=domainR,
                    restrictions=YU_restrictions, 
                    mseed_storage=mseed_storage,
                    stationxml_storage=stationxml_storage,
                    workers=4,parallel_mode="thread")