# Android Device Testing Framework ("dtf")
# Copyright 2013-2016 Jake Valletta (@jake_valletta)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""Integration tests for the "prop set" utility"""

from __future__ import absolute_import
import dtf.testutils as testutils


def test_no_args():

    """Running set with no args"""

    testutils.deploy_config(testutils.get_default_config())

    rtn = testutils.dtf("prop set")

    testutils.undeploy()

    assert(rtn.return_code == 0)


def test_set_a_prop():

    """Set an arbitrary property"""

    testutils.deploy_config(testutils.get_default_config())

    rtn = testutils.dtf("prop set Info magic AbraKadabra")

    testutils.undeploy()

    assert(rtn.return_code == 0)
