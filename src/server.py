# Copyright 2024 Broda Group Software Inc.
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
#
# Created: 2024-04-22 by graeham.broda@gmail.com
# Library imports
import json
import logging
from typing import Optional
import configparser

import uvicorn as uvicorn
from fastapi import FastAPI, Request, WebSocket, HTTPException
from pydantic import BaseModel
import yaml

# Project imports
from models import AddData, QueryData
import utilities
from state import add_global, remove_global, get_global

# Set up logging
LOGGING_FORMAT = \
    "%(asctime)s - %(module)s:%(funcName)s %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=LOGGING_FORMAT)
logger = logging.getLogger(__name__)

# Set up server
app = FastAPI()

# Constants
ENDPOINT_PREFIX = "/api"
DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8000

# Setup database instance
from searchdb import SearchDb
db: SearchDb = None


#####
# ENDPOINTS
#####


@app.post(ENDPOINT_PREFIX + "/search/add")
async def add(
        params: AddData
):
    """
    Add data to the database
    """
    print("in server")
    logger.info(f"Received request with query:{params}")
    try:
        db.add_data(params.uuid, params.name, params.description)
        logger.info("data added")
    except Exception as e:
        msg = f"Unknown exception:{e}"
        logger.error(msg)
        raise HTTPException(status_code=500, detail=msg)


@app.post(ENDPOINT_PREFIX + "/search/query")
async def search(
        params: QueryData
):
    """
    Execute a search based upon the provided query
    """
    logger.info(f"Received request with query:{params.query}")
    try:
        res = db.search(params.query)
    except Exception as e:
        msg = f"Unknown exception:{e}"
        logger.error(msg)
        raise HTTPException(status_code=500, detail=msg)

    return {
        "data": res
    }


@app.post(ENDPOINT_PREFIX + "/search/query/artifacts")
async def search_artifacts(
        params: QueryData
):
    """
    Execute a search absed upon the provided query
    """
    logger.info(f"Received request with query:{params.query}")
    try:
        res = db.search_artifacts(params.query)
    except Exception as e:
        msg = f"Unknown exception:{e}"
        logger.error(msg)
        raise HTTPException(status_code=500, detail=msg)

    return {
        "data": res
    }

#####
# INTERNAL
#####


async def _load(param1, param2):
    """
    Load data from registrar
    """
    logger.info(f"Loading data param1:{param1} param2:{param2}")

    try:
        conf = get_global("config")
        host = conf["registrar"]["host"]
        port = conf["registrar"]["port"]
        service = conf["registrar"]["service"]
        method = conf["registrar"]["method"]
        response = await utilities.httprequest(host, port, service, method)

        # response = await utilities.httprequest(host, port, service, method)

        for element in response:
            logger.info("adding element: {}".format((element["uuid"], element["name"], element["description"])))
            db.add_data(element["uuid"], element["name"], element["description"])
    except Exception as e:
        logger.error(f"Error loading data, exception:{e}")


async def _repeat_every(interval_sec, func, *args):
    """
    Setup a periodically called function
    """
    import asyncio
    while True:
        await func(*args)
        await asyncio.sleep(interval_sec)


@app.on_event("startup")
async def startup_event():
    """
    At startup, immediately load data and then periodically thereafter
    """
    conf = get_global("config")
    logger.info("Running startup event")
    param1 = "fake param 1"
    param2 = "fake param 2"
    await _load(param1, param2)  # Immediate invocation at startup
    import asyncio
    asyncio.create_task(_repeat_every(conf["server"]["load_interval_seconds"], _load, param1, param2))  # Periodic invocation


#####
# MAINLINE
#####


if __name__ == "__main__":
    # Set up argument parsing
    import argparse
    import os

    parser = argparse.ArgumentParser(description="Run the FastAPI server.")
    parser.add_argument("--host", type=str, default=DEFAULT_HOST, help=f"Host for the server (default: {DEFAULT_HOST})")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"Port for the server (default: {DEFAULT_PORT})")
    parser.add_argument("--configuration", help=f"Configuration file")
    args = parser.parse_args()

    logger.info(f"Using current working directory:{os.getcwd()}")
    logger.info(f"arg config: {args.configuration}")
    logger.info(f"dir contents: {os.listdir('./config')}")

    # Read the configuration file
    configuration = None
    with open(args.configuration, 'r') as file:
        add_global("config", yaml.safe_load(file))


    configuration = get_global("config")
    logger.info("config: {}".format(configuration))
    # Setup the database
    db = SearchDb(configuration["database"]["db_location"],
                  configuration["database"]["collection_name"],
                  bool(configuration["database"]["persist"]),
                  configuration["registrar"])



    # Start the server
    try:
        logger.info(f"START: service on host:{args.host} port:{args.port}")
        uvicorn.run(app, host=args.host, port=args.port)
    except Exception as e:
        logger.info(f"Stopping server, exception:{e}")
    finally:
        logger.info(f"DONE: Starting service on host:{args.host} port:{args.port}")