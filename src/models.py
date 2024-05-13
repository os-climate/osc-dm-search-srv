# Copyright 2024 Broda Group Software Inc.
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
#
# Created: 2024-04-22 by graeham.broda@gmail.com
from pydantic import BaseModel
from typing import Optional, List


class AddData(BaseModel):
    uuid: str
    name: str
    description: str


class QueryData(BaseModel):
    query: str


# Downloadable resource
class Resource(BaseModel):
    mimetype: str
    url: str

# Artifact (data reference)
class Artifact(BaseModel):
    uuid: Optional[str] = None
    productnamespace: Optional[str] = None
    productname: Optional[str] = None
    name: str
    description: str
    tags: List[str]
    license: str
    securitypolicy: str
    data: Optional[Resource] = None
    createtimestamp: Optional[str] = None
    updatetimestamp: Optional[str] = None