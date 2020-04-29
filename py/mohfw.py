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
        self.migrated = -1
        self.ref_datetime = None
        self.ref_date = ''
        self.ref_time = ''
        self.foreign = -1
        self.regions = {}
        self.regions_total = -1
        self.regions_cured = -1
        self.regions_death = -1
        self.regions_active = -1


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
    strong_re = re.compile(r'.*<strong>(.*)</strong>')
    time_re = re.compile(r'.*as on\s*:\s*(\d.*) GMT')
    foreign_re = re.compile(r'.*[Ii]ncluding (\d+) [Ff]oreign')
    td_re = re.compile(r'.*<td>([^#]*).*</td>')
    parser_state = 'DEFAULT'

    # Parse the response.
    for i, line in enumerate(lines):
        if data.active == -1 and 'Active Cases' in line:
            data.active = int(strong_re.match(lines[i - 1]).group(1))
        elif data.cured == -1 and 'Cured' in line:
            data.cured = int(strong_re.match(lines[i - 1]).group(1))
        elif data.death == -1 and 'Deaths' in line:
            data.death = int(strong_re.match(lines[i - 1]).group(1))
        elif data.migrated == -1 and 'Migrated' in line:
            data.migrated = int(strong_re.match(lines[i - 1]).group(1))
        elif data.ref_datetime == None and 'as on' in line:
            t = time_re.match(line).group(1)
            data.ref_datetime = datetime.datetime.strptime(t, '%d %B %Y, %H:%M')
            data.ref_date = data.ref_datetime.strftime('%Y-%m-%d')
            data.ref_time = data.ref_datetime.strftime('%H:%M')
        elif data.foreign == -1 and 'foreign' in line:
            data.foreign = int(foreign_re.match(line).group(1))
        elif '<tbody>' in line:
            parser_state = 'REGION'
        elif parser_state == 'REGION' and '<tr>' in line:
            if 'Total' in lines[i + 1]:
                parser_state = 'REGION_TOTAL'
                continue
            region_name = td_re.match(lines[i + 2]).group(1)
            total = int(td_re.match(lines[i + 3]).group(1))
            cured = int(td_re.match(lines[i + 4]).group(1))
            death = int(td_re.match(lines[i + 5]).group(1))
            active = total - cured - death
            data.regions[region_name] = (total, active, cured, death)
        elif parser_state == 'REGION_TOTAL' and 'Total' in line:
            parser_state = 'DEFAULT'
            s = strong_re.match(lines[i + 1]).group(1)
            data.regions_total = int(s.rstrip('*'))
            data.regions_cured = int(strong_re.match(lines[i + 3]).group(1))
            data.regions_death = int(strong_re.match(lines[i + 6]).group(1))
            data.regions_active = (data.regions_total - data.regions_cured
                                                      - data.regions_death)

    data.total = data.active + data.cured + data.death + data.migrated

    # Validations.
    if data.total != data.regions_total:
        log.log('home page: Mismatch in total and regions_total')
    if data.active != data.regions_active:
        log.log('home page: Mismatch in active and regions_active')
    if data.cured + data.migrated != data.regions_cured:
        log.log('home page: Mismatch in cured + migrated and regions_cured')
    if data.death != data.regions_death:
        log.log('home page: Mismatch in death and regions_death')
    return data


def load_dash_data():
    """Return data retrieved from MoHFW dashboard page."""
    data = Data()

    # Retrieve MoHFW dashboard HTML.
    url = 'https://www.mohfw.gov.in/index.php'
    log.log('Connecting to {} ...', url)
    response = urllib.request.urlopen(url).read().decode('utf-8')
    lines = [l.strip() for l in response.splitlines()]
    lines = [l for l in lines if l != '']

    # Parsers.
    strong_re = re.compile(r'.*<strong>(.*)</strong>')
    time_re = re.compile(r'.*as on\s*:\s*(\d.*) GMT')
    js_re = re.compile(r"\['(.*)', (.*), (.*), (.*)\],")
    parser_state = 'DEFAULT'

    # Parse the response.
    for i, line in enumerate(lines):
        if data.active == -1 and 'Active Cases' in line:
            data.active = int(strong_re.match(lines[i - 1]).group(1))
        elif data.cured == -1 and 'Cured' in line:
            data.cured = int(strong_re.match(lines[i - 1]).group(1))
        elif data.death == -1 and 'Deaths' in line:
            data.death = int(strong_re.match(lines[i - 1]).group(1))
        elif data.migrated == -1 and 'Migrated' in line:
            data.migrated = int(strong_re.match(lines[i - 1]).group(1))
        elif data.ref_datetime == None and 'as on' in line:
            t = time_re.match(line).group(1)
            data.ref_datetime = datetime.datetime.strptime(t, '%d %B %Y, %H:%M')
            data.ref_date = data.ref_datetime.strftime('%Y-%m-%d')
            data.ref_time = data.ref_datetime.strftime('%H:%M')
        elif 'Hover' in line:
            break

    data.total = data.active + data.cured + data.death + data.migrated

    # Retrieve MoHFW JSON data.
    url = 'https://www.mohfw.gov.in/data/data.json'
    log.log('Connecting to {} ...', url)
    items = json.load(urllib.request.urlopen(url))

    # Parse the response.
    for item in items:
        region_name = item['state_name']
        total = int(item['positive'])
        cured = int(item['cured'])
        death = int(item['death'])
        active = total - cured - death
        data.regions[region_name] = (total, active, cured, death)

    # Region totals.
    data.regions_total = sum(v[0] for v in data.regions.values())
    data.regions_active = sum(v[1] for v in data.regions.values())
    data.regions_cured = sum(v[2] for v in data.regions.values())
    data.regions_death = sum(v[3] for v in data.regions.values())

    # Validations.
    if data.total != data.regions_total:
        log.log('dashboard: Mismatch in total and regions_total')
    if data.active != data.regions_active:
        log.log('dashboard: Mismatch in active and regions_active')
    if data.cured + data.migrated != data.regions_cured:
        log.log('dashboard: Mismatch in cured + migrated and regions_cured')
    if data.death != data.regions_death:
        log.log('dashboard: Mismatch in death and regions_death')

    return data


def make_summary(data):
    """Print summary of data on the terminal."""
    out = []
    out.append('ref_datetime: {}'.format(data.ref_datetime))
    out.append('overall: total: {}; active: {}; cured: {}; death: {}; '
               'migrated: {}'.format(data.total, data.active,
                                     data.cured, data.death, data.migrated))
    out.append('regions: total: {}; active: {}; cured: {}; death: {}; '
               'foreign: {}'.format(data.regions_total, data.regions_active,
                                    data.regions_cured, data.regions_death,
                                    data.foreign))
    out.append('')
    out.append('regions: {}'.format(sorted(data.regions.items())))
    out.append('')
    return '\n'.join(out)


def make_json_entry(data):
    """Return JSON entry to be added to indiacovid19.json."""
    return ('  [ "{}",  {:5},  {:5},  {:5},  {:5},  "{} {}",  '
            '"https://indiacovid19.github.io/webarchive/mohfw/{}_{}/",'
            '      "" ]'
            .format(data.ref_date, data.active, data.cured, data.death,
                    data.migrated, data.ref_date, data.ref_time,
                    data.ref_date, data.ref_time.replace(':', '')))


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


def print_summary(data, heading):
    """Print a summary of the retrieved data on console."""
    print(heading)
    print('-' * len(heading))
    print(make_summary(data))
    json_entry = make_json_entry(data)
    print('JSON octuple for indiacovid19.json:')
    print()
    print(json_entry)
    print()
    update_json(json_entry)
    print()


def main():
    home_data = load_home_data()
    dash_data = load_dash_data()
    print()
    print_summary(home_data, 'HOME PAGE DATA')
    print_summary(dash_data, 'DASHBOARD DATA')


if __name__ == '__main__':
    main()
