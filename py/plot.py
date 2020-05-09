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


import argparse
import os
import matplotlib as mpl
import matplotlib.pyplot as plt
from py import archive, log


total_color = '#06c'
active_color = '#f60'
cured_color = '#393'
death_color = '#c33'
recent_days = 30


def plot_begin(data):
    """Set up a new plot."""
    global formatted_dates
    formatted_dates = [d.strftime('%d %b') for d in data.datetimes]
    plt.clf()


def plot_end(data, img_name, recent, aspect):
    """Configure current plot and export it to an image file."""
    if recent:
        filename = img_name + '-recent.png'
        legend_size = 'small'
    else:
        filename = img_name + '.png'
        legend_size = 'medium'

    if aspect == 'square':
        plot_size = 4.8, 4.8
    elif aspect == 'wide':
        plot_size = 9.4, 4.8
    else:
        plot_size = 0.16 * len(data.dates), 4.8

    plt.gcf().set_size_inches(plot_size)
    plt.grid(which='major', linewidth='0.4')
    plt.grid(which='minor', linewidth='0.1')
    plt.xlabel('Date')
    plt.xticks(rotation='vertical', size='x-small')
    plt.yticks(size='small')
    plt.tick_params(which='both', length=0)
    plt.legend(shadow=True, fontsize=legend_size)
    os.makedirs('_site/img/', exist_ok=True)
    plt.savefig('_site/img/' + filename,
                dpi=300, bbox_inches='tight')


def plot_total_cases_linear(data, recent, aspect):
    """Plot line chart for all case numbers (linear scale)."""
    m = len(data.dates) - recent_days - 1 if recent else 0
    tick_gap = 1000
    ylim_pad = 6
    title_x, title_y = (0.63, 0.9) if recent else (0.5, 0.9)

    plot_begin(data)
    plt.plot(formatted_dates[m:], data.total_cases[m:],
             marker='.', color=total_color, label='Total Cases', zorder=5)
    plt.plot(formatted_dates[m:], data.active_cases[m:],
             marker='.', color=active_color, label='Active Cases', zorder=4)
    plt.plot(formatted_dates[m:], data.cured_cases[m:],
             marker='.', color=cured_color, label='Cured Cases', zorder=3)
    plt.plot(formatted_dates[m:], data.death_cases[m:],
             marker='.', color=death_color,label='Death Cases', zorder=2)
    ax = plt.gca()
    ax.yaxis.set_major_locator(mpl.ticker.MultipleLocator(tick_gap * 5))
    ax.yaxis.set_minor_locator(mpl.ticker.MultipleLocator(tick_gap))
    plt.ylabel('Count')
    plt.xlim(left=0.2 if recent else -0.8, right=len(data.dates[m:]) - 0.2)
    plt.ylim(top=top_ylim(data.total_cases[m:], tick_gap * ylim_pad, tick_gap))
    plt.ylim(bottom=0)
    plt.title('COVID-19 Cases in India', x=title_x, y=title_y, size='medium')
    plot_end(data, 'total-cases-linear', recent, aspect)


def plot_total_cases_log(data, recent, aspect):
    """Plot line chart for all case numbers (log scale)."""
    m = len(data.dates) - recent_days - 1 if recent else 0
    ylim_top = max(data.total_cases[m:]) * 2
    title_x, title_y = (0.6, 0.91) if recent else (0.5, 0.91)

    total_cases = data.total_cases
    active_cases = data.active_cases
    cured_cases = data.cured_cases
    death_cases = data.death_cases

    total_cases, active_cases = shift(total_cases, active_cases, 0.05, -0.05)
    total_cases, cured_cases = shift(total_cases, cured_cases, 0.05, -0.05)
    cured_cases, active_cases = shift(cured_cases, active_cases, 0, -0.1)

    plot_begin(data)
    plt.yscale('log')
    plt.plot(formatted_dates[m:], total_cases[m:],
             marker='.', color=total_color, label='Total Cases', zorder=5)
    plt.plot(formatted_dates[m:], active_cases[m:],
             marker='.', color=active_color, label='Active Cases', zorder=4)
    plt.plot(formatted_dates[m:], cured_cases[m:],
             marker='.', color=cured_color, label='Cured Cases', zorder=3)
    plt.plot(formatted_dates[m:], death_cases[m:],
             marker='.', color=death_color,label='Death Cases', zorder=2)
    ax = plt.gca()
    ax.yaxis.set_major_locator(mpl.ticker.LogLocator())
    ax.yaxis.set_major_formatter(mpl.ticker.FuncFormatter(log_label_formatter))
    ax.yaxis.set_minor_formatter(mpl.ticker.FuncFormatter(log_label_formatter))
    plt.tick_params(which='minor', labelsize='x-small')
    plt.ylabel('Count')
    plt.xlim(left=0.2 if recent else -0.8, right=len(data.dates[m:]) - 0.2)
    plt.ylim(top=ylim_top)
    plt.ylim(bottom=1)
    plt.title('COVID-19 cases in India', x=title_x, y=title_y, size='medium')
    plot_end(data, 'total-cases-log', recent, aspect)


def plot_new_cases(data, recent, aspect):
    """Plot bar chart for new cases on each day."""
    m = len(data.dates) - recent_days if recent else 0
    tick_gap = 100
    text_gap = 0.5
    ylim_pad = 8 if recent else 9

    plot_begin(data)
    plt.bar(formatted_dates[m:], data.total_diffs[m:],
            color=total_color, zorder=2,
            label='New COVID-19 Cases in India on each day')
    for i, value in enumerate(data.total_diffs[m:]):
        plt.text(i, value + text_gap * tick_gap, value, ha='center',
                 rotation='vertical', size='x-small', color=total_color)
    ax = plt.gca()
    ax.yaxis.set_major_locator(mpl.ticker.MultipleLocator(tick_gap * 5))
    ax.yaxis.set_minor_locator(mpl.ticker.MultipleLocator(tick_gap))
    plt.ylabel('Count')
    plt.xlim(left=-0.8, right=len(data.dates[m:]) - 0.2)
    plt.ylim(top=top_ylim(data.total_diffs[m:], tick_gap * ylim_pad, tick_gap))
    plt.ylim(bottom=0)
    plot_end(data, 'new-cases', recent, aspect)


def plot_growth_percents(data, recent, aspect):
    """Plot growth rate for each day."""
    m = len(data.dates) - recent_days - 1 if recent else 0
    tick_gap = 1 if recent else 10
    text_gap = 0.6 if recent else 1.2
    ylim_gap = 8 if recent else 5

    # Preprocess data for plotting.
    growths = data.total_growths
    growth_nan = [float('nan') if g == -1 else g for g in growths]

    # Plot graph.
    plot_begin(data)
    plt.plot(formatted_dates[m:], growth_nan[m:],
             marker='.', color=total_color,
             label='Growth percent in number of total\n'
                   'COVID-19 cases in India on each day\n'
                   'compared to the previous day')

    # Tweak the position of text values on the graph.
    tweaks = [(0, 0)] * len(data.dates)
    if recent:
        tweaks[data.dates.index('2020-04-11')] = ( 0.0, -2.2)
        tweaks[data.dates.index('2020-04-13')] = ( 0.0, -2.2)
        tweaks[data.dates.index('2020-04-15')] = (+0.8, -1.1)
        tweaks[data.dates.index('2020-04-16')] = (+0.0, -1.8)
        tweaks[data.dates.index('2020-04-18')] = ( 0.0, -1.8)
        tweaks[data.dates.index('2020-04-21')] = (+0.2,  0.0)
        tweaks[data.dates.index('2020-04-23')] = ( 0.0,  0.5)
        tweaks[data.dates.index('2020-04-25')] = ( 0.0,  0.5)
        tweaks[data.dates.index('2020-04-27')] = (+0.3,  0.0)
        tweaks[data.dates.index('2020-05-01')] = (-0.1,  0.0)
        tweaks[data.dates.index('2020-05-04')] = ( 0.0, -1.8)
        tweaks[data.dates.index('2020-05-06')] = ( 0.0, -1.8)
    else:
        tweaks[data.dates.index('2020-02-03')] = (+0.3, +0.0)
        tweaks[data.dates.index('2020-02-04')] = (+0.5, +0.0)
        tweaks[data.dates.index('2020-03-03')] = (+0.6, -0.5)
        tweaks[data.dates.index('2020-03-05')] = (-0.6, -1.0)
        tweaks[data.dates.index('2020-03-16')] = (+0.1, +0.0)
        tweaks[data.dates.index('2020-03-22')] = (+0.1, +0.0)

    # Show text values on the graph.
    prev_val = -1
    for i, val in enumerate(growths[m:]):
        if m != 0 and i == 0:
            continue
        if val != -1 and abs(val - prev_val) > 0.0001:
            x = i + tweaks[m:][i][0]
            y = val + (text_gap + tweaks[m:][i][1]) * tick_gap
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
    plt.xlim(left=0.2 if recent else -0.8, right=len(data.dates[m:]) - 0.2)
    plt.ylim(top=top_ylim(growths[m:], tick_gap * ylim_gap, tick_gap))
    plt.ylim(bottom=0)
    plot_end(data, 'growth-percent', recent, aspect)


def plot_doubling_times(data, recent, aspect):
    """Plot line chart for all case numbers (linear scale)."""
    m = len(data.dates) - recent_days - 1 if recent else 0
    tick_gap = 0.2 if recent else 1.0
    text_gap = 1.7 if recent else 1.0
    ylim_pad = 15 if recent else 5

    # Preprocess data for plotting.
    doubling_times = data.doubling_times
    days_nan = [float('nan') if x == -1 else x for x in doubling_times]

    # Plot graph.
    plot_begin(data)
    plt.plot(formatted_dates[m:], days_nan[m:],
             marker='.', color=total_color,
             label='Number of days it took for the number of\n'
                   'total COVID-19 cases in India to double')

    # Tweak the position of text values on the graph.
    tweaks = [(0, 0)] * len(data.dates)
    if recent:
        tweaks[data.dates.index('2020-03-21')] = (+0.0, -4.2)
        tweaks[data.dates.index('2020-03-23')] = (+0.0, -4.2)
        tweaks[data.dates.index('2020-04-01')] = (+0.0, -4.2)
        tweaks[data.dates.index('2020-04-04')] = (-0.1, -0.0)
        tweaks[data.dates.index('2020-04-06')] = (-0.1, -0.0)
        tweaks[data.dates.index('2020-04-14')] = (+0.1, -0.0)
        tweaks[data.dates.index('2020-04-15')] = (-0.1, -0.0)
    else:
        tweaks[data.dates.index('2020-02-04')] = (+0.8, -1.3)
        tweaks[data.dates.index('2020-02-21')] = (+0.8, -1.3)
        tweaks[data.dates.index('2020-02-27')] = (-0.1, +0.1)
        tweaks[data.dates.index('2020-03-03')] = (+0.8, -1.3)
        tweaks[data.dates.index('2020-03-04')] = (+0.3, +0.0)

    # Show text values on the graph.
    prev_val = -1
    for i, val in enumerate(doubling_times[m:]):
        if m != 0 and i == 0:
            continue
        if val != -1 and abs(val - prev_val) > 0.0001:
            x = i + tweaks[m:][i][0]
            y = val + (text_gap + tweaks[m:][i][1]) * tick_gap
            v = '{:.1f}'.format(val)
            plt.text(x, y, v, ha='center', rotation='vertical',
                     size='x-small', color=total_color)
            prev_val = val

    # Format axes.
    ax = plt.gca()
    ax.yaxis.set_major_locator(mpl.ticker.MultipleLocator(tick_gap * 5))
    ax.yaxis.set_minor_locator(mpl.ticker.MultipleLocator(tick_gap))
    plt.ylabel('Days')
    plt.xlim(left=0.2 if recent else -0.8, right=len(data.dates[m:]) - 0.2)
    plt.ylim(top=top_ylim(doubling_times[m:], tick_gap * ylim_pad, tick_gap))
    plt.ylim(bottom=0)
    plot_end(data, 'doubling-time', recent, aspect)


def plot_cured_percents(data, recent, aspect):
    """Plot line chart for cured and death percents."""
    m = len(data.dates) - recent_days - 1 if recent else 0
    tick_gap = 2
    cured_text_gap = -3.7
    death_text_gap = 1.5

    # Preprocess data for plotting.
    cured_nan = [float('nan') if x == -1 else x for x in data.cured_percents]
    death_nan = [float('nan') if x == -1 else x for x in data.death_percents]

    # Plot graph.
    plot_begin(data)
    plt.plot(formatted_dates[m:], cured_nan[m:],
             marker='.', color=cured_color,
             label='Percent of closed cases that are cured cases')
    plt.plot(formatted_dates[m:], death_nan[m:],
             marker='.', color=death_color,
             label='Percent of closed cases that are death cases')

    # Tweak the position of text values on the graph.
    cured_tweaks = [(0, 0)] * len(data.dates)
    death_tweaks = [(0, 0)] * len(data.dates)
    if recent:
        pass
    else:
        cured_tweaks[data.dates.index('2020-03-13')] = (+0.3, +0.0)
        death_tweaks[data.dates.index('2020-03-13')] = (+0.3, +0.0)

    # Show values on the graph.
    prev_cured = -1
    for i, (cured, death) in enumerate(zip(data.cured_percents[m:],
                                           data.death_percents[m:])):
        if m != 0 and i == 0:
            continue
        if cured != -1 and abs(cured - prev_cured) > 0.001:
            # Print cured value.
            x = i + cured_tweaks[i][0]
            y = cured + (cured_text_gap + cured_tweaks[m:][i][1]) * tick_gap
            v = '{:.0f}%'.format(cured)
            plt.text(x, y, v, ha='center', rotation='vertical',
                     size='x-small', color=cured_color)
            # Print death value.
            x = i + death_tweaks[i][0]
            y = death + (death_text_gap + death_tweaks[m:][i][1]) * tick_gap
            v = '{:.0f}%'.format(death)
            plt.text(x, y, v, ha='center', rotation='vertical',
                     size='x-small', color=death_color)
            prev_cured = cured

    # Format axes.
    ax = plt.gca()
    ax.yaxis.set_major_locator(mpl.ticker.MultipleLocator(tick_gap * 5))
    ax.yaxis.set_minor_locator(mpl.ticker.MultipleLocator(tick_gap))
    ax.yaxis.set_major_formatter(mpl.ticker.FuncFormatter(percent_formatter))
    plt.ylabel('Percent')
    plt.xlim(left=0.2 if recent else -0.8, right=len(data.dates[m:]) - 0.2)
    plt.ylim(top=100)
    plt.ylim(bottom=0)
    plot_end(data, 'cured-percent', recent, aspect)


def plot_cured_ratios(data, recent, aspect):
    """Plot line chart for cured ratio."""
    m = len(data.dates) - recent_days - 1 if recent else 0
    tick_gap = 0.1
    text_gap = 2.1
    ylim_pad = 20 if recent else 22

    # Preprocess data for plotting.
    ratios = data.cured_ratios
    cured_nan = [float('nan') if x == -1 else x for x in ratios]

    # Plot graph.
    plot_begin(data)
    plt.plot(formatted_dates[m:], cured_nan[m:],
             marker='.', color=cured_color,
             label='Number of cured cases per death case\n'
                   'among closed COVID-19 cases in India')

    # Print values on the graph.
    tweaks = [(0, 0)] * len(data.dates)
    tweaks[data.dates.index('2020-03-12')] = (+0.8, -1.7)
    tweaks[data.dates.index('2020-03-17')] = (+0.5, +0.0)
    tweaks[data.dates.index('2020-03-19')] = (-0.3, +0.0)
    tweaks[data.dates.index('2020-03-22')] = (+0.0, -6.5)
    tweaks[data.dates.index('2020-03-26')] = (+0.0, -6.5)
    tweaks[data.dates.index('2020-03-27')] = (-0.2, +0.0)
    tweaks[data.dates.index('2020-03-29')] = (+0.3, +0.0)
    tweaks[data.dates.index('2020-04-02')] = (+0.2, +0.0)
    tweaks[data.dates.index('2020-04-04')] = (-0.2, +0.0)
    tweaks[data.dates.index('2020-04-06')] = (+0.2, +0.0)
    tweaks[data.dates.index('2020-04-21')] = (-0.2, +0.2)
    prev_val = -1
    for i, val in enumerate(ratios[m:]):
        if m != 0 and i == 0:
            continue
        if val != -1 and abs(val - prev_val) > 0.0001:
            x = i + tweaks[m:][i][0]
            y = val + (text_gap + tweaks[m:][i][1]) * tick_gap
            v = '{:.1f}'.format(val)
            plt.text(x, y, v, ha='center', rotation='vertical',
                     size='x-small', color=cured_color)
            prev_val = val

    # Format axes.
    ax = plt.gca()
    ax.yaxis.set_major_locator(mpl.ticker.MultipleLocator(tick_gap * 5))
    ax.yaxis.set_minor_locator(mpl.ticker.MultipleLocator(tick_gap))
    plt.ylabel('Ratio')
    plt.xlim(left=0.2 if recent else -0.8, right=len(data.dates[m:]) - 0.2)
    plt.ylim(top=top_ylim(ratios[m:], tick_gap * ylim_pad, tick_gap))
    plt.ylim(bottom=0)
    plot_end(data, 'cured-ratio', recent, aspect)


def plot_all(data):
    """Plot all graphs."""
    log.log('Rendering total-cases-linear-recent plot ...')
    plot_total_cases_linear(data, recent=True, aspect='square')

    log.log('Rendering total-cases-linear plot ...')
    plot_total_cases_linear(data, recent=False, aspect=None)

    log.log('Rendering total-cases-log-recent plot ...')
    plot_total_cases_log(data, recent=True, aspect='square')

    log.log('Rendering total-cases-log plot ...')
    plot_total_cases_log(data, recent=False, aspect=None)

    log.log('Rendering new-cases-recent plot ...')
    plot_new_cases(data, recent=True, aspect='square')

    log.log('Rendering new-cases plot ...')
    plot_new_cases(data, recent=False, aspect=None)

    log.log('Rendering growth-percents-recent plot ...')
    plot_growth_percents(data, recent=True, aspect='square')

    log.log('Rendering growth-percents plot ...')
    plot_growth_percents(data, recent=False, aspect=None)

    log.log('Rendering doubling-times-recent plot ...')
    plot_doubling_times(data, recent=True, aspect='square')

    log.log('Rendering doubling-times plot ...')
    plot_doubling_times(data, recent=False, aspect=None)

    log.log('Rendering cured-percents-recent plot ...')
    plot_cured_percents(data, recent=True, aspect='square')

    log.log('Rendering cured-percents plot ...')
    plot_cured_percents(data, recent=False, aspect=None)

    log.log('Rendering cured-ratios-percent plot ...')
    plot_cured_ratios(data, recent=True, aspect='square')

    log.log('Rendering cured-ratios plot ...')
    plot_cured_ratios(data, recent=False, aspect=None)


def plot_recent_wide(data):
    """Plot recent graphs only in approx. with 16:9 aspect ratio."""
    log.log('Rendering total-cases-linear-recent plot ...')
    plot_total_cases_linear(data, recent=True, aspect='wide')

    log.log('Rendering total-cases-log-recent plot ...')
    plot_total_cases_log(data, recent=True, aspect='wide')

    log.log('Rendering new-cases-recent plot ...')
    plot_new_cases(data, recent=True, aspect='wide')

    log.log('Rendering growth-percents-recent plot ...')
    plot_growth_percents(data, recent=True, aspect='wide')

    log.log('Rendering doubling-times-recent plot ...')
    plot_doubling_times(data, recent=True, aspect='wide')

    log.log('Rendering cured-percents-recent plot ...')
    plot_cured_percents(data, recent=True, aspect='wide')

    log.log('Rendering cured-ratios-percent plot ...')
    plot_cured_ratios(data, recent=True, aspect='wide')


def linear_label_formatter(x, pos):
    """Return tick label for linear scale."""
    if x % 100 == 0:
        return int(x)


def log_label_formatter(x, pos):
    """Return tick label for log scale."""
    if str(x)[0] in ['1', '2', '4', '6']:
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
    parser = argparse.ArgumentParser()
    parser.add_argument('-w', action='store_true',
                        help='Plot recent graphs only with 16:9 aspect ratio')
    args = parser.parse_args()

    data = archive.load()
    if args.w:
        plot_recent_wide(data)
    else:
        plot_all(data)


if __name__ == '__main__':
    main()
