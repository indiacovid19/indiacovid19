COVID19IN
=========

This repository contains the source code for the COVID-19 India
data page at <https://covid19in.github.io/>.

The data page at the above URL is generated from the following JSON
file: [`indiacovid19.json`][1].

This JSON file contains a list of lists (6-tuples). Each 6-tuple
contains a date string in `YYYY-MM-DD HH:MM` format format followed by
five numbers and a reference archive link. The five numbers are in the
following order: the number of active cases, the number of recoveries,
the number of deaths, and the number of migrated cases. If we add these
five numbers, we get the number of total cases for each day.

To contribute to this repository, please update [`indiacovid19.json`][1]
and send a pull request.

[1]: indiacovid19.json


Reference Archive Links
-----------------------

The last value in each 6-tuple occurring in [`indiacovid19.json`][1] is
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
archive URLs. However, a few exceptions have been made where the data in
the JSON file differs slightly from the one in the reference link. Such
exceptions are described in the [Exceptions](#exceptions) section below.


Exceptions
----------

In the following cases, the data in [`indiacovid19.json`][1]
differs slightly from the data in the reference links documented above:

- 2020-03-25 20:57: The WoM reference link shows 554 active
  cases on this date. However, the MoHFW website showed 553 active cases
  as the latest update on the same day. It appeared that this
  discrepancy was due to an error in the WoM data which was likely
  caused by the fact that the 1 migrated case (as per MoHFW) had not
  been counted as a recovered case in the WoM data. Unfortunately, there
  is no archive URL for the MoHFW website for this date. The number of
  active cases in the JSON file has been copied from the MoHFW website
  after manually verifying it at 23:59 IST on the same date. There was
  no discrepancy with respect to this total number of cases because this
  number was 606 on both websites.


License
-------

This is free and open source software. You can use, copy, modify,
merge, publish, distribute, sublicense, and/or sell copies of it,
under the terms of the MIT License. See [LICENSE.md][L] for details.

This software is provided "AS IS", WITHOUT WARRANTY OF ANY KIND,
express or implied. See [LICENSE.md][L] for details.

The [favicon.png](favicon.png) is generated from
<https://publicdomainvectors.org/en/free-clipart/Graph-icon/45340.html>
which is available in public domain.

[L]: LICENSE.md
