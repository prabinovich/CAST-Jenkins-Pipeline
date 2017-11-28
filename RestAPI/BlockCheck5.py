# Python 

# update configurations as appropriate
_connection_ = 'http://34.205.9.185:8080/CAST-AAD-AED/rest/'
_auth_ = ('cast', 'cast')

import os
import sys
import argparse
import requests

BUS_CRITERIA = {}

def check_rule(_rule, _app,  auth, apiurl):
    """ put the logic in here """
    headers = {'Accept':'application/json'}

    print('->' +str( headers) + ' ->' + str(apiurl))
    print('Rule is :' + str(_rule))

    print('Credentials: ', auth)
 
    if _rule == "new_vs_old":
        RESTCALL = 'AAD/results?select=(evolutionSummary)&quality-indicators=(60017)&snapshots=(-1)&applications=(' +_app + ')'
        print('RESTCALL: ', RESTCALL)
        try:
            data = requests.get(apiurl+RESTCALL, headers = headers, auth=auth, verify=False)
            BUS_CRITERIA = data.json()
        except:
            print('Failed on RESTAPI')
        try:
            _results = (BUS_CRITERIA[0])
        except IndexError:
            print("Likely invalid application name")
            return(100)             
        _data = _results.get('applicationResults')
        _results = _data[0].get('result')
        _added =    _results.get('evolutionSummary').get('addedCriticalViolations')
        _removed =  _results.get('evolutionSummary').get('removedCriticalViolations')
        print(str(_added) + ' violations added, and  ' + str(_removed) + ' were removed')
        if _added <= _removed:
            print(str(_added) + ' were added and ' + str(_removed) + ' were removed')
            return(0)
        else:
            print('build failed')
            return(10)
    if _rule == "TQI_change":
        try:
            RESTCALL = "AAD/applications"
            data = requests.get(apiurl+RESTCALL, headers = headers, auth=auth, verify=False)
            BUS_CRITERIA = data.json()

        except:
            print('Failed on RESTAPI')  
        
        print(pp.pprint(BUS_CRITERIA))
        _results = (BUS_CRITERIA[0])
        _added =    _results.get('result').get('applicationResults').get('evolutionSummary').get('addedCriticalViolations')
        _removed =  _results.get('result').get('applicationResults').get('evolutionSummary').get('removedCriticalViolations')
        print(str(_added) + ' ' + str(_removed))
		
        if _added <= _removed:
            return(0)
        else:
            return(10)        
    else:
        print("invalid rule - failing")
        return(10)              


if __name__ == "__main__":
    """ Access RESTAPI, then check results """
    apiurl = ''
    curr_dir = os.getcwd()
    overridepath = curr_dir
    parser = argparse.ArgumentParser(description="""\n\nCAST Blocking Rule Check - \n Reads RestAPI, Pulls scores, runs a test and returns 0 if all is ok, and 10 if not""")
    parser.add_argument('-a', '--appname', action='store', dest='app_name', required=True,
                        help='Name of the target application as shown in AAD')		
    parser.add_argument('-r', '--rule', action='store', dest='rule', required=False, default="new_vs_old",
                        choices=['new_vs_old', 'TQI_change'],
                        help='Pre-defined rule number that will be evaluated for success')
    parser.add_argument('-l', '--logging', action='store', dest='ext_log', default='debug',
                        choices=['debug', 'info'],
                        help='Show log on the console when set to debug')
    parser.add_argument('-v','--version', action='version', version='%(prog)s 1.0')
    results = parser.parse_args()

    _rule = results.rule
    app_name = results.app_name

    _result_code = check_rule(_rule, app_name, _auth_, _connection_)
    print('exit code is ' + str(_result_code))
    sys.exit(_result_code)