# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

import logging

from .app import ExtrasConfig

__all__ = ('ExtrasConfig','setup')
logger = logging.getLogger("extras.setup")

def setup():
    """Imports the data folder in to the database"""
    import csv
    import os
    from .models import world_data

    for file in os.listdir(os.path.join(os.path.dirname(__file__), 'data')):
        logger.debug(f"reading in {file}")
        if file.endswith('.csv') and hasattr(world_data, file.split('.')[0]):
            model = getattr(world_data, file.split('.')[0])
            with open(os.path.join(os.path.dirname(__file__), 'data', file), 'r',
                    encoding='utf-8') as csvfile:
                rows = 0
                reader = csv.DictReader(csvfile)
                for row in reader:
                    data = parse_row(row,model.data_targets)
                    o,new = model.objects.get_or_create(**data)
                    if new:
                        o.save()
                        rows += 1
                    del o
                    del data

                logger.debug(f"{rows} rows imported")

def parse_row(row:dict,parser:list) -> dict:
    """
    Parses a row from the CSV file

    :param row: The row to parse
    :type row: dict
    :param parser: The parser to use expect the list to contain a tuple in the form of
        (field,type,eval function)
    :type parser: list[tuple[str,str,object]]
    :return: The parsed row
    :rtype: dict
    """

    data = {}
    for field in parser:
        if field[0] in row:
            data[field[1]] = field[2](row[field[0]])
    return data