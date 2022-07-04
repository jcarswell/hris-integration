# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

import unittest

from hirs_admin import validators
from django.core.exceptions import ValidationError

class TestValidators(unittest.TestCase):
    def test_cron(self):
        validators.cron_validator('* * * * *')
        self.assertRaises(validators.cron_validator('70 * * * *'),ValidationError)
        self.assertRaises(validators.cron_validator('* 70 * * *'),ValidationError)
        self.assertRaises(validators.cron_validator('* * 70 * *'),ValidationError)
        self.assertRaises(validators.cron_validator('* * * 70 *'),ValidationError)
        self.assertRaises(validators.cron_validator('* * * * 70'),ValidationError)
        self.assertRaises(validators.cron_validator('a * * * *'),ValidationError)
        self.assertRaises(validators.cron_validator('* a * * *'),ValidationError)
        self.assertRaises(validators.cron_validator('* * a * *'),ValidationError)
        self.assertRaises(validators.cron_validator('* * * a *'),ValidationError)
        self.assertRaises(validators.cron_validator('* * * * a'),ValidationError)
        validators.cron_validator('1/2 * * * *')
        validators.cron_validator('* 1/2 * * *')
        validators.cron_validator('* * 1/2 * *')
        validators.cron_validator('* * * 1/2 *')
        validators.cron_validator('* * * * 1/2')
        validators.cron_validator('*,1/2 * * * *')
        validators.cron_validator('* *,1/2 * * *')
        validators.cron_validator('* * *,1/2 * *')
        validators.cron_validator('* * * *,1/2 *')
        validators.cron_validator('* * * * *,1/2')
        validators.cron_validator('2,*/2 * * * *')
        validators.cron_validator('* 2,*/2 * * *')
        validators.cron_validator('* * 2,*/2 * *')
        validators.cron_validator('* * * 2,*/2 *')
        validators.cron_validator('* * * * 2,*/2')
        validators.cron_validator('*/2 * * * *')
        validators.cron_validator('* */2 * * *')
        validators.cron_validator('* * */2 * *')
        validators.cron_validator('* * * */2 *')
        validators.cron_validator('* * * * */2')
        validators.cron_validator('4 4 4 4 4')