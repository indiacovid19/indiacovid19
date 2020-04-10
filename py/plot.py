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


def plt_begin():
    """Set up a new plot."""
    global formatted_dates
    formatted_dates = [d.strftime('%d %b') for d in data.datetimes]
    plt.clf()


def plt_end(image_name):
    """Configure current plot and export it to an image file."""
    plt.gcf().set_size_inches(7.2, 4.8)
    plt.grid(which='major', linewidth='0.4')
    plt.grid(which='minor', linewidth='0.1')
    plt.xlabel('Date')
    plt.xlim(left=-0.8, right=len(formatted_dates) - 0.2)
    plt.xticks(rotation='vertical', fontsize='x-small')
    plt.yticks(fontsize='small')
    plt.tick_params(which='both', length=0)
    plt.legend(shadow=True)
    os.makedirs('_site/img/', exist_ok=True)
    plt.savefig('_site/img/' + image_name,
                dpi=300, bbox_inches='tight')


def all_cases_linear():
    """Plot line chart for all case numbers (linear scale)."""
    plt_begin()
    plt.plot(formatted_dates, data.total_cases,
             marker='.', color=total_color, label='Total Cases', zorder=5)
    plt.plot(formatted_dates, data.active_cases,
             marker='.', color=active_color, label='Active Cases', zorder=4)
    plt.plot(formatted_dates, data.cured_cases,
             marker='.', color=cured_color, label='Cured Cases', zorder=3)
    plt.plot(formatted_dates, data.death_cases,
             marker='.', color=death_color,label='Death Cases', zorder=2)
    ax = plt.gca()
    ax.yaxis.set_major_locator(mpl.ticker.MultipleLocator(500))
    ax.yaxis.set_minor_locator(mpl.ticker.MultipleLocator(100))
    plt.ylabel('Count')
    plt.ylim(bottom=0)
    plt.title('COVID-19 Cases in India', x=0.6, y=0.92)
    plt_end('all-cases-linear.png')


def all_cases_logarithmic():
    """Plot line chart for all case numbers (logarithmic scale)."""
    total_cases = data.total_cases
    active_cases = data.active_cases
    cured_cases = data.cured_cases
    death_cases = data.death_cases

    total_cases, active_cases = shift(total_cases, active_cases, 0.05, -0.05)
    total_cases, cured_cases = shift(total_cases, cured_cases, 0.05, -0.05)
    cured_cases, active_cases = shift(cured_cases, active_cases, 0, -0.1)

    plt_begin()
    plt.yscale('log')
    plt.plot(formatted_dates, total_cases,
             marker='.', color=total_color, label='Total Cases', zorder=5)
    plt.plot(formatted_dates, active_cases,
             marker='.', color=active_color, label='Active Cases', zorder=4)
    plt.plot(formatted_dates, cured_cases,
             marker='.', color=cured_color, label='Cured Cases', zorder=3)
    plt.plot(formatted_dates, death_cases,
             marker='.', color=death_color,label='Death Cases', zorder=2)
    ax = plt.gca()
    ax.yaxis.set_major_locator(mpl.ticker.LogLocator())
    ax.yaxis.set_major_formatter(mpl.ticker.FuncFormatter(log_label_formatter))
    ax.yaxis.set_minor_formatter(mpl.ticker.FuncFormatter(log_label_formatter))
    plt.tick_params(which='minor', labelsize='xx-small')
    plt.ylabel('Count')
    plt.ylim(bottom=1)
    plt.title('COVID-19 Cases in India', x=0.6, y=0.92)
    plt_end('all-cases-logarithmic.png')


def new_cases():
    """Plot bar chart for new cases on each day."""
    plt_begin()
    plt.bar(formatted_dates, data.total_diff,
            color=total_color, label='New Cases', zorder=2)

    for index, value in enumerate(data.total_diff):
        plt.text(index, value + 10, value, ha='center',
                 rotation='vertical', fontsize='xx-small')

    ax = plt.gca()
    ax.yaxis.set_major_locator(mpl.ticker.MultipleLocator(50))
    ax.yaxis.set_minor_locator(mpl.ticker.MultipleLocator(10))
    plt.ylabel('New Cases')
    plt.ylim(top=top_ylim(data.total_diff, 50, 10))
    plt.ylim(bottom=0)
    plt.title('COVID-19 Cases in India', x=0.55, y=0.92)
    plt_end('new-cases.png')


def growth_percent():
    """Plot growth rate for each day."""
    growth_percents = [-1 if g == -1 else 100 * (g - 1)
                       for g in data.total_growth]
    growth_with_nan = [float('nan') if g == -1 else g
                       for g in growth_percents]

    plt_begin()
    plt.plot(formatted_dates, growth_with_nan,
             marker='.', color=total_color,
             label='Growth percent in number of total COVID-19 cases\n'
                   'in India on each day compared to previous day')

    for index, value in enumerate(growth_percents):
        if value != -1:
            v = '{:.0f}%'.format(value)
            plt.text(index, value + 12, v, ha='center',
                     rotation='vertical', fontsize='xx-small')

    ax = plt.gca()
    ax.yaxis.set_major_locator(mpl.ticker.MultipleLocator(50))
    ax.yaxis.set_minor_locator(mpl.ticker.MultipleLocator(10))
    ax.yaxis.set_major_formatter(mpl.ticker.FuncFormatter(percent_formatter))
    plt.ylabel('Growth percent')
    plt.ylim(top=top_ylim(growth_percents, 50, 10))
    plt.ylim(bottom=0)
    plt_end('growth-percent.png')


def doubling_time():
    """Plot line chart for all case numbers (linear scale)."""
    days = [float('nan') if x == -1 else x for x in data.doubling_days]
    plt_begin()
    plt.plot(formatted_dates, days,
             marker='.', color=total_color,
             label='Number of days it took for the number of\n'
                   'total COVID-19 cases in India to double')
    for index, value in enumerate(data.doubling_days):
        if value != -1:
            v = '{:.1f}'.format(value)
            plt.text(index, value + 1, v, ha='center',
                     rotation='vertical', fontsize='xx-small')
    ax = plt.gca()
    ax.yaxis.set_major_locator(mpl.ticker.MultipleLocator(5))
    ax.yaxis.set_minor_locator(mpl.ticker.MultipleLocator(1))
    plt.ylabel('Days')
    plt.ylim(top=top_ylim(data.doubling_days, 5, 1))
    plt.ylim(bottom=0)
    plt.title('COVID-19 Cases in India', x=0.6, y=0.92)
    plt_end('doubling-time.png')


def cured_percent():
    """Plot line chart for cured and death percents."""
    cured_nan = [float('nan') if x == -1 else x for x in data.cured_percents]
    death_nan = [float('nan') if x == -1 else x for x in data.death_percents]
    plt_begin()
    plt.plot(formatted_dates, cured_nan,
             marker='.', color=cured_color,
             label='Percent of closed cases that are cured cases')
    plt.plot(formatted_dates, death_nan,
             marker='.', color=death_color,
             label='Percent of closed cases that are death cases')
    for index, (cured, death) in enumerate(zip(data.cured_percents,
                                               data.death_percents)):
        if cured != -1:
            c = '{:.0f}%'.format(cured)
            d = '{:.0f}%'.format(death)
            plt.text(index, cured - 7, c, ha='center',
                     rotation='vertical', fontsize='xx-small')
            plt.text(index, death + 3, d, ha='center',
                     rotation='vertical', fontsize='xx-small')
    ax = plt.gca()
    ax.yaxis.set_major_locator(mpl.ticker.MultipleLocator(5))
    ax.yaxis.set_minor_locator(mpl.ticker.MultipleLocator(1))
    ax.yaxis.set_major_formatter(mpl.ticker.FuncFormatter(percent_formatter))
    plt.ylabel('Days')
    plt.ylim(top=100)
    plt.ylim(bottom=0)
    plt_end('cured-percent.png')


def cured_ratio():
    """Plot line chart for cured ratio."""
    cured_nan = [float('nan') if x == -1 else x for x in data.cured_ratios]
    plt_begin()
    plt.plot(formatted_dates, cured_nan,
             marker='.', color=cured_color,
             label='Number of cured cases per death case')
    for index, value in enumerate(data.cured_ratios):
        if value != -1:
            c = '{:.1f}'.format(value)
            plt.text(index, value + 0.2, c, ha='center',
                     rotation='vertical', fontsize='xx-small')
    ax = plt.gca()
    ax.yaxis.set_major_locator(mpl.ticker.MultipleLocator(0.5))
    ax.yaxis.set_minor_locator(mpl.ticker.MultipleLocator(0.1))
    plt.ylabel('Days')
    plt.ylim(top=top_ylim(data.cured_ratios, 2, 1))
    plt.ylim(bottom=0)
    plt_end('cured-ratio.png')


def linear_label_formatter(x, pos):
    """Return tick label for linear scale."""
    if x % 100 == 0:
        return int(x)


def log_label_formatter(x, pos):
    """Return tick label for logarithmic scale."""
    if str(x)[0] in ['1', '2', '4', '6', '8']:
        return int(x)


def bar_label_formatter(x, pos):
    """Return tick label for bar chart."""
    return int(x)


def percent_formatter(x, pos):
    """Return tick label for growth percent graph."""
    return str(int(x)) + '%'


def top_ylim(data, padding, round_to):
    """Calculate top ylim by adding padding to max data value."""
    y = max(data) + padding
    y = y - (y % round_to)
    return y


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
