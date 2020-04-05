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


total_color = '#06c'
active_color = '#f60'
cured_color = '#393'
death_color = '#c33'


def all_cases_linear():
    """Plot line chart for all case numbers (linear scale)."""
    os.makedirs('_site/img/', exist_ok=True)
    dates = formatted_dates()
    plt.clf()
    plt.gcf().set_size_inches(6.4, 4.8)
    plt.plot(dates, data.total_cases,
             marker='.', color=total_color, label='Total Cases', zorder=5)
    plt.plot(dates, data.active_cases,
             marker='.', color=active_color, label='Active Cases', zorder=4)
    plt.plot(dates, data.cured_cases,
             marker='.', color=cured_color, label='Cured Cases', zorder=3)
    plt.plot(dates, data.death_cases,
             marker='.', color=death_color,label='Death Cases', zorder=2)
    ax = plt.gca()
    ax.yaxis.set_major_locator(mpl.ticker.MultipleLocator(50))
    ax.yaxis.set_minor_locator(mpl.ticker.MultipleLocator(10))
    ax.yaxis.set_major_formatter(mpl.ticker.FuncFormatter(linear_label_formatter))
    plt.grid(which='major', linewidth='0.4')
    plt.grid(which='minor', linewidth='0.1')
    plt.tick_params(which='both', length=0)
    plt.xticks(rotation='vertical', fontsize='x-small')
    plt.yticks(fontsize='small')
    plt.xlabel('Date')
    plt.ylabel('Count')
    plt.xlim(left=-0.8, right=len(dates) - 0.2)
    plt.ylim(bottom=0)
    plt.title('COVID-19 Cases in India', x=0.6, y=0.92)
    plt.legend(shadow=True)
    plt.savefig('_site/img/all-cases-linear.png',
                dpi=300, bbox_inches='tight')


def all_cases_logarithmic():
    """Plot line chart for all case numbers (logarithmic scale)."""
    os.makedirs('_site/img/', exist_ok=True)
    dates = formatted_dates()
    total_cases = data.total_cases
    active_cases = data.active_cases
    cured_cases = data.cured_cases
    death_cases = data.death_cases

    total_cases, active_cases = shift(total_cases, active_cases, 0.05, -0.05)
    total_cases, cured_cases = shift(total_cases, cured_cases, 0.05, -0.05)
    cured_cases, active_cases = shift(cured_cases, active_cases, 0, -0.1)

    plt.clf()
    plt.gcf().set_size_inches(6.4, 4.8)
    plt.plot(dates, total_cases,
             marker='.', color=total_color, label='Total Cases', zorder=5)
    plt.plot(dates, active_cases,
             marker='.', color=active_color, label='Active Cases', zorder=4)
    plt.plot(dates, cured_cases,
             marker='.', color=cured_color, label='Cured Cases', zorder=3)
    plt.plot(dates, death_cases,
             marker='.', color=death_color,label='Death Cases', zorder=2)
    plt.yscale('log')
    ax = plt.gca()
    ax.yaxis.set_major_locator(mpl.ticker.LogLocator())
    ax.yaxis.set_major_formatter(mpl.ticker.FuncFormatter(log_label_formatter))
    ax.yaxis.set_minor_formatter(mpl.ticker.FuncFormatter(log_label_formatter))
    plt.grid(which='major', linewidth='0.4')
    plt.grid(which='minor', linewidth='0.1')
    locs, labels = plt.xticks()
    plt.tick_params(which='both', length=0)
    plt.tick_params(which='minor', length=0, labelsize='xx-small')
    plt.xticks(rotation='vertical', fontsize='x-small')
    plt.yticks(fontsize='small')
    plt.xlabel('Date')
    plt.ylabel('Count')
    plt.xlim(left=-0.8, right=len(dates) - 0.2)
    plt.ylim(bottom=1)
    plt.title('COVID-19 Cases in India', x=0.6, y=0.92)
    plt.legend(shadow=True)
    plt.savefig('_site/img/all-cases-logarithmic.png',
                dpi=300, bbox_inches='tight')


def new_cases():
    """Plot bar chart for new cases on each day."""
    os.makedirs('_site/img/', exist_ok=True)
    dates = formatted_dates()
    plt.clf()
    plt.gcf().set_size_inches(6.4, 4.8)
    plt.bar(dates, data.total_diff,
             color=total_color, label='New Cases', zorder=4)
    for index, value in enumerate(data.total_diff):
        plt.text(index, value + 2, value, ha='center', fontsize='x-small')

    ax = plt.gca()
    ax.yaxis.set_major_locator(mpl.ticker.MultipleLocator(50))
    ax.yaxis.set_minor_locator(mpl.ticker.MultipleLocator(10))
    ax.yaxis.set_major_formatter(mpl.ticker.FuncFormatter(bar_label_formatter))
    plt.grid(which='major', linewidth='0.4')
    plt.grid(which='minor', linewidth='0.1')
    plt.tick_params(which='major', length=0)
    plt.tick_params(which='minor', length=0)
    plt.xticks(rotation='vertical', fontsize='x-small')
    plt.yticks(fontsize='small')
    plt.xlabel('Date')
    plt.ylabel('New Cases')
    plt.xlim(left=-0.8, right=len(dates) - 0.2)
    plt.ylim(bottom=0)
    plt.title('COVID-19 Cases in India', x=0.55, y=0.92)
    plt.legend(shadow=True)
    plt.savefig('_site/img/new-cases.png', dpi=300, bbox_inches='tight')


def doubling_time():
    """Plot line chart for all case numbers (linear scale)."""
    os.makedirs('_site/img/', exist_ok=True)
    dates = formatted_dates()
    days = [float('nan') if x == -1 else x for x in data.doubling_days]
    plt.clf()
    plt.gcf().set_size_inches(6.4, 4.8)
    plt.plot(dates, days,
             marker='.', color=total_color,
             label='Number of days it took for the number of\n'
                   'total COVID-19 cases in India to double')
    ax = plt.gca()
    ax.yaxis.set_major_locator(mpl.ticker.MultipleLocator(5))
    ax.yaxis.set_minor_locator(mpl.ticker.MultipleLocator(1))
    plt.grid(which='major', linewidth='0.4')
    plt.grid(which='minor', linewidth='0.1')
    plt.tick_params(which='both', length=0)
    plt.xticks(rotation='vertical', fontsize='x-small')
    plt.yticks(fontsize='small')
    plt.xlabel('Date')
    plt.ylabel('Days')
    plt.xlim(left=-0.8, right=len(dates) - 0.2)
    plt.ylim(bottom=0)
    plt.title('COVID-19 Cases in India', x=0.6, y=0.92)
    plt.legend(shadow=True)
    plt.savefig('_site/img/doubling-time.png',
                dpi=300, bbox_inches='tight')


def linear_label_formatter(x, pos):
    """Return tick label for linear scale."""
    if x % 100 == 0:
        return int(x)


def log_label_formatter(x, pos):
    """Return tick label for logarithmic scale."""
    if str(x)[0] != '9':
        return int(x)


def bar_label_formatter(x, pos):
    """Return tick label for bar chart."""
    return int(x)


def formatted_dates():
    """Date strings to use as X-axis tick labels."""
    return [d.strftime('%d %b') for d in data.datetimes]


def shift(a, b, shift_a, shift_b):
    """Shift overlapping values in lists a and b to make them different."""
    new_a = a[:]
    new_b = b[:]
    for i, (total, active) in enumerate(zip(a, b)):
        if total == active:
            new_a[i] += shift_a
            new_b[i] += shift_b
    return new_a, new_b


def main():
    data.load()
    all_cases_linear()
    all_cases_logarithmic()
    new_cases()
    doubling_time()


if __name__ == '__main__':
    main()
