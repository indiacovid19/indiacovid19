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


import argparse
import datetime
import difflib
import sys

from py import archive, mohfw


"""Generate Wikipedia markup code.

There are two templates used in the Wikipedia article
https://en.wikipedia.org/wiki/2020_coronavirus_pandemic_in_India
to display charts related to case numbers.

  1. Template:2019–20 coronavirus pandemic data/India medical cases chart
     [ https://w.wiki/Mxi ]
  2. Template:2019–20 coronavirus pandemic data/India medical cases
     [ https://w.wiki/Mxj ]

This script generates Wikipedia markup code for both charts. Enter these
commands at the top-level directory of this project to generate the
corresponding markups:

    python3 -m py.wiki -1
    python3 -m py.wiki -2

"""


import datetime


def medical_cases_chart():
    """Generate Wikipedia markup code for medical cases chart template."""
    output = open('layout/medical_cases_chart.txt').read()
    output = output.replace('@@data@@', medical_cases_chart_data())
    return output


def medical_cases_chart_data():
    """Generate data entries for medical cases chart template."""
    ignore_dates = ('2020-02-04', '2020-02-21', '2020-02-27')
    data = archive.load(ignore_dates=ignore_dates)
    out = []

    for i, (date, total, cured, death) in enumerate(zip(
            data.dates, data.total_cases, data.cured_cases, data.death_cases)):

        # Comma-delimited digit grouping.
        total_comma = '' if total == 0 else '{:,}'.format(total)
        death_comma = '' if death == 0 else '{:,}'.format(death)

        # Previous numbers.
        if i == 0:
            prev_total = 0
            prev_death = 0
        else:
            prev_total = data.total_cases[i - 1]
            prev_death = data.death_cases[i - 1]

        # Growth percent expressions
        growth_expr = '+{{{{#expr:({}/{} - 1)*100 round 0}}}}%'
        if total != prev_total:
            if prev_total == 0:
                total_growth_expr = 'firstright1=y'
            else:
                total_growth_expr = growth_expr.format(total, prev_total)
        else:
            total_growth_expr = ''

        if death != prev_death:
            if prev_death == 0:
                death_growth_expr = 'firstright2=y'
            else:
                death_growth_expr = growth_expr.format(death, prev_death)
        else:
            death_growth_expr = ''

        # date;deaths;cured;total;;;total;%age;deaths;%age
        out.append('{};{};{};{};;;{:};{};{:};{}'
                   .format(date, death, cured, total,
                           total_comma, total_growth_expr,
                           death_comma, death_growth_expr))

        # Print continuation lines.
        curr_index = data.dates.index(date)
        if curr_index < len(data.dates) - 1:
            curr_datetime = data.datetimes[curr_index]
            next_datetime = data.datetimes[curr_index + 1]
            if (next_datetime - curr_datetime).days != 1:
                month = next_datetime.strftime('%b')
                out.append(';{};{};{};;;{:,};;;;divisor=4;collapsed=y;id={}'
                           .format('' if death == 0 else death,
                                   '' if cured == 0 else cured,
                                   total, total, month.lower()))
    return '\n'.join(out)


def medical_cases():
    """Generate Wikipedia markup for medical cases template."""
    data = mohfw.load()
    output = open('layout/medical_cases.txt').read()
    output = region_table_rows(data, output)
    output = region_table_foot(data, output)

    ignore_dates = ('2020-02-04', '2020-02-27')
    data = archive.load(ignore_dates=ignore_dates)
    output = medical_cases_plots(data, output)
    return output


def region_table_rows(data, layout):
    """Generate table rows for state and union territory data table."""
    region_names = (
        'Andaman and Nicobar Islands',
        'Andhra Pradesh',
        'Arunachal Pradesh',
        'Assam',
        'Bihar',
        'Chandigarh',
        'Chhattisgarh',
        'Dadra and Nagar Haveli and Daman and Diu',
        'Delhi',
        'Goa',
        'Gujarat',
        'Haryana',
        'Himachal Pradesh',
        'Jammu and Kashmir',
        'Jharkhand',
        'Karnataka',
        'Kerala',
        'Ladakh',
        'Lakshadweep',
        'Madhya Pradesh',
        'Maharashtra',
        'Manipur',
        'Meghalaya',
        'Mizoram',
        'Nagaland',
        'Odisha',
        'Puducherry',
        'Punjab',
        'Rajasthan',
        'Sikkim',
        'Tamil Nadu',
        'Telangana',
        'Tripura',
        'Uttar Pradesh',
        'Uttarakhand',
        'West Bengal',
    )
    out = []
    for i, name in enumerate(sorted(region_names), 1):
        matches = difflib.get_close_matches(name, list(data.regions), 1)
        if len(matches) == 0:
            total, active, cured, death = 0, 0, 0, 0
        else:
            total, active, cured, death = data.regions[matches[0]]
        if name == 'Kerala':
            death = str(death) + open('layout/fn1.txt').read().strip()
        out.append('|-')
        out.append('!{}'.format(i))
        out.append('! scope="row" |\'\'\'{}\'\'\''.format(markup_region(name)))
        out.append('|{}'.format(markup_num(total)))
        out.append('|{}'.format(markup_num(death)))
        out.append('|{}'.format(markup_num(cured)))
        out.append('|{}'.format(markup_num(active)))
    out = '\n'.join(out)
    output = layout.replace('@@region_rows@@', out)
    return output


def region_table_foot(data, layout):
    """Generate footer row for region table."""
    output = (layout
                .replace('@@regions_total@@', str(data.regions_total))
                .replace('@@regions_death@@', str(data.regions_death))
                .replace('@@regions_cured@@', str(data.regions_cured))
                .replace('@@regions_active@@', str(data.regions_active))
                .replace('@@foreign_cases@@', str(data.foreign))
             )
    return output


def markup_region(name):
    """Generate Wikipedia markup to display region name in region table."""
    if name in (
        'Assam',
        'Delhi',
        'Goa',
        'Gujarat',
        'Karnataka',
        'Kerala',
        'Madhya Pradesh',
        'Maharashtra',
        'Odisha',
        'Rajasthan',
        'Tamil Nadu',
        'Uttar Pradesh',
        'West Bengal'
    ):
        return ('[[2020 coronavirus pandemic in {}|{}]]'
                .format(name, name))

    if name in ('Punjab'):
        return ('[[2020 coronavirus pandemic in {}, India|{}]]'
                .format(name, name))

    return name


def markup_num(n):
    """Generate Wikipedia markup for case numbers in region table."""
    return ' style="color:gray;" |0' if n == 0 else n


def medical_cases_plots(data, layout):
    """Generate Wikipedia markup to draw graph plots."""
    dates = ', '.join(x.strftime('%d %b').lstrip('0') for x in data.datetimes)
    total_cases = ', '.join(str(y) for y in data.total_cases)
    active_cases = ', '.join(str(y) for y in data.active_cases)
    cured_cases = ', '.join(str(y) for y in data.cured_cases)
    death_cases = ', '.join(str(y) for y in data.death_cases)
    total_diffs = ', '.join(str(y) for y in data.total_diffs)
    cured_diffs = ', '.join(str(y) for y in data.cured_diffs)
    death_diffs = ', '.join(str(y) for y in data.death_diffs)
    exp_marker = get_exp_marker(data)
    output = (layout
                .replace('@@dates@@', dates)
                .replace('@@total_cases@@', total_cases)
                .replace('@@active_cases@@', active_cases)
                .replace('@@cured_cases@@', cured_cases)
                .replace('@@death_cases@@', death_cases)
                .replace('@@exp_marker@@', exp_marker)
                .replace('@@total_diffs@@', total_diffs)
                .replace('@@cured_diffs@@', cured_diffs)
                .replace('@@death_diffs@@', death_diffs)
             )
    return output


def get_exp_marker(data):
    """Generate Wikipedia markup code to show exponential growth."""
    i = data.dates.index('2020-03-04')  # Index of reference point
    j = len(data.dates) - 1  # Index of last element
    n = (data.datetimes[j] - data.datetimes[i]).days
    commas1 = (', ' * i).strip()
    commas2 = (', ' * (j - i)).strip()
    output = ('{} {}{} {{{{#expr:50*1.16^{}}}}}'
              .format(commas1, 50, commas2, (j - i)))
    return output


def diffs():
    """Generate Wikipedia markup code to plot new cases."""
    print('\nNew cases per day:\n')
    print('y =', ', '.join(str(y) for y in data.total_diffs))
    print('\nNew recoveries per day:\n')
    print('y =', ', '.join(str(y) for y in data.cured_diffs))
    print('\nNew deaths per day:\n')
    print('y =', ', '.join(str(y) for y in data.death_diffs))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-1', action='store_true',
                        help='Markup for India medical cases chart')
    parser.add_argument('-2', action='store_true',
                        help='Markup for India medical cases')
    args = vars(parser.parse_args())

    if not any((args['1'], args['2'])):
        parser.print_help()
        sys.exit(1)

    if args['1']:
        print(medical_cases_chart(), end='')

    if args['2']:
        print(medical_cases(), end='')


if __name__ == '__main__':
    main()
