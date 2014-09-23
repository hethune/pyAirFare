from datetime import timedelta, date
from compiler.ast import flatten
from itertools import chain
from re import sub
from pprint import pprint
import time
import requests
import json
import smtplib
import math
from email.mime.text import MIMEText

__API_KEY__ = "" # Replace with your google api key

def saveToFile(data, fileName):
    with open(fileName, 'w') as outfile:
        json.dump(data, outfile)

def saveTextToFile(text, fileName):
    with open(fileName, 'w') as outfile:
        outfile.write(text)

def html_table(lol):
    html = '''
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.2.0/css/bootstrap.min.css">
    <script type="text/javascript" src="http://code.jquery.com/jquery-2.1.1.min.js"></script> 
    <script type="text/javascript" src="https://raw.githubusercontent.com/christianbach/tablesorter/master/jquery.tablesorter.min.js"></script>
    '''
    html += '<div class="row">'
    html += '<div class="col-md-8">'
    html += '<table id="flightsTable" class="table tablesorter">'
    html += '''
    <thead> 
    <tr>    
    <th> Date </th>
    <th> From </th>
    <th> To </th>
    <th> Price </th>
    <th> Duration(mins) </th>
    <th colspan="20"> Flight Segments (From, To, Flight Number, Class, Remaining Tickets</th>
    </tr></thead> 
    <tbody>
    '''
    for sublist in lol:
        sublist = flatten(sublist)
        sublist = [list(chain(x.values())) if type(x) is dict else x for x in sublist]
        sublist = flatten(sublist)
        html += '  <tr><td>'
        html += '    </td><td>'.join(list(map(lambda x: str(x), sublist)))
        html += '  </td></tr>'
    html += '</tbody></table>'
    html += '</div><div class="col-md-4">'
    html += '</div></div>'

    html += '''
    <script>
    $(document).ready(function() 
    { 
        $("#flightsTable").tablesorter(); 
    } 
    ); 
    </script>
    '''

    return html

def sendToNumber(data_list, numbers):
    return
    recipients = list(map((lambda x: str(x) + "@txt.att.net"), numbers))

    GMAIL_USERNAME = ""
    GMAIL_PASSWORD = ""
    session = smtplib.SMTP('smtp.gmail.com', 587)
    session.ehlo()
    session.starttls()
    session.login(GMAIL_USERNAME, GMAIL_PASSWORD)

    email_subject = "Flight price alert"

    for recipient in recipients:
        headers = "\r\n".join(["from: " + GMAIL_USERNAME,
                           "subject: " + email_subject,
                           "to: " + recipient,
                           "mime-version: 1.0",
                           "content-type: text/html"])
        content = headers + "\r\n\r\n"
        for data in data_list:
            body = generateEmailContent(data)
            content += body + "\r\n\r\n"
        print 'sending to ' + recipient
        session.sendmail(GMAIL_USERNAME, recipient, content)

def generateEmailContent(data):
    origin = ''
    destination = ''
    startDate = ''
    returnDate = ''
    flights = ''
    try:
        origin = data['origin']
        destination = data['destination']
        startDate = data['startDate']
        returnDate = data['returnDate']
    except KeyError:
        pass

    for idx, slice in enumerate(data['slice']):
        try:
            price = slice['saleTotal']
            tmp = "flight " + str(idx+1) + ":"
            for segment in slice['flights']:
                for flight in segment:
                    tmp += flight['flight'] + " class:" + flight['class'] + " remaining:" + str(flight['remaining']) + " "
            flights += tmp + price + "  "
        except KeyError:
            pass
    msg = "Flights from " + origin + " to " + destination + " between " + startDate + " and " + returnDate + ": " + flights
    return msg

def generateList(data):
    results = []
    for slice in data['slice']:
        result = []
        result.append(data['startDate'])
        result.append(data['origin'])
        result.append(data['destination'])
        result.append(slice['saleTotal'])
        result.append(slice['duration'])
        result.append(slice['flights'])
        results.append(result)
    return results

def generateRequestJSON(origin, destination, maxStop, date, alliance = "", maxConnectionDuration = 300):
    request = {"request": {
        "passengers": {},
        "solutions": 0,
        "refundable": False,
        "slice": []
    }}

    dateString = list(map((lambda x: x.strftime("%Y-%m-%d")), date))

    request['request']['passengers'] = {
        "adultCount": 1,
        "infantInLapCount": 0,
        "infantInSeatCount": 0,
        "childCount": 0,
        "seniorCount": 0
    }
    request['request']["solutions"] = 100
    request['request']['refundable'] = False
    request['request']['saleCountry'] = 'US'

    request['request']['slice'] = []
    request['request']['slice'].append({
        "origin": origin,
        "destination": destination,
        "date": dateString[0],
        "maxStops": maxStop,
        "maxConnectionDuration": maxConnectionDuration,
        "prohibitedCarrier": ["CI", "BR"]
    })

    if alliance in ["STAR", "ONEWORLD", "SKYTEAM"]:
        request['request']['slice'][0]['alliance'] = alliance

    # if there's a return date....
    if len(dateString) <= 1:
        return request

    request['request']['slice'].append({
        "origin": destination,
        "destination": origin,
        "date": dateString[1],
        "maxStops": maxStop,
        "alliance": "STAR",
        "maxConnectionDuration": maxConnectionDuration
    })

    return request

def purify(raw_result, numberOfFlightsToShow, maxTripDuration):
    result = {}
    try:
        result['startDate'] = raw_result['startDate']
        result['returnDate'] = raw_result['returnDate']
        result['origin'] = raw_result['origin']
        result['destination'] = raw_result['destination']
        result['carrier'] = list(map((lambda x: x['code']), raw_result['trips']['data']['carrier']))
    except KeyError:
        pass

    # Get best price
    tmp_price_slice = []
    try:
        tmp_price_slice = sorted([x for x in raw_result['trips']['tripOption'] if sum(y['duration'] for y in x['slice']) < maxTripDuration], key=lambda trip: float(sub("[a-z]|[A-Z]", "", trip['saleTotal'])))[0:numberOfFlightsToShow]
    except KeyError:
        print "key error in soring price"
        pass

    price_slices = []
    for tmp in tmp_price_slice:
        price_slice = {}
        try:
            price_slice['saleTotal'] = float(sub("[a-z]|[A-Z]","", tmp['saleTotal']))
            price_slice['duration'] = sum(x['duration'] for x in tmp['slice'])
            price_slice['flights'] = list(map(lambda x: list(map(lambda y: {"flight": y['flight']['carrier'] + y['flight']['number'], "origin": y['leg'][0]['origin'],
                "destination": y['leg'][0]['destination'], "class": y['bookingCode'], "remaining": y['bookingCodeCount']}, x['segment'])), tmp['slice']))
        except KeyError:
            print "key error in price slice"
            pass
        price_slices.append(price_slice)
    result['slice'] = price_slices
    return result

def aggregate(purified_results, numberOfFlightsToShow):
    result = sorted(purified_results, key=lambda x: math.fsum(float(sub("[a-z]|[A-Z]","", y['saleTotal'])) for y in x['slice']))[0: numberOfFlightsToShow]
    return result

def queryRoundTrip(origins, destinations, startDate, startDateRange, returnDate, returnDateRange, alliance):
    requests = []
    results = []
    maxStops = 1
    maxConnectionDuration = 300
    for i in range(startDateRange):
        for j in range(returnDateRange):
            start = startDate + timedelta(days = i)
            end = returnDate + timedelta(days = j)
            for origin in origins:
                for destination in destinations:
                    print start, end, origin, destination
                    request = generateRequestJSON(origin, destination, maxStops, [start, end], alliance, maxConnectionDuration)
                    requests.append(request)
                    result = sendRequest(request)
                    result['startDate'] = start.strftime("%Y-%m-%d")
                    result['returnDate'] = end.strftime("%Y-%m-%d")
                    result['origin'] = origin
                    result['destination'] = destination
                    results.append(result)

    saveToFile(results, '/tmp/pyFare_round_trip_results_' + '_' + str(int(time.time())) + '.json')
    # Process raw data
    processResultJson(results, 0)

def queryOneWayTrip(origins, destinations, startDate, startDateRange, alliance):
    requests = []
    results = []
    maxStops = 1
    maxConnectionDuration = 300
    if not (alliance in ["STAR", "ONEWORLD", "SKYTEAM"]) :
        alliance = ""
    for i in range(startDateRange):
        start = startDate + timedelta(days = i)
        for origin in origins:
            for destination in destinations:
                print start, origin, destination
                request = generateRequestJSON(origin, destination, maxStops, [start], alliance, maxConnectionDuration)
                # pprint(request)
                requests.append(request)
                result = sendRequest(request)
                result['startDate'] = start.strftime("%Y-%m-%d")
                result['returnDate'] = ""
                result['origin'] = origin
                result['destination'] = destination
                results.append(result)

    saveToFile(results, '/tmp/pyFare_oneway_trip_results_' + origins[0] + '_' + time.strftime("%Y%m%d") + "_" + str(int(time.time())) + '.json')
    # Process raw data
    processResultJson(results, 1)


def processFile(fileName):
    results = []
    json_file = open(fileName)
    try:
        results = json.load(json_file)
    finally:
        json_file.close()
    processResultJson(results, 2)

def processResultJson(results, isOneWay = 2):
    purified_results = []

    maxTripDuration = 1200

    if isOneWay == 1:
        maxTripDuration = 1200
    elif isOneWay == 0:
        maxTripDuration = 2400
    elif isOneWay == 2:
        if results[0]['returnDate'] == '':
            maxTripDuration = 1200
        else:
            maxTripDuration = 2400

    for result in results:
        purified_results.append(purify(result, 5, maxTripDuration))

    aggregated_results = []
    for result in purified_results:
        aggregated_results += generateList(result)

    saveTextToFile(html_table(aggregated_results), 'data/html/' + time.strftime("%Y%m%d") + "-" + str(int(time.time())) + '.html')

    return aggregated_results

def sendRequest(request):
    headers = {'content-type': 'application/json'}
    # return {}
    r = requests.post("https://www.googleapis.com/qpxExpress/v1/trips/search?key=" + __API_KEY__, data=json.dumps(request), headers=headers)
    return r.json()
