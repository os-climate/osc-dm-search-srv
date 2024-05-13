# Copyright 2024 Broda Group Software Inc.
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
#
# Created: 2024-05-02 by graeham.broda@gmail.com
import pytest
import yaml

from  src.searchdb import SearchDb
from src.bgsexception import BgsException
# from state import gstate

db: SearchDb = None

class TestSearchdb:
    def test_add_data_successful(self):
        db = SearchDb("test",
                      "test",
                      False)
        data_id = "id1"
        db.add_data(data_id, "name1", "description1")
        res = db.search("description1")
        res_id = res[0]["metadata"]["id"]
        assert data_id == data_id


    def test_search(self):
        db = SearchDb("test",
                      "test",
                      False)
        data_id = "id2"
        db.add_data("1231231231", "name1", "this is a sample description, orange")
        db.add_data(data_id, "name2", "this is a sample description, purple")

        res = db.search("purple")
        res_id = res[0]["metadata"]["id"]
        assert data_id == data_id

    def test_search_no_results(self):
        db = SearchDb("test",
                      "test",
                      False)

        res = db.search("purple")
        assert len(res) == 0

