# mutcd-getter
This script downloads MUTCD-related signage SVGs from Wikipedia and includes
a JSON-formatted mapping of common sign names to filenames.

## Requirements
The following Python libraries are required by the script:

    lxml
    wikipedia
    pyquery

A simple `pip install lxml wikipedia pyquery` should take care of these
requirements, though you may need some dev libraries and building tools to
compile `lxml`. You may have luck finding a pre-built binary [here](http://lxml.de/installation.html).

## Usage
The most basic example is

    python mutcd-getter.py

which will retrieve all the SVGs into the working directory. The full usage
list of options is as follows:

    --title               The title of the Wikipedia entry containing the
                          tables of MUTCD-inspired signs.
    --tables              The headers of the tables whose signs you wish to
                          retrieve.
    --column              The identifier representing the column you wish to
                          pull from each table (e.g. 5, or "USA").
    --output_folder       The path to the folder into which the signage and
                          common names file should be downloaded.
    --common_names_filename
                          The filename for the JSON-formatted file mapping
                          common sign names to SVG file names.

### --tables Option
The `--tables` option takes a comma-separated list of table headers. SVGs will
only be pulled from these tables. The default list of table headers is

    Warning,Regulatory,Mandatory or permitted actions,Other (indication)

### --column Option
It is expected to be an integer (representing a 0-indexed column number) or
a string (representing the starting text of a column header). The default for
`--column` is 'USA', such that only USA signage SVGs will be downloaded.
`--column` only takes a single argument.

## Why?
Well, I needed some MUTCD signage SVGs. So, that's why.

## License
This software is licensed with the MIT license. Knock yourself out.
