#!/usr/bin/python
#
# Distributed under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
#
"""
Inspired by easybuild EnhancedTestCase from test.framework.utilities

@author: Stijn De Weirdt (Ghent University)
"""

import logging
import os
import shutil
import tempfile


from unittest import TestCase
from vsc.utils.run import run_asyncloop


def gen_test_func(profile, regexps_tuples):
    """Test function generator"""
    def test_func(self):
        self.makeResult(profile)
        for descr, compiled_regexps in regexps_tuples:
            for idx, compiled_regexp in enumerate(compiled_regexps):
                msg = "%s (%03d) pattern %s output\n%s" % (descr, idx, compiled_regexp.pattern, self.result)
                self.assertTrue(compiled_regexp.search(self.result), msg)
    return test_func


class RegexpTestCase(TestCase):
    """Dedicated testcase class for handling regular expressions for config-templates-metaconfig"""
    SERVICE = None  # name of service
    PROFILEPATH = None  # absolute path of profiles folder
    TEMPLATEPATH = None  # absolute path of templates folder
    JSON2TT = None  # absolute path to the json2tt.pl tool

    def setUp(self):
        """Set up testcase."""
        self.tmpdir = tempfile.mkdtemp()

    def makeResult(self, profile):
        """Compile the profile from SERVICE and run the template toolkit on it"""
        tmpdir = self.tmpdir

        # stupid bug in panc
        cwd = os.getcwd()
        os.chdir(self.PROFILEPATH)

        cmd = ['panc', '--formats' , 'json', '--output-dir', tmpdir, "%s.pan" % profile]
        ec, out = run_asyncloop(cmd)

        # change back
        os.chdir(cwd)

        jsonfile = os.path.join(tmpdir, "%s.json" % profile)
        if not os.path.exists(jsonfile):
            logging.error("No json file found for service %s and profile %s. cmd %s output %s" % (self.SERVICE, profile, cmd, out))

        cmd = ['perl', self.JSON2TT, '--json', jsonfile, '--unittest', '--includepath', self.TEMPLATEPATH]
        ec, out = run_asyncloop(cmd)
        if ec > 0:
            logging.error("json2tt exited with non-zero ec %s: %s" % (ec, out))

        self.result = out


    def tearDown(self):
        """Clean up after running testcase."""
        try:
            shutil.rmtree(self.tmpdir)
        except OSError, err:
            pass
