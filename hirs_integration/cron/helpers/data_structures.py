# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

from cron.validators import cron_validator,ValidationError

class CronJob:
    """A Dict like object that is setup specifically to handle
    the schedule for a cron job. CronJob take one argument of
    a string that's a valid cron schedule. From the minute,
    hour, day, month and day_of_week variable are populated
    with a list of valid matching times. Theses variable can
    also be accessed by postion instead of name.
    If being used to create a new scheduled, either the full
    schedule string or schedule values can be passed to the 
    setup method or each item can be set on the class as a dict
    and then setup called to ensure everything is set right.
    the str method returns the formated cron schedule.

    Raises:
        ValueError: when the provided string does not match that
            of a valid cron schedule
    """

    minute = None
    hour = None
    day = None
    month = None
    day_of_week = None
    _MINUTE = None
    _HOUR = None
    _DAY = None
    _MONTH = None
    _DAY_OF_WEEK = None
    
    _CRON_MAP = {
        'minute': '_MINUTE',
        'hour': '_HOUR',
        'day': '_DAY',
        'month': '_MONTH',
        'day_of_week': '_DAY_OF_WEEK',
        '0': '_MINUTE',
        '1': '_HOUR',
        '2': '_DAY',
        '3': '_MONTH',
        '4': '_DAY_OF_WEEK',
        0: '_MINUTE',
        1: '_HOUR',
        2: '_DAY',
        3: '_MONTH',
        4: '_DAY_OF_WEEK'
        }

    def __init__(self,cron_schedule:str =None, **kwargs) -> None:
        self.setup(cron_schedule, **kwargs)

    def setup(self,cron_schedule:str =None, **kwargs):
        if cron_schedule != None:
            try:
                cron_validator(cron_schedule)
            except ValidationError as e:
                raise ValidationError(str(e))

            sched = cron_schedule.split()
            if len(sched) != 5:
                raise ValueError(f"Expected 5 segments got {len(sched)}")
            self._MINUTE = sched[0]
            self._HOUR = sched[1]
            self._DAY = sched[2]
            self._MONTH = sched[3]
            self._DAY_OF_WEEK = sched[4]
        
        for k,v in kwargs.items():
            if k in self._CRON_MAP:
                setattr(self,self._CRON_MAP[k],v)

        self.minute = self._to_list(self._MINUTE or '*',list(range(60)))
        self.hour = self._to_list(self._HOUR or '*',list(range(24)))
        self.day = self._to_list(self._DAY or '*',list(range(1,32)))
        self.month = self._to_list(self._MONTH or '*',list(range(1,13)))
        self.day_of_week = self._to_list(self._DAY_OF_WEEK or '*',list(range(7)))

    def _to_list(self,val:str,default:list) -> list:
        if val == "*":
            return default

        elif len(val.split('/')) == 2:
            mply = int(val.split('/')[1])
            ret = []
            for x in default:
                if x % mply == 0:
                    ret.append(x)
            return ret

        elif len(val.split(',')) > 1:
            ret = []
            for v in val.split(','):
                ret.append(self._to_list(v))
            return val.split(',')

        else:
            return [int(val)]

    def __str__(self) -> str:
        return f"{self._MINUTE} {self._HOUR} {self._DAY} {self._MONTH} {self._DAY_OF_WEEK}"

    def __getitem__(self,key):
        __map = {
            'minute': 'minute',
            'hour': 'hour',
            'day': 'day',
            'month': 'month',
            'day_of_week': 'day_of_week',
            '0': 'minute',
            '1': 'hour',
            '2': 'day',
            '3': 'month',
            '4': 'day_of_week',
            0: 'minute',
            1: 'hour',
            2: 'day',
            3: 'month',
            4: 'day_of_week'
            }
        if key in __map.keys():
            return getattr(self,__map[key])
        else:
            return KeyError

    def __setitem__(self,key,value):
        if key in self._CRON_MAP.items():
            setattr(self,self._CRON_MAP[key],value)

        else:
            raise ValueError("key out of bounds")

    def __eq__(self, o: object) -> bool:
        for key in ['minute','hour','day','month','day_of_week',
                    '_MINUTE','_HOUR','_DAY','_MONTH','_DAY_OF_WEEK']:
            if getattr(self,key,None) != getattr(o,key,None):
                return False

        return True