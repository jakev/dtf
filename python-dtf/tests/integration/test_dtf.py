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
"""Integration tests for the general launcher"""

from __future__ import absolute_import
import dtf.testutils as testutils


def test_dtf():

    """Just attempt to run dtf"""

    rtn = testutils.dtf("")
    assert(rtn.return_code == 255)


def test_version():

    """Attempt to obtain version"""

    rtn = testutils.dtf("--version")
    assert(rtn.return_code == 0)

    rtn = testutils.dtf("-v")
    assert(rtn.return_code == 0)

    rtn = testutils.dtf("version")
    assert(rtn.return_code == 0)


def test_help():

    """Attempt to print help/useage"""

    rtn = testutils.dtf("--help")
    assert(rtn.return_code == 0)

    rtn = testutils.dtf("-h")
    assert(rtn.return_code == 0)

    rtn = testutils.dtf("help")
    assert(rtn.return_code == 0)

def test_non_project():

    """Attempt to run a built-in without a .dtfini"""

    rtn = testutils.dtf("archive")
    assert(rtn.return_code == 253)


def test_python_precheck_sdk_missing():

    """Attempt to run python module with missing SDK"""

    testutils.deploy_config_raw("")

    rtn = testutils.dtf("archive")

    testutils.undeploy()

    assert(rtn.return_code == 248)


def test_python_load_imp_exception():

    """Attempt to run builtin and fail to parse load_imp"""

    testutils.deploy_config_raw("")

    rtn = testutils.dtf("status")

    testutils.undeploy()

    assert(rtn.return_code == 247)
