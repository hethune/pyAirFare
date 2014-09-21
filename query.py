#!/usr/bin/python
import sys, getopt

from datetime import datetime
from queryUtil import queryRoundTrip, queryOneWayTrip
from pprint import pprint

def usage():
    print 'query.py --from <origin1, origin2...> -to <dest1, dest2...> --startDate <YYYY-MM-DD> --startDateRange <int> --returnDate <YYYY-MM-DD> --returnDateRange <int> --alliance <STAR, SKYTEAM, ONEWORLD>'

def readParms(argv):
    origin = ''
    destination = ''
    startDate = ''
    returnDate = ''
    startDateRange = None
    returnDateRange = None
    alliance = ""
    try:
        opts, args = getopt.getopt(argv,"f:t:s:sr:a:r:rr",["from=","to=","startDate=","startDateRange=", "alliance=","returnDate=","returnDateRange="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-f", "--from"):
            origin = arg
        elif opt in ("-t", "--to"):
            destination = arg
        elif opt in ("-s", "--startDate"):
            startDate = datetime.strptime(arg, "%Y-%m-%d")
        elif opt in ("-sr", "--startDateRange"):
            startDateRange = int(arg)
        elif opt in ("-a", "--alliance"):
            alliance = arg
        elif opt in ("-r", "--returnDate"):
            returnDate = datetime.strptime(arg, "%Y-%m-%d")
        elif opt in ("-sr", "--returnDateRange"):
            returnDateRange = int(arg)

    if origin == '' or destination == '' or startDate == '' or startDateRange == None:
        usage()
        sys.exit(2)

    return {'origin': origin, 'destination': destination, 'startDate':startDate, 'startDateRange':startDateRange, 'alliance': alliance, 'returnDate': returnDate, 'returnDateRange': returnDateRange}


def main(argv):
    parms = readParms(argv)
    origins = map(str.strip, parms['origin'].split(','))
    destinations = map(str.strip, parms['destination'].split(','))
    startDate = parms['startDate']
    returnDate = parms['returnDate']
    startDateRange = parms['startDateRange']
    returnDateRange = parms['returnDateRange']
    alliance = parms['alliance']

    if (not destinations or returnDate == ''):
        pass
        # queryOneWayTrip(origins, destinations, startDate, startDateRange, alliance)
    else:
        queryRoundTrip(origins, destinations, startDate, startDateRange, returnDate, returnDateRange, alliance)


if __name__ == "__main__":
   main(sys.argv[1:])
