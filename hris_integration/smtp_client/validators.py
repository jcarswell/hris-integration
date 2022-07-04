# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from hris_integration.validators import ValidationError
from common.functions import model_to_choices

__all__ = ("email_template_list",)


def email_template_list(none: bool = True):
    """Returns a Choice iterator for the available email templates

    :param none: Include the None or unset option, defaults to True
    :type none: bool, optional
    :return: Django choice objects
    :rtype: iterable
    """

    from smtp_client.models import EmailTemplates

    return model_to_choices(EmailTemplates.objects.all(), none=none)
