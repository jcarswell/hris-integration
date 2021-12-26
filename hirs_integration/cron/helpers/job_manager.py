from types import MethodType
from importlib import import_module
import logging

from .data_structures import CronJob
from . import config
from cron.exceptions import AlreadyExists,ModuleOrMethodInvalid

logger = logging.getLogger("cron.job_manager")

class Job:
    """Cron Job Manager defines the ability to add, update and delete jobs."""
    
    def __init__(self, name:str, path:str =None,schedule:str =None, args:str =None, state:bool =False, **kwargs):
        self.name = self._clean(name)
        self.job_config = config.get_job(self.name)

        if self.job_config:
            self.path = path or self.job_config[config.ITEM_PATH][0]
            schedule = CronJob(schedule,**kwargs)
            if schedule == CronJob():
                self.schedule = self.job_config[config.ITEM_SCHEDULE][0]
            self.args = args or self.job_config[config.ITEM_ARGS][0]
            self.state = state or self.job_config[config.ITEM_STATE]
        else:
            self.path = path
            self.schedule = CronJob(schedule,**kwargs)
            self.args = args
            self.state = state

        self.kwargs = kwargs

        if path:
            self.module = self.__import_path()

    def update_schedule(self, schedule,**kwargs):
        """Create a new schedule for a job"""
        self.schedule = CronJob(schedule,**kwargs)

    @staticmethod
    def _clean(name:str) -> str:
        return "_".join(name.split()).lower()
    
    def delete(self):
        """Delete a job"""
        if self.job_config != {}:
            for k,v in self.job_config.items():
                logger.debug(f"Deleting {k} for job {self.name}")
                v[1].delete()
                self.job_config[k].pop(1)
    
    def new(self, path:str =None,schedule:str =None, args:str =None, state:bool =False, **kwargs):
        """Create a new Cron Job Entry

        Args:
            path (str)[optional]: the path to call for the job if not already set during init
            schedule (str)[optional]: the cron schedule to use if not already set during init
            args (str)[optional]: any arguments requred for the path
            state (bool)[optional]: Job Status

        Raises:
            AlreadyExists: If this job already exists don't use this method
        """
        
        if len(self.job_config) != 0:
            raise AlreadyExists(f"{self.name} is already a job please use the save method")

        self.path = path or self.path
        self.schedule = CronJob(schedule,**kwargs)
        if schedule == CronJob() and schedule != self.schedule:
            self.schedule = schedule
        self.args = args or self.args
        self.state = state or self.state
        
        self.module = self.__import_path()
        
        logger.debug(f"Creating Job {str(self)}")
        
        self.save()
    
    def __str__(self) -> str:
        return f"{self.name}: {self.schedule} {self.path}({self.args})"

    def __eq__(self, o: object) -> bool:
        """Checks to see if the configured values are the same regardless of the name"""
        for key in ['path','schedule','args','state']:
            if getattr(self,key) != getattr(o,key):
                return False
        
        return True

    def __import_path(self) -> MethodType:
        """Import the defined path and return the requested function

        Raises:
            ValueError: If path is not set
            ModuleOrMethodInvalid: If the imported module doesn't have the request function
            ModuleNotFoundError: If the Module doesn't exist

        Returns:
            Method or Function: Requested import
        """
        
        if self.path == None:
            raise ValueError("Path may not be empty")
        else:
            m = import_module('.'.join(self.path.split('.')[0:-1]))
            if not hasattr(m,self.path.split('.')[-1]):
                raise ModuleOrMethodInvalid(f"Module does not have a method {self.path.split('.')[-1]}")

        return getattr(m,self.path.split('.')[-1])

    def save(self):
        config.set_job(self.name,self.path,self.schedule,self.args,self.state)


def get_jobs(keep_disabled=False):
    jobs = config.get_jobs(keep_disabled)
    output = []
    for job in jobs:
        output.append(Job(job))

    return output