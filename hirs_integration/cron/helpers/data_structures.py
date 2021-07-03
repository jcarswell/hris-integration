class CronJob:
    """A Dict like object that is setup spcifically to handle
    the schdule for a cron job. CronJob take one argument of
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

    @staticmethod    
    def _to_list(val:str,default:list) -> list:
        if val == "*":
            return default

        elif len(val.split('/')) == 2:
            mply = val.split('/')[1]
            ret = []
            for x in default:
                if x % mply == 0:
                    ret.append(x)
            return ret

        elif len(val.split(',')) > 1:
            return len.split(',')
        
        else:
            return [int(val)]

    def __str__(self) -> str:
        return f"{self._MINUTE} {self._HOUR} {self._DAY} {self._MONTH} {self._DAY_OF_WEEK}"

    def __getitem__(self,key):
        if key in self._CRON_MAP.keys():
            return getattr(self,self._CRON_MAP[key])
        try:
            return getattr(self,key)
        except AttributeError:
            return KeyError
    
    def __setitem__(self,key,value):
        key_map = {
            'minute': '_MINUTE',
            'hour': '_HOUR',
            'day': '_DAY',
            'month': '_MONTH',
            'day_of_week': '_DAY_OF_WEEK',
            '0': '_MINUTE',
            '1': '_HOUR',
            '2': '_DAY',
            '3': '_MONTH',
            '4': '_DAY_OF_WEEK'
        }
        if key in key_map.items():
            setattr(self,key_map[key],value)
        
        else:
            setattr(self,key,value)