import logging

from hirs_admin.models import Setting
from distutils.util import strtobool

from .data_structures import CronJob

GROUP_CONFIG = 'cron'
CONFIG_CAT = 'configuration'
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
        PATH = GROUP_CONFIG + Setting.FIELD_SEP + '%s' + Setting.FIELD_SEPadd + '%s'

        hidden = False
        
        if type(value) == list and value[0] in [True,False]:
            hidden=value[0]
            value = value[1]
        elif type(value) == list and value[1] in [True,False]:
            hidden=value[1]
            value = value[0]

        obj,new = Setting.o2.get_or_create(setting=PATH % (catagory,item))
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

def get_jobs(keep_disabled=False) -> dict:
    jobs = Setting.o2.get_by_path(GROUP_JOBS)
    output = {}

    for job in jobs:
        if job.item not in ITEM_JOBS:
            logger.warning(f"Got invalid config item {job.item_text} for job {job.catagory_text}")
        elif job not in output.keys():
            output[job] = {job.item:job.value}
        else:
            output[job][job.item] = job.value

    for job in output:
        logger.debug(f"Job Config {job} - {jobs[job]}")        
        if output[job].keys != list(ITEM_JOBS):
            logger.error(f"job {job} is missing required paramaters. Exluding job")
            output.pop(job)
        else:
            output[job][ITEM_SCHEDULE] = CronJob(output[job][ITEM_SCHEDULE])
            output[job][ITEM_STATE] = strtobool(output[job][ITEM_STATE])
        if not output[job][ITEM_STATE] and not keep_disabled:
            logger.debug(f"job {job} is disabled")
            output.pop(job)

    return output

def get_job(job_name:str, create=False) -> dict:
    jobs = Setting.o2.get_by_path(GROUP_JOBS,job_name)
    output = {}

    for job in jobs:
        if job.item not in ITEM_JOBS:
            logger.warning(f"Got invalid config item {job.item_text} for job {job.catagory_text}")
        else:
            output[job.item] = [job.value,job]

    logger.debug(f"Job Config {job_name} - {output}")        
    if output.keys != list(ITEM_JOBS):
        logger.error(f"job {job_name} is missing required paramaters. Exluding job")
        return {}
    else:
        output[ITEM_SCHEDULE][0] = CronJob(output[job][ITEM_SCHEDULE][0])
        output[ITEM_STATE][0] = strtobool(output[ITEM_STATE][0])

    return output

def get_config(catagory:str ,item:str) -> str:
    if not catagory in CATAGORY_SETTINGS:
        return ValueError(f"Invalid Catagory requested valid options are: {CATAGORY_SETTINGS}")

    q = Setting.o2.get_by_path(GROUP_CONFIG,catagory,item)
    if item in CONFIG_DEFAULTS[GROUP_CONFIG] and len(q) == 0:
        configuration_fixures()
        q = Setting.o2.get_by_path(GROUP_CONFIG,catagory,item)
        if len(q) == 0:
            logger.fatal("Failed to install fixture data")
            raise SystemError(f"Installation of fixture data failed.")
    elif len(q) == 0:
        logger.error(f"Setting {GROUP_CONFIG}/{catagory}/{item} was requested but does not exist")
        raise ValueError(f"Unable to find requested item {item}")

    return q[0].value

def set_job(name, path, schedule, args, state):
    query_path = GROUP_JOBS + Setting.FIELD_SEP + name + Setting.FIELD_SEP + '%s'

    def save(setting,value):
        o,_ = Setting.o2.get_or_create(setting=setting)
        if o.value != value:
            o.value = value
            o.save()
            return True
        else:
            return False

    save(query_path % ITEM_SCHEDULE, str(schedule))
    save(query_path % ITEM_PATH, path)
    save(query_path % ITEM_ARGS, args)
    save(query_path % ITEM_STATE, f"{state}")