# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _t


class UserApplicationsConfig(AppConfig):
    name = "user_applications"
    verbose_name = _t("User Applications")
    default_auto_field = "django.db.models.AutoField"
