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


"""Scrape https://www.mohfw.gov.in/ to retrieve COVID-19 statistics.

To run this scraper and print a summary of the scraped data, enter this
command at the top-level directory of this project:

    python3 -m py.mohfw
"""


import datetime
import json
import re
import sys
import urllib
import urllib.request

from py import log


class Data:
    def __init__(self):
        """Container for all data read and derived from MoHFW."""
        self.total = -1
        self.active = -1
        self.cured = -1
        self.death = -1
        self.ref_datetime = None
        self.ref_date = ''
        self.ref_time = ''
        self.regions = {}
        self.region_total = -1
        self.region_cured = -1
        self.region_death = -1
        self.region_active = -1


def load_home_data():
    """Return data retrieved from MoHFW website."""
    data = Data()

    # Save the response from MoHFW as a list of lines.
    url = 'https://www.mohfw.gov.in/'
    log.log('Connecting to {} ...', url)
    response = urllib.request.urlopen(url).read().decode('utf-8')
    lines = [l.strip() for l in response.splitlines()]
    lines = [l for l in lines if l != '']

    # Parsers.
    strong_re = re.compile(r'.*<strong.*?>([0-9]*).*<')
    time_re = re.compile(r'.*as on\s*:\s*(\d.*) IST')
    td_re = re.compile(r'.*<td>([^#]*).*</td>')
    parser_state = 'DEFAULT'

    # Parse the response.
    for i, line in enumerate(lines):
        if data.active == -1 and 'Active' in line:
            data.active = int(strong_re.match(lines[i + 1]).group(1))
        elif data.cured == -1 and 'Discharged' in line:
            data.cured = int(strong_re.match(lines[i + 1]).group(1))
        elif data.death == -1 and 'Deaths' in line:
            data.death = int(strong_re.match(lines[i + 1]).group(1))
        elif data.ref_datetime == None and 'as on' in line:
            t = time_re.match(line).group(1)
            data.ref_datetime = datetime.datetime.strptime(t, '%d %B %Y, %H:%M')
            data.ref_date = data.ref_datetime.strftime('%Y-%m-%d')
            data.ref_time = data.ref_datetime.strftime('%H:%M')

    data.total = data.active + data.cured + data.death
    return data


def load_region_data(home_data=None):
    """Return data retrieved from MoHFW data JSON."""
    data = Data()

    # Retrieve MoHFW JSON data.
    url = 'https://www.mohfw.gov.in/data/datanew.json'
    log.log('Connecting to {} ...', url)
    items = json.load(urllib.request.urlopen(url))

    # Parse the response.
    for item in items:
        region_name = item['state_name']
        total = int(item['new_positive'])
        active = int(item['new_active'])
        cured = int(item['new_cured'])
        death = int(item['new_death'])

        if region_name == '':
            data.region_total = total
            data.region_active = active
            data.region_cured = cured
            data.region_death = death
        else:
            if total != (active + cured + death):
                log.log('WARN: region: Total mismatch for {}', region_name)
            data.regions[region_name] = (total, active, cured, death)

    # Region totals.
    region_total_sum = sum(v[0] for v in data.regions.values())
    region_active_sum = sum(v[1] for v in data.regions.values())
    region_cured_sum = sum(v[2] for v in data.regions.values())
    region_death_sum = sum(v[3] for v in data.regions.values())

    # Validations.
    if home_data and data.region_total != home_data.total:
        log.log('WARN: region: Mismatch in region total and home total')
    if home_data and data.region_active != home_data.active:
        log.log('WARN: region: Mismatch in region active and home active')
    if home_data and data.region_cured != home_data.cured:
        log.log('WARN: region: Mismatch in region cured and home cured')
    if home_data and data.region_death != home_data.death:
        log.log('WARN: region: Mismatch in region death and home death')

    if data.region_total != region_total_sum:
        log.log('WARN: region: Mismatch in region total and calculated sum')
    if data.region_active != region_active_sum:
        log.log('WARN: region: Mismatch in region active and calculated sum')
    if data.region_cured != region_cured_sum:
        log.log('WARN: region: Mismatch in region cured and calculated sum')
    if data.region_death != region_death_sum:
        log.log('WARN: region: Mismatch in region death and calculated sum')

    return data


def make_json_entry(data):
    """Return JSON entry to be added to indiacovid19.json."""
    j = [
            data.ref_date,
            data.active,
            data.cured,
            data.death,
            data.ref_date + ' ' + data.ref_time,

            'https://indiacovid19.github.io/webarchive/mohfw/{}_{}/'
            .format(data.ref_date, data.ref_time.replace(':', '')),

            ''
    ]
    return '  ' + json.dumps(j)


def update_json(json_entry):
    """Update indiacovid19.json with the specified JSON entry."""
    with open('indiacovid19.json') as f:
        j = f.read()
    if json_entry in j:
        print('JSON archive is up-to-date')
        return
    print('Updating JSON archive ...')
    lines = j.splitlines()
    for i, line in enumerate(lines):
        if 1 < i < len(lines) - 1 and line.endswith(']'):
            lines[i] = line + ','
    lines[len(lines) - 1] = json_entry
    lines.append(']')
    output = '\n'.join(lines) + '\n'
    with open('indiacovid19.json', 'w') as f:
        f.write(output)
    print('Done')


def print_home_summary(home_data, region_data, json_entry):
    """Print summary of data on the terminal."""
    data = home_data
    print()
    print('ref_datetime: {}'.format(data.ref_datetime))
    print('overall: total: {}; active: {}; cured: {}; death: {}'
          .format(data.total, data.active, data.cured, data.death))
    data = region_data
    print('regions: total: {}; active: {}; cured: {}; death: {}'
          .format(data.region_total, data.region_active,
                  data.region_cured, data.region_death))
    print()
    print('regions: {}'.format(sorted(data.regions.items())))
    print()
    print('json:', json_entry)


def main():
    home_data = load_home_data()
    region_data = load_region_data(home_data)

    json_entry = make_json_entry(home_data)
    update_json(json_entry)

    print_home_summary(home_data, region_data, json_entry)


if __name__ == '__main__':
    main()
