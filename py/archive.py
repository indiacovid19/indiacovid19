#!/usr/bin/python3

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


class Data:
    """Container for all data read and derived from source JSON."""
    def __init__(self):
        # Master data map.
        self.master = {
        }

        # Reference metadata.
        self.dates = []
        self.refs = []

        # Cumulative totals until each date.
        self.active_cases = []
        self.cured_cases = []
        self.death_cases = []
        self.total_cases = []

        # Increment or decrement w.r.t. previous day for each date.
        self.active_diffs = []
        self.cured_diffs = []
        self.death_diffs = []
        self.total_diffs = []

        # Cured and death percents within closed cases.
        self.cured_percents = []
        self.death_percents = []
        self.cured_ratios = []

        # Growth w.r.t previous day for each date.
        self.active_growths = [-1]
        self.cured_growths = [-1]
        self.death_growths = [-1]
        self.total_growths = [-1]
        self.doubling_times = [-1]

        # Date and time as Python objects instead of strings.
        self.datetimes = []
        self.last_ref_datetimes = []


def load(ignore_dates=()):
    """Load data from JSON and populate module variables."""
    with open('indiacovid19.json') as f:
        entries = json.load(f)

    # Load entries into a dict to map each date to its entry and references.
    data = Data()
    for entry in entries:
        (date, active, cured, death, migrated,
         ref_date, ref_link, ref_comment) = entry

        if date in ignore_dates:
            continue

        if date not in data.master:
            data.dates.append(date)
            data.datetimes.append(datetime.datetime.strptime(date, '%Y-%m-%d'))
            data.master[date] = {'refs': []}

        data.master[date]['active'] = active
        data.master[date]['cured'] = cured + migrated
        data.master[date]['death'] = death
        data.master[date]['closed'] = cured + death + migrated
        data.master[date]['total'] = active + cured + death + migrated
        data.master[date]['refs'].append([ref_date, ref_link, ref_comment])

    # Split the dict into separate lists for use with matplotlib.pyplot.
    for date in data.dates:
        entry = data.master[date]
        # Case numbers.
        data.active_cases.append(entry['active'])
        data.cured_cases.append(entry['cured'])
        data.death_cases.append(entry['death'])
        data.total_cases.append(entry['total'])
        # Cured and death percents within closed cases.
        if entry['closed'] == 0:
            data.cured_percents.append(-1)
            data.death_percents.append(-1)
        else:
            data.cured_percents.append(100 * entry['cured'] / entry['closed'])
            data.death_percents.append(100 * entry['death'] / entry['closed'])
            assert data.cured_percents[-1] + data.death_percents[-1] == 100
        # Cured ratio.
        if entry['death'] == 0:
            data.cured_ratios.append(-1)
        else:
            data.cured_ratios.append(entry['cured'] / entry['death'])
        # List of references for each date.
        data.refs.append(entry['refs'])
        # Last reference time for each date.
        last_ref_time = entry['refs'][-1][0]
        if last_ref_time[:10] != date:
            last_ref_time = date + ' 23:59'
        last_ref_datetime = datetime.datetime.strptime(last_ref_time,
                                                       '%Y-%m-%d %H:%M')
        data.last_ref_datetimes.append(last_ref_datetime)

    # Populate increment/decrement in numbers for each date.
    data.active_diffs.append(data.active_cases[0])
    data.cured_diffs.append(data.cured_cases[0])
    data.death_diffs.append(data.death_cases[0])
    data.total_diffs.append(data.total_cases[0])
    for i in range(1, len(data.dates)):
        data.active_diffs.append(data.active_cases[i] -
                                 data.active_cases[i - 1])
        data.cured_diffs.append(data.cured_cases[i] -
                                data.cured_cases[i - 1])
        data.death_diffs.append(data.death_cases[i] -
                                data.death_cases[i - 1])
        data.total_diffs.append(data.total_cases[i] -
                                data.total_cases[i - 1])
        data.active_growths.append(calc_growths(data.active_cases[i - 1],
                                                data.active_cases[i]))
        data.cured_growths.append(calc_growths(data.cured_cases[i - 1],
                                               data.cured_cases[i]))
        data.death_growths.append(calc_growths(data.death_cases[i - 1],
                                               data.death_cases[i]))
        data.total_growths.append(calc_growths(data.total_cases[i - 1],
                                               data.total_cases[i]))
        data.doubling_times.append(calc_doubling_time(data, i))
    return data


def calc_growths(prev_num, curr_num):
    """Calculate the percentage growth of curr_num over prev_num."""
    if prev_num == 0:
        return -1  # -1 represents undefined growth.
    else:
        return 100 * (curr_num - prev_num) / prev_num


def calc_doubling_time(data, i):
    """Calculate the number of days it took for total cases to double."""
    n3 = data.total_cases[i]
    t3 = data.last_ref_datetimes[i]
    for n1, t1 in zip(data.total_cases[i::-1],
                      data.last_ref_datetimes[i::-1]):
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
    data = load()
    for a, b, c, d, e in zip(data.dates, data.total_cases, data.total_diffs,
                             data.total_growths, data.doubling_times):
        print('{} {:6} {:+6} ({:+4.1f}%) ({:2.1f} d)'.format(a, b, c, d, e))


if __name__ == '__main__':
    main()
