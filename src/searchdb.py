# Copyright 2024 Broda Group Software Inc.
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
#
# Created: 2024-04-22 by graeham.broda@gmail.com
import chromadb
import chromadb.utils.embedding_functions as embedding_functions
import utilities
import constants
# from bgsexception import BgsException
# from state import get_global

import os
import uuid
import logging
logger = logging.getLogger(__name__)


class SearchDb():

    def __init__(self,
                 source_location: str,
                 collection_name: str,
                 persist: bool,
                 registrar: dict
                 ):


        if persist:
            self.client = chromadb.PersistentClient(path=source_location)
        else:
            self.client = chromadb.Client()
        self.collection_name = collection_name

        embeddings = embedding_functions.OpenAIEmbeddingFunction(
            api_key=os.environ.get('OPENAI_API_KEY'),
            model_name="text-embedding-ada-002"
        )

        self.collection = self.client.get_or_create_collection(name=self.collection_name, embedding_function=embeddings)
        self.registrar = registrar

    def add_data(self, _id: str, name: str, description: str):
        '''

        :param id: identifier of the data product
        :param name: name of the data product
        :param description: description of the data product which will be searched on
        :return:
        '''
        meta = {
            "name": name,
            "id": _id
        }
        self.collection.add(
            documents=description,
            metadatas=meta,
            ids=str(uuid.uuid4())
        )

    def search(self, query, n_results=1):

        logger.info("query: {}".format(query))
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        logger.info("results: {}".format(results))
        res = []
        if len(results) != 0:
            for index, _ in enumerate(results["ids"][0]):
                structured_result = {
                    "data": results["documents"][0][index],
                    "metadata": results["metadatas"][0][index]
                }
                res.append(structured_result)

        logger.info("output res: {}".format(res))
        return res

    # async def search_artifacts(self, query, n_results=1):
    async def search_artifacts(self, query, n_results=1):
        results = self.search(query, n_results=n_results)

        if len(results) == 0:
            return results

        res = []
        for result in results:
            host = "osc-dm-proxy-srv"
            port = 8000
            _uuid = result["metadata"]["id"]
            service = f"/api/dataproduct/discovery/uuid/{_uuid}/artifacts"
            logger.info(f"service being called: {service}")
            method = "GET"

            headers = {
                constants.HEADER_USERNAME: constants.USERNAME,
                constants.HEADER_CORRELATION_ID: str(uuid.uuid4())
            }
            response = await utilities.httprequest(
                host, port, service, method, headers=headers)
            formatted = []
            for element in response:
                logger.info(f"artifact: {element}")
                formatted.append(element)

            logger.info("output from artifact query: {}".format(response))
            result["artifact"] = formatted
            res.append(result)
        #  search the artifacts for this uuid


        logger.info("final output: {}".format(res))
        return results
