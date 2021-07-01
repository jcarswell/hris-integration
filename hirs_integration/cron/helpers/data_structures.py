class CronJob:
    """A Dict like object that is setup spcifically to handle
    the schdule for a cron job. CronJob take one argument of
    a string that's a valid cron schedule. From the minute,
    hour, day, month and day_of_week variable are populated
    with a list of valid matching times. Theses variable can
    also be accessed by postion instead of name.   

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
        0: minute,
        1: hour,
        2: day,
        3: month,
        4: day_of_week
    }

    def __init__(self,cron_schedule:str, **kwargs) -> None:
        sched = cron_schedule.split()
        if len(sched) != 5:
            raise ValueError(f"Expected 5 segments got {len(sched)}")
        self._MINUTE = sched[0]
        self._HOUR = sched[1]
        self._DAY = sched[2]
        self._MONTH = sched[3]
        self._DAY_OF_WEEK = sched[4]

        for k,v in kwargs:
            setattr(self,k,v)

        self.minute = self._to_list(self._MINUTE,list(range(60)))
        self.hour = self._to_list(self._HOUR,list(range(24)))
        self.day = self._to_list(self._DAY,list(range(1,32)))
        self.month = self._to_list(self._MONTH,list(range(1,13)))
        self.day_of_week = self._to_list(self._DAY_OF_WEEK,list(range(7)))

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
        if key in ['0','1','2','3','4']:
            return self._CRON_MAP[int(key)]

        try:
            return getattr(self,key)
        except AttributeError:
            return KeyError