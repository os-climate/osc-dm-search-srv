# Copyright 2024 Broda Group Software Inc.
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
#
# Created: 2024-05-02 by graeham.broda@gmail.com
import sys, os
testdir = os.path.dirname(__file__)
srcdir = '../src'
sys.path.insert(0, os.path.abspath(os.path.join(testdir, srcdir)))

from src.state import get_global, remove_global, add_global

class TestState:
    def test_add(self):
        add_global("test_param", "test_val")
        res = get_global("test_param")
        assert res == "test_val"

    def test_get(self):
        add_global("test_param", "test_val")
        res = get_global("test_param")
        assert res == "test_val"

    def test_remove(self):
        add_global("test_param", "test_val")
        res = get_global("test_param")
        assert res == "test_val"
        res = remove_global("test_param")
        assert res is None

