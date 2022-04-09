# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

import logging

from hirs_admin.models import Setting

logger = logging.getLogger('hirs_admin.config')


def setting_parse(setting:Setting =None,html_id:str =None):
    """Converts either a Setting object to an html safe id that can be back parsed
    or converts a html safe id into a Setting object

    Args:
        object (Setting, optional): Returns an html safe id from the reference object
        html_id (str, optional): [description]. Returns a tuple from the html safe id.

    Raises:
        ValueError: if the html_id is not a valid or parsable html safe id
    """
    if setting and isinstance(setting,Setting):
        return ".".join(setting.setting.split(Setting.FIELD_SEP))
    if html_id and isinstance(html_id,str):
        s = html_id.split('.')
        if len(s) != 3:
            raise ValueError("provided ID is not a properly formated setting id string")
        qs = Setting.o2.get_by_path(*s)
        if len(qs) != 1:
            raise ValueError("provided ID did not return a valid settings object")
        return qs[0]
    raise Exception("Mother Fucker that's not how this works.")