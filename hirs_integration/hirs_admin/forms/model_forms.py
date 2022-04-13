# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

from django.utils.translation import gettext_lazy as _t
from hris_integration.forms import Form,MetaBase

from hirs_admin import models


class WordList(Form):
    name = _t("Word Expansion Map")
    class Meta(MetaBase):
        model = models.WordList
        fields = ('id','src','replace')
        labels = {
            'src': _t("Source Pattern"),
            'replace': _t("Substitution")
        }
        disabled = ('id',)
        required = ('src','replace')
