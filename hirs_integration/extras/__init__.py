# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

__all__ = ('setup')

def setup():
    """Imports the data folder in to the database"""
    import csv
    import os
    from . import models

    for file in os.listdir(os.path.join(os.path.dirname(__file__), 'data')):
        if file.endswith('.csv') and hasattr(models, file.split('.')[0]):
            model = getattr(models, file.split('.')[0])
            with open(os.path.join(os.path.dirname(__file__), 'data', file), 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    data = parse_row(row,model.data_targets)
                    model.objects.create(**data)
                    del data

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
            data[field[1]] = eval(field[2],row[field[0]])
    return data