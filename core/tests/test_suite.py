# coding: utf-8
#
# Copyright 2014 The Oppia Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Oppia-ml test suite.

In general, this script should not be run directly. Instead, invoke
it from the command line by running

    bash scripts/run_backend_tests.sh

from the oppia/ root folder.
"""

# Pylint has issues with import order of argparse.
#pylint: disable=wrong-import-order
import argparse
import os
import sys
import unittest
#pylint: enable=wrong-import-order

import vmconf

CURR_DIR = os.path.abspath(os.getcwd())
THIRD_PARTY_DIR = os.path.join(CURR_DIR, 'third_party')
MANIFEST_FILE_PATH = os.path.join(os.getcwd(), 'manifest.txt')

with open(MANIFEST_FILE_PATH, 'r') as f:
    DIRS_TO_ADD_TO_SYS_PATH = [
        os.path.join(
            os.getcwd(), 'third_party',
            '%s-%s' % (line.split()[0], line.split()[1])
        ) for line in [x.strip() for x in f.readlines()]
        if line and not line.startswith('#')
    ]

DIRS_TO_ADD_TO_SYS_PATH.append(CURR_DIR)

_PARSER = argparse.ArgumentParser()
_PARSER.add_argument(
    '--test_target',
    help='optional dotted module name of the test(s) to run',
    type=str)


def create_test_suites(test_target=None):
    """Creates test suites. If test_dir is None, runs all tests."""
    if test_target and '/' in test_target:
        raise Exception('The delimiter in test_target should be a dot (.)')

    loader = unittest.TestLoader()
    return (
        [loader.loadTestsFromName(test_target)]
        if test_target else [loader.discover(
            CURR_DIR, pattern='*_test.py', top_level_dir=CURR_DIR)])


def main():
    """Runs the tests."""

    def _iterate(test_suite_or_case):
        """Iterate through all the test cases in `test_suite_or_case`."""
        try:
            suite = iter(test_suite_or_case)
        except TypeError:
            yield test_suite_or_case
        else:
            for test in suite:
                for subtest in _iterate(test):
                    yield subtest

    vmconf.PLATFORM = 'gce'
    # Set DEV_MODE to True so that application uses default communication url
    # and port.
    vmconf.DEV_MODE = True

    for directory in DIRS_TO_ADD_TO_SYS_PATH:
        if not os.path.exists(os.path.dirname(directory)):
            raise Exception('Directory %s does not exist.' % directory)
        sys.path.insert(0, directory)

    parsed_args = _PARSER.parse_args()
    suites = create_test_suites(parsed_args.test_target)

    results = [unittest.TextTestRunner(verbosity=2).run(suite)
               for suite in suites]

    tests_run = 0
    for result in results:
        tests_run += result.testsRun
        if result.errors or result.failures:
            raise Exception(
                'Test suite failed: %s tests run, %s errors, %s failures.' % (
                    result.testsRun, len(result.errors), len(result.failures)))

    if tests_run == 0:
        raise Exception('No tests were run.')


if __name__ == '__main__':
    main()
