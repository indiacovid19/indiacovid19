India COVID-19 Data Archive
===========================

This repository contains the source code for the COVID-19 India data
archive website at <https://indiacovid19.github.io/>. The website can
also be reached using the short link <https://git.io/indiacovid19>.

The data page at the above URL is generated from the following JSON
file: [`indiacovid19.json`][1].

This JSON file contains a list of list entries. Each inner list entry is
a septuple (7-tuple) consisting of 7 values. Here is an example entry:

```json
["2020-03-25", 553, 43, 10, "2020-03-25 18:45",
 "https://web.archive.org/web/20200325192939/https://www.mohfw.gov.in/", ""]
```

Here is a description of these 7 values in the order they appear in each
septuple:

 1. Date (in "YYYY-MM-DD" format as per Indian Standard Time)
 2. Number of active cases
 3. Number of cured cases
 4. Number of death cases
 5. Date and time at which the data was collected/published by the
    source of the data (in "YYYY-MM-DD HH:MM" format as per Indian
    Standard Time)
 6. Reference archive link of the source of the data as supporting
    evidence
 7. Any additional comment or note about the entry

To contribute to this repository, please update [`indiacovid19.json`][1] and
send a pull request.

[1]: indiacovid19.json


Reference Archive Links
-----------------------

The 7th value in each septuple occurring in [`indiacovid19.json`][1] is
a reference archive link. These links point to reliable archives
(snapshots) of either <https://pib.gov.in/> (PIB) or
<https://www.mohfw.gov.in/> (MoHFW) for the corresponding date. These
are the official sources of COVID-19 case numbers for India.

The date and time for each entry specified as the 6th value in each
entry is picked directly from the content of the archived snapshot.

The intention of this project is to ensure that every piece of data in
[`indiacovid19.json`][1] can be justified with evidence archived in the
archive URLs.


License
-------

This is free and open source software. You can use, copy, modify,
merge, publish, distribute, sublicense, and/or sell copies of it,
under the terms of the MIT License. See [LICENSE.md][L] for details.

This software is provided "AS IS", WITHOUT WARRANTY OF ANY KIND,
express or implied. See [LICENSE.md][L] for details.

The [favicon.png](static/favicon.png) is generated from
<https://publicdomainvectors.org/en/free-clipart/Graph-icon/45340.html>
which is available in public domain.

[L]: LICENSE.md
