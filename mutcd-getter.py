#!/usr/bin/env python
"""Get MUTCD SVGs from Wikipedia."""

import urllib
import argparse
import os
import json

from lxml import html
import wikipedia
from pyquery import PyQuery


class MUTCDGetterError(Exception):
    pass


# Setup arguments.
parser = argparse.ArgumentParser()
parser.add_argument('--title', default='Comparison of MUTCD-Influenced Traffic Signs',
                    help='The title of the Wikipedia entry containing the tables of MUTCD-inspired signs.')
parser.add_argument('--tables', default='Warning,Regulatory,Mandatory or permitted actions,Other (indication)',
                    help='The headers of the tables whose signs you wish to retrieve.')
parser.add_argument('--column', default='USA',
                    help='The identifier representing the column you wish to pull from each table (e.g. 5, or "USA").')
parser.add_argument('--output_folder', default=os.getcwd(),
                    help='The path to the folder into which the signage and common names file should be downloaded.')
parser.add_argument('--common_names_filename', default='mutcd_common_names.json',
                    help='The filename for the JSON-formatted file mapping common sign names to SVG file names.')
parsed_args = parser.parse_args()

# Get the requested article.
print('Fetching the wikipedia page...')
wiki_page = wikipedia.page(parsed_args.title)

# Parse the html and wrap it in pyquery.
d = PyQuery(html.fromstring(wiki_page.html()))

# Get a list of all headers in the document, to be filtered later for each table's header.
all_headers = d(':header')

# Create a data structure to store sign data and filenames.
signs = []
raw_filename_map = {}

print('Finding the SVGs. Hang tight. This may take a couple of minutes.\n')

# For each table header, get the associated table.
table_headers = parsed_args.tables.split(',')
for table_header in table_headers:
    table_signs = {
        'type': 'category',
        'text': table_header,
        'data': []
    }

    table = PyQuery(all_headers.filter(lambda: this.text_content() == table_header + '[edit]').next_all('table')[0])
    first_row = table('tr:nth-child(1)')

    column = parsed_args.column
    if isinstance(column, str):
        # If the provided column is a string, find the column index. While this is probably the same for each table,
        # we'll still check every time. It's cheap and this is an infrequent script.
        for i, header_cell in enumerate(first_row.find('th')):
            if header_cell.text_content().strip().startswith(column):
                column = i
                break
        if isinstance(column, str):
            # We couldn't find it.
            raise MUTCDGetterError('The specified column header could not be found.')

    # Get all rows following the first row.
    table_rows = first_row.next_all('tr')
    for row in table_rows:
        row = PyQuery(row)

        # Due to a current pyquery bug, nth-child does not work right.
        row_header = PyQuery(row.find('td')[0]).text()

        if not row_header:
            # This is an intermediary header row to remind readers which column is which.
            continue

        target_cell_imgs = PyQuery(row.find('td')[column]).find('img[alt$=svg]')

        if not target_cell_imgs:
            continue

        row_sign_filenames = []

        target_cell_imgs.each(lambda: row_sign_filenames.append(
            {
                'type': 'sign filename',
                'text': PyQuery(this).attr('alt').replace(' ', '_'),
            }
        ))

        filenames_to_remove = []
        for filename in row_sign_filenames:
            # Download the SVG(s).
            try:
                image_page = PyQuery('http://en.wikipedia.org/wiki/File:{}'.format(filename['text']))
                svg_link = image_page.find('a.internal').filter(lambda: this.text_content().strip() == 'Original file')
                svg_url = svg_link.attr('href')

                if not svg_url:
                    print(
                        'Could not find URL for {table_header}: {row_header}: {filename}\n'.format(
                            table_header=table_header,
                            row_header=row_header,
                            filename=filename['text']
                        )
                    )

                if svg_url.startswith('//'):
                    # De-relativize to an absolute URL.
                    svg_url = 'http:' + svg_url

                urllib.urlretrieve(svg_url, os.path.join(parsed_args.output_folder, filename['text']))

                raw_filename_map[filename['text']] = {
                    'category': table_header,
                    'commonName': row_header,
                }
            except KeyboardInterrupt:
                raise
            except:
                # Plan for success, prepare for absolute destruction of everything you hold dear.
                print(
                    'An unknown error occurred while attempting to retrieve '
                    '{table_header}: {row_header}: {filename}\n'.format(
                        table_header=table_header,
                        row_header=row_header,
                        filename=filename['text']
                    )
                )

                filenames_to_remove.append(filename)

        for filename in filenames_to_remove:
            row_sign_filenames.remove(filename)

        if row_sign_filenames:
            table_signs['data'].append({
                'type': 'common name',
                'text': row_header,
                'data': row_sign_filenames,
            })

    if table_signs['data']:
        signs.append(table_signs)

with open(os.path.join(parsed_args.output_folder, parsed_args.common_names_filename), 'w') as json_file:
    json.dump({'signs': signs, 'rawFilenameMap': raw_filename_map}, json_file, indent=4)

print('\nAll files written. Enjoy!')
