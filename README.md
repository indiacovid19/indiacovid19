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
[ "2020-03-20", 196, 22, 4, 1, "2020-03-20 17:00",
  "https://web.archive.org/web/20200320173607/https://www.mohfw.gov.in/" ]
```

Here is a description of these 7 values in the order they appear in each
septuple:

 1. Date (in "YYYY-MM-DD" format)
 2. Number of active cases
 3. Number of cured cases
 4. Number of death cases
 5. Number of migrated cases
 6. Last updated time as found in the source of the data
    (in "YYYY-MM-DD HH:MM" format)
 7. Reference archive link of the source of the data as supporting
    evidence

To contribute to this repository, please update [`indiacovid19.json`][1]
and send a pull request.

[1]: indiacovid19.json


Reference Archive Links
-----------------------

The last value in each septuple occurring in [`indiacovid19.json`][1] is
a reference archive link. These links point to reliable archives
(snapshots) of either <https://www.mohfw.gov.in/> (MoHFW) or
<https://www.worldometers.info/coronavirus/> (WoM) for the corresponding
date. Archive URLs of MoHFW is preferred if available. Archive URLs of
WoM is used only if a suitable one for MoHFW is unavailable. The entries
in this file are written with the following syntax:

The date and time for each entry is picked from the content of the
snapshot.

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
