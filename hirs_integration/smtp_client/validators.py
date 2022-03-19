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