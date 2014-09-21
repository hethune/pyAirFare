## PyAirFAre

Allow you query flight fares from command line

### Usage
* Get an api key from `https://developers.google.com/qpx-express/v1/prereqs`
* Replace `__API_KEY__` in `queryUtil.api' with your api key

* run `query.py --from <origin1, origin2...> -to <dest1, dest2...> --startDate <YYYY-MM-DD> --startDateRange <int> --returnDate <YYYY-MM-DD> --returnDateRange <int> --alliance <STAR, SKYTEAM, ONEWORLD>`

* The results will be stored in a html file under `data/html`

### Parameters

* `from`: an array of departing airports
* `to`: an array of destination airports
* `startDate`: the startDate of the trip, in the format of YYYY-MM-DD
* `startDateRange`: an indicator of flexibility, for example, if your startDate is 2014-09-29, startDateRange is 2, this will query
departing flights on 2014-09-29 and 2014-09-30
* `returnDate` (optional): the return date of the trip
* `returnDateRange` (optional):an indicator of flexibility, for example, if your returnDate is 2014-09-29, returnDateRange is 2, this will query
returning flights on 2014-09-29 and 2014-09-30
* `alliance` (optional): preferred alliance. "STAR" or "SKYTEAM" or "ONEWORLD"

### example
#### Query:
`./query.py --from "pek, hkg" --to "sfo" --startDate "2015-01-03" --startDateRange 2 --alliance "STAR"`

#### Output
![Output HTML Screenshot](https://www.dropbox.com/s/mdycsyhla4ndj0q/Screenshot%202014-09-21%2015.05.51.png?dl=0)