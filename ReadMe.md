This is a quick tool that converts a CSV in the format

    itemID,locationID,X,Y,Z
    1013156298630,30045312,1799358501536,31355412970,-6456266711164
    1013987379821,30045312,1818790794537,28961390992,-5219429291407

into

    itemID,locationID,celestialID,celestialName,X,Y,Z
    1013156298630,30045312,40347994,Korasen VII - Moon 2,1799358501536,31355412970,-6456266711164
    1013987379821,30045312,40347994,Korasen VII - Moon 2,1818790794537,28961390992,-5219429291407

Why is this useful? If you (or your corp) have multiple POSes in one system
it's not possible just by looking at the API which POS modules are on which
POS. The [Corp/Locations](https://neweden-dev.com/Corp/Locations) endpoint was
added to help with this (and also allows individuals to look up ship names
through the API as well). The missing link is that the Locations endpoint
only gives you the coordinates of the item in space, not the ID or name of the
closest celestial. These scripts set up a database and then use it to find the
closest celestial given the necessary coordinates.

## Setup

It's super bare-bones, and requires some manual setup to get working. It
requires recent versions of PostgreSQL and PostGIS. The easy way to get them
(on OS X) is to download [Postgres.app](http://postgresapp.com/). Set up
instructions for creating the database and the schema are in the `load_db.py`
file. It also requires access to the EVE static data export. The easy way to do
that is to download the SQLite version from Steve Ronuken's
[conversions](https://www.fuzzwork.co.uk/dump/).

## Usage

Example usage (using the default database name `ccp_locations` and the SQLite
filename of sqlite-latest.sqlite stored next to the scripts):

    $ ./load_db.py
    $ ./process_csv.py input.csv

To easily generate the input CSV file, you can use
[this spreadsheet](https://docs.google.com/spreadsheets/d/1JHDI8ih5olebM5lu5jT_7oLF2q_QJn3ITLhQ5Wg3474/edit?usp=sharing).
Make a copy and fill in the three cells in the Config sheet with the
information from an API key. The key needs the AssetList and Locations access
mask. If it's a character key, it needs to be for a single character, and
you'll need to change the value of the Scope value from 'Corp' to 'Char'. Let
the various ImportXML functions do their ork, then export the Output sheet
using 'File' -> 'Download As...' -> 'Comma-separated values (.csv,
current sheet)'. This means you'll need the Output sheet displayed to get it to
export properly. Give the path to the downloaded file as an argument to the
process\_csv.py script.
