import asyncio
import json
import logging
import os

import uvloop
from aiohttp import web

from .caching import start_background_caching, NjTransitClient
from .helper import google_maps

from .routes import add_routes


def init_logger(logger_level):
    """
    Initialize the logger
    :param logger_level:
    :return:
    """
    logger_format = '%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s'
    logging.basicConfig(format=logger_format,
                        level=logger_level,
                        datefmt='%d-%m-%Y:%H:%M:%S')


def get_all_stations(stations_file: str) -> dict:

    with open(stations_file) as fp:
        return json.load(fp)


async def init_app() -> web.Application:
    """
    Initializes the application
    :return web.Application object
    """
    init_logger(os.environ.get('LOGGING_LEVEL', logging.INFO))

    event_loop = uvloop.new_event_loop()
    asyncio.set_event_loop(event_loop)

    app = web.Application()

    # Checking if maps can be used for validation and zipcode lookup
    google_maps_key = os.environ.get('GOOGLE_MAPS_APIKEY', None)
    if google_maps_key:
        logging.error("Google Maps service available")
        app['google_maps'] = google_maps.GoogleMaps(google_maps_key)
    else:
        logging.error("Google Maps service NOT available")

    app["all_stations"] = get_all_stations("./stationname_with_station2char.json")
    app["njt_client"] = NjTransitClient(app["all_stations"])
    #app.on_startup.append(start_background_caching)
    # Adding routes
    add_routes(app)
    return app
