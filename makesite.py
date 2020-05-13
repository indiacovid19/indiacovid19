#!/usr/bin/env python3

# Copyright (c) 2020 Susam Pal
# Licensed under the terms of the MIT License.

# This software is a derivative of the original makesite.py available at
# <https://github.com/sunainapai/makesite>. The license text of the
# original makesite.py is included below.

# The MIT License (MIT)
#
# Copyright (c) 2018 Sunaina Pai
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
import os
import re
import shutil
import sys

from py import archive, log, plot


def fread(filename):
    """Read file and close the file."""
    with open(filename, 'r') as f:
        return f.read()


def fwrite(filename, text):
    """Write content to file and close the file."""
    basedir = os.path.dirname(filename)
    if not os.path.isdir(basedir):
        os.makedirs(basedir)
    with open(filename, 'w') as f:
        f.write(text)


def render(template, **params):
    """Replace placeholders in template with values from params."""
    return re.sub(r'{{\s*([^}\s]+)\s*}}',
                  lambda match: str(params.get(match.group(1), match.group(0))),
                  template)


def case_links(data):
    """Create HTML to display navigation links for case numbers table."""
    prev_month = None
    months = []
    for date in data.dates:
        curr_month = date[:7]
        if curr_month != prev_month:
            months.append(curr_month)
        prev_month = curr_month

    out = []
    for month in months:
        text = datetime.datetime.strptime(month, '%Y-%m').strftime('%b')
        out.append('    <a href="#{}">[{}]</a>'.format(month, text))
    return '\n'.join(out) + '\n'


def case_head(month):
    """Create HTML to display table heading for case numbers table."""
    th_date = datetime.datetime.strptime(month, '%Y-%m').strftime('%b&nbsp;%Y')
    out = [
        '    <tr id="{}">'.format(month),
        '      <th class="date"><a href="#{}">Date ({})</a></th>'
        .format(month, th_date),
        '      <th class="total">Total Cases</th>',
        '      <th class="total">New Cases</th>',
        '      <th class="total">Growth</th>',
        '      <th class="total">Doubling Time' +
        '<sup><a href="#footnote1">*</a></sup></th>',
        '      <th class="active">Active Cases</th>',
        '      <th class="cured">Cured Cases</th>',
        '      <th class="death">Death Cases</th>',
        '      <th class="ref">References' +
        '<sup><a href="#footnote2">&dagger;</a></sup></th>',
        '    </tr>',
    ]
    return '\n'.join(out) + '\n'


def case_refs(date, refs):
    """Create HTML to display a list of refs in case numbers table."""
    out = []
    for ref_date, ref_link, ref_comment in refs:
        ref_date, ref_time = ref_date[:10], ref_date[11:]
        ref_day = ''
        if date != ref_date:
            entry_datetime = datetime.datetime.strptime(date, '%Y-%m-%d')
            ref_datetime = datetime.datetime.strptime(ref_date, '%Y-%m-%d')
            plus = (ref_datetime - entry_datetime).days
            ref_day = '<a href="#footnote3"><sup>+{}d</sup></a>'.format(plus)
        out.extend(['{}<a href="{}">{}</a>'
                    .format(ref_day, ref_link, ref_time)])
    return ', '.join(out)


def case_data(entry):
    """Create HTML to display a row of entry in case numbers table."""
    (date, total, new, growth, days, active, cured, deaths, refs) = entry

    if growth == -1:
        growth = '-'
    else:
        growth = plot.plus_percent_str(growth)

    if days == -1:
        days = '-'
    else:
        days = '{:.1f}d'.format(days)

    out = [
        '    <tr id="{}">'.format(date),
        '      <td class="date"><a href="#{}">{}</a></td>'.format(date, date),
        '      <td class="total">{}</td>'.format(total),
        '      <td class="total">{:+}</td>'.format(new),
        '      <td class="total">{}</td>'.format(growth),
        '      <td class="total">{}</td>'.format(days),
        '      <td class="active">{}</td>'.format(active),
        '      <td class="cured">{}</td>'.format(cured),
        '      <td class="death">{}</td>'.format(deaths),
        '      <td class="ref">{}</td>'.format(case_refs(date, refs)),
        '    </tr>',
    ]
    return '\n'.join(out) + '\n'


def case_rows(data):
    """Create HTML to display row of case numbers in a table."""
    prev_month = None
    out = ''
    for i, entry in enumerate(zip(data.dates,
                                  data.total_cases,
                                  data.total_diffs,
                                  data.total_growths,
                                  data.doubling_times,
                                  data.active_cases,
                                  data.cured_cases,
                                  data.death_cases,
                                  data.refs)):
        curr_month = entry[0][:7]
        if curr_month != prev_month:
            out += case_head(curr_month)
        out += case_data(entry)
        prev_month = curr_month
    return out


def main():
    """Render the home page."""
    # Copy static files.
    if os.path.isdir('_site'):
        shutil.rmtree('_site')
    shutil.copytree('static', '_site')
    shutil.copy('indiacovid19.json', '_site')

    # Load COVID-19 archive data.
    log.log('Loading archive ...')
    data = archive.load()
    log.log('Found entries for {} days', len(data.dates))

    # Format placeholder values.
    last_updated = data.last_ref_datetimes[-1].strftime('%d %b %Y %H:%M IST')
    new_growth = plot.plus_percent_str(data.total_growths[-1])
    doubling_time = '{:.1f}'.format(data.doubling_times[-1])
    cured_percent = '{:.0f}%'.format(data.cured_percents[-1])
    death_percent = '{:.0f}%'.format(data.death_percents[-1])
    cured_ratio = '{:.1f}'.format(data.cured_ratios[-1])
    img_max_width = round(len(data.dates) * 100 / 40)

    # Render home page.
    log.log('Rendering home page ...')
    layout = fread('layout/index.html')
    output = render(layout,
                    last_total=data.total_cases[-1],
                    last_active=data.active_cases[-1],
                    last_cured=data.cured_cases[-1],
                    last_death=data.death_cases[-1],
                    last_date=data.dates[-1],
                    last_updated=last_updated,
                    new_cases=data.total_diffs[-1],
                    new_growth=new_growth,
                    doubling_time=doubling_time,
                    cured_percent=cured_percent,
                    death_percent=death_percent,
                    cured_ratio=cured_ratio,
                    case_links=case_links(data),
                    case_rows=case_rows(data))
    fwrite('_site/index.html', output)

    # Render CSS.
    log.log('Rendering stylesheet ...')
    layout = fread('layout/main.css')
    output = render(layout, img_max_width=img_max_width)
    fwrite('_site/main.css', output)

    # Plot graphs.
    plot.plot_all(data)
    log.log('Done')


if __name__ == '__main__':
    main()
