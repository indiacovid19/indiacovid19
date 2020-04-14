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
    plt.gcf().set_size_inches(7.68, 4.8)
    plt.grid(which='major', linewidth='0.4')
    plt.grid(which='minor', linewidth='0.1')
    plt.xlabel('Date')
    plt.xlim(left=-0.8, right=len(formatted_dates) - 0.2)
    plt.xticks(rotation='vertical', size='x-small')
    plt.yticks(size='small')
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
    plt.tick_params(which='minor', labelsize='x-small')
    plt.ylabel('Count')
    plt.ylim(bottom=1)
    plt.title('COVID-19 Cases in India', x=0.6, y=0.92)
    plt_end('all-cases-logarithmic.png')


def new_cases():
    """Plot bar chart for new cases on each day."""
    tick_gap = 20
    plt_begin()
    plt.bar(formatted_dates, data.total_diff,
            color=total_color, label='New Cases', zorder=2)
    for i, value in enumerate(data.total_diff):
        plt.text(i, value + 20, value, ha='center',
                 rotation='vertical', size='x-small', color=total_color)
    ax = plt.gca()
    ax.yaxis.set_major_locator(mpl.ticker.MultipleLocator(tick_gap * 5))
    ax.yaxis.set_minor_locator(mpl.ticker.MultipleLocator(tick_gap))
    plt.ylabel('New Cases')
    plt.ylim(top=top_ylim(data.total_diff, tick_gap * 7, tick_gap))
    plt.ylim(bottom=0)
    plt.title('COVID-19 Cases in India', x=0.55, y=0.92)
    plt_end('new-cases.png')


def growth_percent():
    """Plot growth rate for each day."""
    growth_val = [-1 if g == -1 else 100 * (g - 1) for g in data.total_growth]
    growth_nan = [float('nan') if g == -1 else g for g in growth_val]
    tick_gap = 10

    # Plot graph.
    plt_begin()
    plt.plot(formatted_dates, growth_nan,
             marker='.', color=total_color,
             label='Growth percent in number of total COVID-19 cases\n'
                   'in India on each day compared to previous day')

    # Print values on the graph.
    tweaks = [(0, 0)] * len(data.dates)
    tweaks[data.dates.index('2020-02-03')] = (+0.3, +0.0)
    tweaks[data.dates.index('2020-02-04')] = (+0.5, +0.0)
    tweaks[data.dates.index('2020-03-03')] = (+0.6, -0.5)
    tweaks[data.dates.index('2020-03-05')] = (-0.6, -1.0)
    tweaks[data.dates.index('2020-03-16')] = (+0.1, +0.0)
    tweaks[data.dates.index('2020-03-22')] = (+0.1, +0.0)
    prev_val = -1
    for i, val in enumerate(growth_val):
        if val != -1 and abs(val - prev_val) > 0.001:
            x = i + tweaks[i][0]
            y = val + (1.2 + tweaks[i][1]) * tick_gap
            v = '{:.0f}%'.format(val)
            plt.text(x, y, v, ha='center', rotation='vertical',
                     size='x-small', color=total_color)
            prev_val = val

    # Format axes.
    ax = plt.gca()
    ax.yaxis.set_major_locator(mpl.ticker.MultipleLocator(tick_gap * 5))
    ax.yaxis.set_minor_locator(mpl.ticker.MultipleLocator(tick_gap))
    ax.yaxis.set_major_formatter(mpl.ticker.FuncFormatter(percent_formatter))
    plt.ylabel('Growth percent')
    plt.ylim(top=top_ylim(growth_val, tick_gap * 5, tick_gap))
    plt.ylim(bottom=0)
    plt_end('growth-percent.png')


def doubling_time():
    """Plot line chart for all case numbers (linear scale)."""
    days_nan = [float('nan') if x == -1 else x for x in data.doubling_days]
    tick_gap = 1

    # Plot graph.
    plt_begin()
    plt.plot(formatted_dates, days_nan,
             marker='.', color=total_color,
             label='Number of days it took for the number of\n'
                   'total COVID-19 cases in India to double')

    # Print values on the graph.
    tweaks = [(0, 0)] * len(data.dates)
    tweaks[data.dates.index('2020-02-04')] = (+0.8, -1.3)
    tweaks[data.dates.index('2020-02-21')] = (+0.8, -1.3)
    tweaks[data.dates.index('2020-02-27')] = (-0.1, +0.1)
    tweaks[data.dates.index('2020-03-03')] = (+0.8, -1.3)
    tweaks[data.dates.index('2020-03-04')] = (+0.3, +0.0)
    prev_val = -1
    for i, val in enumerate(data.doubling_days):
        if val != -1 and abs(val - prev_val) > 0.001:
            x = i + tweaks[i][0]
            y = val + (1.0 + tweaks[i][1]) * tick_gap
            v = '{:.1f}'.format(val)
            plt.text(x, y, v, ha='center', rotation='vertical',
                     size='x-small', color=total_color)
            prev_val = val

    # Format axes.
    ax = plt.gca()
    ax.yaxis.set_major_locator(mpl.ticker.MultipleLocator(tick_gap * 5))
    ax.yaxis.set_minor_locator(mpl.ticker.MultipleLocator(tick_gap))
    plt.ylabel('Days')
    plt.ylim(top=top_ylim(data.doubling_days, tick_gap * 5, tick_gap))
    plt.ylim(bottom=0)
    plt.title('COVID-19 Cases in India', x=0.6, y=0.92)
    plt_end('doubling-time.png')


def cured_percent():
    """Plot line chart for cured and death percents."""
    cured_nan = [float('nan') if x == -1 else x for x in data.cured_percents]
    death_nan = [float('nan') if x == -1 else x for x in data.death_percents]
    tick_gap = 1

    # Plot graph.
    plt_begin()
    plt.plot(formatted_dates, cured_nan,
             marker='.', color=cured_color,
             label='Percent of closed cases that are cured cases')
    plt.plot(formatted_dates, death_nan,
             marker='.', color=death_color,
             label='Percent of closed cases that are death cases')

    # Tweaks for cured values.
    cured_tweaks = [(0, 0)] * len(data.dates)
    cured_tweaks[data.dates.index('2020-03-13')] = (+0.3, +0.0)

    # Tweaks for death values.
    death_tweaks = [(0, 0)] * len(data.dates)
    death_tweaks[data.dates.index('2020-03-13')] = (+0.3, +0.0)

    # Print values on the graph.
    prev_cured = -1
    for i, (cured, death) in enumerate(zip(data.cured_percents,
                                               data.death_percents)):
        if cured != -1 and abs(cured - prev_cured) > 0.001:
            # Print cured value.
            x = i + cured_tweaks[i][0]
            y = cured + (-8 + cured_tweaks[i][1]) * tick_gap
            v = '{:.0f}%'.format(cured)
            plt.text(x, y, v, ha='center', rotation='vertical',
                     size='x-small', color=cured_color)
            # Print death value.
            x = i + death_tweaks[i][0]
            y = death + (+3 + death_tweaks[i][1]) * tick_gap
            v = '{:.0f}%'.format(death)
            plt.text(x, y, v, ha='center', rotation='vertical',
                     size='x-small', color=death_color)
            prev_cured = cured

    # Format axes.
    ax = plt.gca()
    ax.yaxis.set_major_locator(mpl.ticker.MultipleLocator(tick_gap * 5))
    ax.yaxis.set_minor_locator(mpl.ticker.MultipleLocator(tick_gap))
    ax.yaxis.set_major_formatter(mpl.ticker.FuncFormatter(percent_formatter))
    plt.ylabel('Days')
    plt.ylim(top=100)
    plt.ylim(bottom=0)
    plt_end('cured-percent.png')


def cured_ratio():
    """Plot line chart for cured ratio."""
    cured_nan = [float('nan') if x == -1 else x for x in data.cured_ratios]
    tick_gap = 0.1

    # Plot graph.
    plt_begin()
    plt.plot(formatted_dates, cured_nan,
             marker='.', color=cured_color,
             label='Number of cured cases per death case')

    # Print values on the graph.
    tweaks = [(0, 0)] * len(data.dates)
    tweaks[data.dates.index('2020-03-12')] = (+0.8, -1.7)
    tweaks[data.dates.index('2020-03-17')] = (+0.5, +0.0)
    tweaks[data.dates.index('2020-03-19')] = (-0.3, +0.0)
    tweaks[data.dates.index('2020-03-22')] = (+0.0, -5.5)
    tweaks[data.dates.index('2020-03-26')] = (+0.0, -5.5)
    tweaks[data.dates.index('2020-03-27')] = (-0.2, +0.0)
    tweaks[data.dates.index('2020-03-29')] = (+0.2, +0.0)
    tweaks[data.dates.index('2020-04-02')] = (+0.2, +0.0)
    tweaks[data.dates.index('2020-04-04')] = (-0.2, +0.0)
    tweaks[data.dates.index('2020-04-06')] = (+0.2, +0.0)
    prev_val = -1
    for i, val in enumerate(data.cured_ratios):
        if val != -1 and abs(val - prev_val) > 0.001:
            x = i + tweaks[i][0]
            y = val + (2.0 + tweaks[i][1]) * tick_gap
            v = '{:.1f}'.format(val)
            plt.text(x, y, v, ha='center', rotation='vertical',
                     size='x-small', color=cured_color)
            prev_val = val

    # Format axes.
    ax = plt.gca()
    ax.yaxis.set_major_locator(mpl.ticker.MultipleLocator(tick_gap * 5))
    ax.yaxis.set_minor_locator(mpl.ticker.MultipleLocator(tick_gap))
    plt.ylabel('Days')
    plt.ylim(top=top_ylim(data.cured_ratios, tick_gap * 6, tick_gap))
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
