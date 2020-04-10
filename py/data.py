#!/usr/bin/python3

# Copyright (c) 2020 Susam Pal
# Licensed under the terms of the MIT License.

# The MIT License (MIT)
#
# Copyright (c) 2020 Susam Pal
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


import datetime
import json
import math
import re


# Master data map.
data = {
}

# Reference metadata.
dates = []
refs = []

# Cumulative totals until each date (directly available in indiacovid19.json).
active_cases = []
cured_cases = []
death_cases = []
total_cases = []

# Increment or decrement w.r.t. previous day for each date.
active_diff = []
cured_diff = []
death_diff = []
total_diff = []

# Cured and death percents within closed cases.
cured_percents = []
death_percents = []
cured_ratios = []


# Growth w.r.t previous day for each date.
active_growth = [-1]
cured_growth = [-1]
death_growth = [-1]
total_growth = [-1]
doubling_days = [-1]

# Date and time as Python objects instead of strings.
datetimes = []
last_ref_datetimes = []


def load():
    """Load data from JSON and populate module variables."""
    with open('indiacovid19.json') as f:
        entries = json.load(f)

    # Load entries into a dict to map each date to its entry and references.
    for i, entry in enumerate(entries):
        (date, active, cured, death, migrated,
         ref_date, ref_link, ref_comment) = entry

        if date not in data:
            dates.append(date)
            datetimes.append(datetime.datetime.strptime(date, '%Y-%m-%d'))
            data[date] = {'refs': []}

        data[date]['active'] = active
        data[date]['cured'] = cured + migrated
        data[date]['death'] = death
        data[date]['closed'] = cured + death + migrated
        data[date]['total'] = active + cured + death + migrated
        data[date]['refs'].append([i + 1, ref_date, ref_link, ref_comment])

    # Split the dict into separate lists for use with matplotlib.pyplot.
    for date in dates:
        entry = data[date]
        # Case numbers.
        active_cases.append(entry['active'])
        cured_cases.append(entry['cured'])
        death_cases.append(entry['death'])
        total_cases.append(entry['total'])
        # Cured and death percents within closed cases.
        if entry['closed'] == 0:
            cured_percents.append(-1)
            death_percents.append(-1)
        else:
            cured_percents.append(100 * entry['cured'] / entry['closed'])
            death_percents.append(100 * entry['death'] / entry['closed'])
            assert cured_percents[-1] + death_percents[-1] == 100
        # Cured ratio.
        if entry['death'] == 0:
            cured_ratios.append(-1)
        else:
            cured_ratios.append(entry['cured'] / entry['death'])
        # List of references for each date.
        refs.append(entry['refs'])
        # Last reference time for each date.
        last_ref_time = entry['refs'][-1][1]
        if last_ref_time[:10] != date:
            last_ref_time = date + ' 23:59'
        last_ref_datetime = datetime.datetime.strptime(last_ref_time,
                                                       '%Y-%m-%d %H:%M')
        last_ref_datetimes.append(last_ref_datetime)

    # Populate increment/decrement in numbers for each date.
    active_diff.append(active_cases[0])
    cured_diff.append(cured_cases[0])
    death_diff.append(death_cases[0])
    total_diff.append(total_cases[0])
    for i in range(1, len(dates)):
        active_diff.append(active_cases[i] - active_cases[i - 1])
        cured_diff.append(cured_cases[i] - cured_cases[i - 1])
        death_diff.append(death_cases[i] - death_cases[i - 1])
        total_diff.append(total_cases[i] - total_cases[i - 1])
        active_growth.append(calc_growth(active_cases[i - 1], active_cases[i]))
        cured_growth.append(calc_growth(cured_cases[i - 1], cured_cases[i]))
        death_growth.append(calc_growth(death_cases[i - 1], death_cases[i]))
        total_growth.append(calc_growth(total_cases[i - 1], total_cases[i]))
        doubling_days.append(calc_doubling_time(dates[i]))


def calc_growth(previous_number, current_number):
    """Calculate the ratio of current_number to previous_number."""
    if previous_number == 0:
        return -1  # -1 represents undefined growth.
    else:
        return current_number / previous_number


def calc_doubling_time(date):
    """Calculate the number of days it took for total cases to double."""
    i = dates.index(date)
    n3 = total_cases[i]
    t3 = last_ref_datetimes[i]
    for d1, n1, t1 in zip(dates[i::-1],
                          total_cases[i::-1],
                          last_ref_datetimes[i::-1]):
        if n1 <= n3/2:
            break
        n2 = n1
        t2 = t1
    else:
        return -1  # -1 represents undefined doubling time.
    seconds = ((t3 - t2).total_seconds() +
               (t2 - t1).total_seconds() * (n2 - n3/2) / (n2 - n1))
    days = seconds / 86400
    return days


def main():
    load()
    for a, b, c, d, e in zip(dates, total_cases, total_diff,
                             total_growth, doubling_days):
        print('{} {:5} {:+4} ({:+4.2f}) ({:2.1f} d)'.format(a, b, c, d, e))


if __name__ == '__main__':
    main()
