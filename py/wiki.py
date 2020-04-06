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
from py import data


"""Generate Wikipedia markup code.

Generate Wikipedia markup code for the case number entries used to draw
https://en.wikipedia.org/wiki/Template:2019%E2%80%9320_coronavirus_pandemic_data/India_medical_cases_chart

The above chart is used in the main article at
https://en.wikipedia.org/wiki/2020_coronavirus_pandemic_in_India under
the heading "COVID-19 cases in India".

Enter the following command at the top-level directory of this project
to execute this script:

    python3 -m py.wiki

"""


def main():
    """Generate Wikipedia markup code."""
    data.load()
    months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun',
              'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
    for (date, death, cured,
         total, new, growth) in zip(data.dates, data.death_cases,
                                    data.cured_cases, data.total_cases,
                                    data.total_diff, data.total_growth):

        if growth == -1:
            growth = 'NA'
        else:
            growth = '{:+.0f}%'.format(100 * (growth - 1))

        # Ignore entries not used in Wikipedia.
        if date in ('2020-02-04', '2020-02-21', '2020-02-27'):
            continue

        print('{};{};{};{};;;{:,};{:+};;{}'.format(date, death, cured, total,
                                                     total, new, growth))

        # Print continuation lines.
        if date in ('2020-01-30', '2020-02-03'):
            month = datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%b')
            month = months[(months.index(month.lower()) + 1) % len(months)]
            print(';;;{};;;{};;;;divisor=4;collapsed=y;id={}'
                  .format(total, total, month))


if __name__ == '__main__':
    main()
