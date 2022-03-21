# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _t

class CorepointExportConfig(AppConfig):
    name = 'corepoint_export'
    verbose_name = _t('Corepoint Export')
    default_auto_field = 'django.db.models.AutoField'