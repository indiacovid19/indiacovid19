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


import os
import re
import shutil

from py import data, plot


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


def case_rows():
    """Create HTML to display row of case numbers in a table."""
    output = ''
    for i, entry in enumerate(zip(data.dates,
                                  data.total_cases,
                                  data.total_diff,
                                  data.total_growth,
                                  data.active_cases,
                                  data.cured_cases,
                                  data.death_cases,
                                  data.ref_dates,
                                  data.ref_links)):

        (date, total, new, growth, active, cured, deaths,
         ref_date, ref_link) = entry

        if growth == -1:
            growth = '-'
        else:
            growth = '{:+.0f}%'.format(100 * (growth - 1))

        output += '  <tr>'
        output += '    <td class="date">{}</td>'.format(date)
        output += '    <td class="total">{}</td>'.format(total)
        output += '    <td class="total">{:+}</td>'.format(new)
        output += '    <td class="total">{}</td>'.format(growth)
        output += '    <td class="active">{}</td>'.format(active)
        output += '    <td class="cured">{}</td>'.format(cured)
        output += '    <td class="death">{}</td>'.format(deaths)
        output += '    <td class="ref"><a href="{}">{}</a></td>'.format(
                   ref_link, ref_date.replace(' ', '&nbsp;'))
        output += '  </tr>'
    return output


def main():
    """Render the home page."""
    # Copy static files.
    if os.path.isdir('_site'):
        shutil.rmtree('_site')
    shutil.copytree('static', '_site')
    shutil.copy('indiacovid19.json', '_site')

    # Load COVID-19 data.
    data.load()

    # Plot graphs.
    plot.all_cases()
    plot.new_cases()

    # Render home page.
    layout = fread('layout/index.html')
    output = render(layout, case_rows=case_rows())
    fwrite('_site/index.html', output)


if __name__ == '__main__':
    main()
