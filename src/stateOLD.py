# Copyright 2024 Broda Group Software Inc.
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
#
# Created: 2024-05-02 by graeham.broda@gmail.com
from typing import Any
"""
Dictionary containing global state
"""
global_state = {}

def add_global(key: str, val: Any):
    global_state[key] = val

def get_global(key: str) -> Any:
    return global_state[key]

def remove_global(key: str):
    del global_state[key]