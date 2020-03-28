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


import os
import matplotlib as mpl
import matplotlib.pyplot as plt
from py import data


def all_cases():
    """Plot line chart for all case numbers."""
    os.makedirs('_site/img/', exist_ok=True)
    dates = formatted_dates()
    plt.clf()
    plt.plot(dates, data.total_cases,
             color='#06c', label='Total Cases', zorder=4)
    plt.plot(dates, data.active_cases,
             color='#f60', label='Active Cases', zorder=3)
    plt.plot(dates, data.cured_cases,
             color='#393', label='Cured Cases', zorder=2)
    plt.plot(dates, data.death_cases,
             color='#c33',label='Death Cases', zorder=1)
    ax = plt.gca()
    ax.yaxis.set_major_locator(mpl.ticker.MultipleLocator(50))
    ax.yaxis.set_minor_locator(mpl.ticker.MultipleLocator(10))
    plt.grid(which='major', linewidth='0.4')
    plt.grid(which='minor', linewidth='0.1')
    plt.tick_params(which='major', length=0)
    plt.tick_params(which='minor', length=0)
    plt.xticks(rotation='vertical', fontsize='x-small')
    plt.yticks(fontsize='small')
    plt.xlabel('Date')
    plt.ylabel('Count')
    plt.ylim(bottom=0)
    plt.xlim(left=0, right=len(dates) - 1)
    plt.title('COVID-19 Cases in India', x=0.6, y=0.9)
    plt.legend(shadow=True)
    plt.savefig('_site/img/all-cases.png', dpi=300, bbox_inches='tight')


def new_cases():
    """Plot bar chart for new cases on each day."""
    os.makedirs('_site/img/', exist_ok=True)
    dates = formatted_dates()
    plt.clf()
    plt.bar(dates, data.total_diff,
             color='#06c', label='New Cases', zorder=4)
    for index, value in enumerate(data.total_diff):
        plt.text(index, value + 2, value, ha='center', fontsize='x-small')

    ax = plt.gca()
    ax.yaxis.set_major_locator(mpl.ticker.MultipleLocator(5))
    ax.yaxis.set_minor_locator(mpl.ticker.MultipleLocator(1))
    plt.grid(which='major', linewidth='0.4')
    plt.grid(which='minor', linewidth='0.1')
    plt.tick_params(which='major', length=0)
    plt.tick_params(which='minor', length=0)
    plt.xticks(rotation='vertical', fontsize='x-small')
    plt.yticks(fontsize='small')
    plt.xlabel('Date')
    plt.ylabel('Count')
    plt.ylim(bottom=0)
    plt.xlim(left=0, right=len(dates))
    plt.title('COVID-19 Cases in India', x=0.55, y=0.9)
    plt.legend(shadow=True)
    plt.savefig('_site/img/new-cases.png', dpi=300, bbox_inches='tight')


def formatted_dates():
    """Date strings to use as X-axis tick labels."""
    return [d.strftime('%d %b') for d in data.datetimes]


def main():
    data.load()
    cases()
    new_cases()


if __name__ == '__main__':
    main()
