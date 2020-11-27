if __name__ == "__main__":

    import sys
    module_path = "/home/ecastillo/repositories/AIpicker"
    sys.path.insert(0,module_path)

    from AIpicker.concurrent_downloader.mdl.bulk_downloader import BulkDownloader
    from obspy.clients.fdsn.mass_downloader.domain import RectangularDomain
    from obspy.clients.fdsn.mass_downloader import Restrictions
    from obspy.core.utcdatetime import UTCDateTime

    ##Definición del client
    IRIS_client = {"base_url":"IRIS", "user":"gaprietogo@unal.edu.co",
                        "password":"DaCgmn3hNjg"}  

    ##Definición de las restricciones
    YU_restrictions = Restrictions(starttime=UTCDateTime(2016, 8, 1),
                            endtime=UTCDateTime(2016, 8, 3),
                            network="YU", 
                            station="CS*",
                            location="*", channel="*",
                            chunklength_in_sec=86400,
                            reject_channels_with_gaps=False,
                            minimum_length=0.0,
                            minimum_interstation_distance_in_m=0.0,
                            channel_priorities=[],
                            location_priorities=[""])
    ##Dominio de carma
    domainR = RectangularDomain(minlatitude=6, maxlatitude=14,
                        minlongitude=-80, maxlongitude=-68)

    ## Almacenamiento
    ## Poner {<SDSdir>} al inicio para indicar que es formato SDS
    mseed_storage = ("{<SDSdir>}:/home/ecastillo/downloads/CARMA/waveforms")
    stationxml_storage = "/home/ecastillo/downloads/CARMA/stations/{network}/{station}.xml"

    #Instancie objeto y descargue
    bdl = BulkDownloader(client_dict=IRIS_client)

    bdl.download_by_station(domain=domainR,
                    restrictions=YU_restrictions, 
                    mseed_storage=mseed_storage,
                    stationxml_storage=stationxml_storage,
                    workers=4,parallel_mode="process")