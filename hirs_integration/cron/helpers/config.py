# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

import logging

from typing import Any
from hirs_admin.models import Setting
from common.functions import ConfigurationManagerBase,FieldConversion
from warnings import warn

from .data_structures import CronJob
from .settings_fields import *

ITEM_SCHEDULE = 'schedule'
ITEM_PATH = 'path'
ITEM_ARGS = 'options'
ITEM_STATE = 'status'
ITEM_JOBS = (ITEM_ARGS,ITEM_PATH,ITEM_SCHEDULE,ITEM_STATE)

logger = logging.getLogger('cron.config_helper')


def get_jobs(keep_disabled:bool =False) -> dict:
    jobs = Setting.o2.get_by_path(GROUP_JOBS)
    output = {}
    job_list = {}

    for job in jobs:
        field = FieldConversion(job.field_properties.get("type","CharField"))
        
        if job.item not in ITEM_JOBS:
            logger.warning(f"Got invalid config item {job.item_text} for job {job.category_text}")    
        elif job.category not in job_list.keys():
            job_list[job.category] = {job.item:field(job.value)}
        else:
            job_list[job.category][job.item] = field(job.value)
        
        if job.item == ITEM_SCHEDULE:
            job_list[job.category][job.item] = CronJob(field.value)

    for job in job_list.keys():
        if (keep_disabled and not job_list[job][ITEM_STATE]) or job_list[job][ITEM_STATE]:
            logger.debug(f"Job Config {job} - {job_list[job]}")
            output[job] = job_list[job]
        else:
            logger.debug(f"Job {job} is disabled")

    return output

def get_job(job_name:str) -> dict:
    jobs = Setting.o2.get_by_path(GROUP_JOBS,job_name)
    output = {}

    for job in jobs:
        if job.item not in ITEM_JOBS:
            logger.warning(f"Got invalid config item {job.item_text} for job {job.category_text}")
        else:
            output[job.item] = [FieldConversion(job.field_properties.get("type","CharField"))(job.value),job]

    logger.debug(f"Job Config {job_name} - {output}")        
    if output.keys != list(ITEM_JOBS):
        logger.error(f"job {job_name} is missing required paramaters. Excluding job")
        return {}
    else:
        output[ITEM_SCHEDULE][0] = CronJob(output[job][ITEM_SCHEDULE][0])

    return output

class Config(ConfigurationManagerBase):
    root_group = GROUP_CONFIG
    category_list = CATEGORY_SETTINGS
    fixtures = CONFIG_DEFAULTS


def get_config(category:str ,item:str) -> Any:
    """Now deprecated use Config instead to manage the value"""
    warn("get_config is deprecated use Config instead to manage the value", DeprecationWarning)
    return Config()(category,item)

def set_job(name, path, schedule, args, state):
    query_path = GROUP_JOBS + Setting.FIELD_SEP + name + Setting.FIELD_SEP + '%s'
    field_properties_schedule = {
        "type": "CharField",
        "validators": ["validators.cron_validator"],
        "required": True,
    }
    field_properties_path = {
        "type": "CharField",
        "help": "Path to executable or module to excute",
        "required": True,
    }
    field_properties_args = {
        "type": "CharField",
        "help": "Flags or arguments to pass to the executable",
    }
    field_properties_state = {
        "type": "BooleanField",
    }

    def save(setting,value,fp):
        item,new = Setting.o2.get_or_create(setting=setting)
        if new:
            for k,v in fp.items():
                item.field_properties[k] = v            
        if item.value != value:
            item.value = value
            item.save()
            return True
        else:
            return False

    save(query_path % ITEM_SCHEDULE, str(schedule), field_properties_schedule)
    save(query_path % ITEM_PATH, path, field_properties_path)
    save(query_path % ITEM_ARGS, args, field_properties_args)
    save(query_path % ITEM_STATE, str(state), field_properties_state)