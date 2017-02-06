__author__ = 'wiljoh'


import unittest
from test_pg_transmogrify import test_pg_transmogrify
import HTMLTestRunner
import os

# get the directory path to output report file
dir = os.getcwd()

# get transmogrify tests
peci_mogrify_tests = unittest.TestLoader().loadTestsFromTestCase( test_pg_transmogrify )
# create test suite
peci_test_suite = unittest.TestSuite( [peci_mogrify_tests] )

# open the report file
outfile = open( "peci_test_report.html", "w" )
# configure html report options
runner = HTMLTestRunner.HTMLTestRunner( stream=outfile ,
                                        title='peci fallback/commit test report',
                                        description='peci tests' )


# run test suite
runner.run( peci_test_suite )

