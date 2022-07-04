# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

from hris_integration.validators import ValidationError
from string import digits

__all__ = ('cron_validator',)

def cron_validator(value):
    def char_validate(str_list):
        for c in str_list:
            if c not in ['*','/',','] + list(digits):
                raise ValidationError("got invlaid charater in cron job. Allowed characters are 0-9, * and /")

    def place_validate(place,min,max):
        if '/' in list(place):
            values = place.split('/')
            if values[0] != '*':
                raise ValidationError(f"cron value with step must start with *: {place}")
            if not min <= int(values[1]) <= max:
                raise ValidationError(f"cron step value '{values[1]}'' outside of valid range '{min}-{max}'")
        elif ',' in list(place):
            values = place.split(',')
            for v in values:
                place_validate(v,min,max)
        elif place != '*' and not min <= int(place) <= max:
            raise ValidationError(f"cron value '{place}'' outside of valid range '{min}-{max}'")

    if not isinstance(value,str):
        raise ValidationError(f"Expected str got {value.__class__.__name__}")
    
    cron = value.split()
    if len(cron) != 5:
        raise ValidationError(f"Cron schedule should be 5 segments. got {len(cron)}")
    
    # cron[0] == minute
    char_validate(list(cron[0]))
    place_validate(cron[0],0,59)
    
    # cron[1] == hour
    char_validate(list(cron[1]))
    place_validate(cron[1],0,23)

    # cron[2] == day
    char_validate(list(cron[2]))
    place_validate(cron[2],1,31)

    # cron[3] == month
    char_validate(list(cron[3]))
    place_validate(cron[3],1,12)

    # cron[4] == day of week
    char_validate(list(cron[4]))
    place_validate(cron[4],0,6)