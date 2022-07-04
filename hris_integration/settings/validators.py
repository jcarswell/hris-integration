# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from hris_integration.validators import ValidationError


def setting_parse(setting=None, html_id: str = None):
    """
    Converts either a Setting object to an html safe id that can be back parsed
    or converts a html safe id into a Setting object

    :param setting: Returns an html safe id from the reference object, defaults to None
    :type setting: Settings, optional
    :param html_id: Returns a tuple from the html safe id, defaults to None
    :type html_id: str, optional
    :raises ValueError: _description_
    :raises ValidationError: if the html_id is not a valid or parsable html safe id
    :raises Exception: If you get this error you probably forgot to specify a setting or html_id
    :return: the converted object
    :rtype: string for setting, Settings for html_id
    """

    from .models import Setting

    if setting and isinstance(setting, Setting):
        return ".".join(setting.setting.split(Setting.FIELD_SEP))
    if html_id and isinstance(html_id, str):
        s = html_id.split(".")
        if len(s) != 3:
            raise ValidationError(
                "Provided ID is not a properly formatted setting id string"
            )
        qs = Setting.o2.get_by_path(*s)
        if len(qs) != 1:
            raise ValidationError("provided ID did not return a valid settings object")
        return qs[0]
    raise Exception("Mother Fucker that's not how this works.")
