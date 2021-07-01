import logging

from hirs_integration.hirs_admin.models import Setting

from .data_structures import CronJob

GROUP_CONFIG = 'cron'
CONFIG_CAT = 'cponfiguration'
CATAGORY_SETTINGS = (CONFIG_CAT,)
GROUP_JOBS =  'cron_jobs'
ITEM_SCHEDULE = 'schedule'
ITEM_PATH = 'path'
ITEM_ARGS = 'options'
ITEM_STATE = 'status'
ITEM_JOBS = (ITEM_ARGS,ITEM_PATH,ITEM_SCHEDULE,ITEM_STATE)


CONFIG_DEFAULTS = {
    CONFIG_CAT: {
        'enabled': True
    }
}

logger = logging.getLogger('cron.config_helper')

def configuration_fixures():
    def add_fixture(catagory,item,value):
        PATH = GROUP_CONFIG + Setting.PATH_SEP + '%s' + Setting.PATH_SEP + '%s'

        hidden = False
        
        if type(value) == list and value[0] in [True,False]:
            hidden=value[0]
            value = value[1]
        elif type(value) == list and value[1] in [True,False]:
            hidden=value[1]
            value = value[0]

        obj,new = Setting.objects.get_or_create(setting=PATH % (catagory,item))
        if new:
            obj.setting = PATH % (catagory,item)
            obj.hidden = hidden
            obj.value = value
            obj.save()
        
        return new

    for key,val in CONFIG_DEFAULTS.items():
        if type(val) == dict:
            for item,data in val.items():
                add_fixture(key,item,data)

def get_jobs(keep_disabled=False) -> list:
    jobs = Setting.objects.get_by_path(GROUP_JOBS)
    output = {}
    for job in jobs:
        if job.item in ITEM_JOBS:
            logger.warning(f"Got invalid config item {job.item_text} for job {job.catagory_text}")
        elif job not in output.keys():
            output[job] = {job.item:job.value}
        else:
            output[job][job.item] = job.value

    for job in output:
        logger.debug(f"Job Config {job} - {jobs[job]}")        
        if output[job].keys not in [ITEM_PATH,ITEM_SCHEDULE]:
            logger.error(f"job {job} is missing required paramaters. Exluding job")
            output.pop(job)
        else:
            output[job][ITEM_SCHEDULE] = CronJob(output[job][ITEM_SCHEDULE])
        if not output[job][ITEM_STATE] and not keep_disabled:
            logger.debug(f"job {job} is disabled")
            output.pop(job)

    return list(output.values())

def get_config(catagory:str ,item:str) -> str:
    if not catagory in CATAGORY_SETTINGS:
        return ValueError(f"Invalid Catagory requested valid options are: {CATAGORY_SETTINGS}")
    
    try:
        q = Setting.objects.get_by_path(GROUP_CONFIG,catagory,item)
    except Setting.DoesNotExist:
        if item in CONFIG_DEFAULTS[GROUP_CONFIG]:
            configuration_fixures()
            try:
                q = Setting.objects.get_by_path(GROUP_CONFIG,catagory,item)
            except Setting.DoesNotExist:
                logger.fatal("Failed to install fixture data")
                raise SystemError(f"Installation of fixture data failed.")
        else:
            logger.error(f"Setting {GROUP_CONFIG}/{catagory}/{item} was requested but does not exist")
            raise ValueError(f"Unable to find requested item {item}")
    
    return q.value