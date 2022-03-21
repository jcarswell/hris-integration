# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

from common.validators import ValidationError
from common.functions import model_to_choices
from .models import EmailTemplates

def template_list(none:bool =True):
    """Returns a Choice iterator for the available email templates

    :param none: Include the None or unset option, defaults to True
    :type none: bool, optional
    :return: Django choice objects
    :rtype: iterable
    """

    return model_to_choices(EmailTemplates.objects.all(),none)