from functools import singledispatch
import time
import logging
import json
import subprocess
import signal

from multiprocessing import Process

from hirs_integration.hirs_admin.models import Setting

SCHEDULE_NAME = '_Schedule'
PATH_NAME = '_Path'
ARGS_NAME = '_Options'
STATE_NAME = '_Status'

logger = logging.getLogger(__name__)

class Runner:

    def get_jobs(self) -> dict:
        jobs = {}
        for setting in Setting.objects.filter(setting='Cron/Jobs/*'):
            path = setting.setting.split('/')[3]
            job = "".join(path.split("_")[:-1])
            if not hasattr(jobs, job):
                jobs[job] = {"status":False,"ags":""}
                
            if path[-(len(SCHEDULE_NAME)):] == SCHEDULE_NAME:
                jobs[job]["time"] = setting.value
            elif path[-(len(PATH_NAME)):] == PATH_NAME:
                jobs[job]["path"] = setting.value
            elif path[-(len(ARGS_NAME)):] == ARGS_NAME:
                jobs[job]["args"] = setting.value
            elif path[-(len(STATE_NAME)):] == STATE_NAME:
                jobs[job]["status"] = bool(setting.value)
            else:
                logger.warn(f"Got unexpected config {''.Join(path.split('_')[-1])} for job {job}")
        
        for job in jobs:
            logger.debug(f"Job Config {job} - {json.dumps(jobs[job])}")
            if jobs[job].keys not in ['path','time']:
                logger.error(f"job {job} is missing required paramaters. Exluding job")
                jobs.pop(job)
            if not jobs[job]["status"]:
                logger.debug(f"job {job} is disabled")
                jobs.pop(job)
        
        self._jobs = jobs

    def __init__(self):
        self.get_jobs()
        if self.jobs == {}:
            logger.warning("There are currently no jobs configured")
        
        if hasattr(self,'runners'):
            logger.warning("It seams that we're already running")
            return
        
        signal.signal(signal.SIGTERM, self.stop)
        signal.signal(signal.SIGBREAK, self.stop)
        self.running = True
        self.runners = {}
        self._run = Process(target=self.run).start()
        self._qm = Process(target=self.queue_manager).start()

    def __del__(self):
        self.stop()
        self._run.terminate()
        self._qm.terminate()

    def stop(self, gracefull:bool =True):
        self.running = False
        if not gracefull:
            for runner in self.runners:
                if runner.is_alive():
                    runner.terminate()
        else:
            while len(self.runners) > 0:
                time.sleep(1)
            
        self.runners = None

    def queue_manager(self):
        while isinstance(self.runners,dict):
            for job in self.runners:
                if not job.is_alive:
                    job.join()

                self.runners.pop(job)

    def run(self):
        self.runners = {}
        while self.running:
            if time.localtime().tm_sec <= 10:
                for job,config in self._jobs.items():
                    if self.check_job(config[time]) and job not in self.queue.keys():
                        self.exec(job,config)
                    else:
                        pjob = getattr(self.runners,job,None)
                        try:
                            if not pjob.is_alive:
                                self.exec(job,config)
                        except AttributeError:
                            pass

                if time.localtime().tm_min == 0:
                    self.get_jobs()

            time.sleep(10)

        # Ensure that the Queue is empty

    def exec(self, job:str, config:str):
        logger.info(f"Running job {job}")
        proc = Process(target=self.exec_job, args=(config,))
        self.runners[job] = proc
        proc.start()

    def exec_job(self,job:dict):
        if not isinstance(job,dict):
            logger.critical("Received invalid gob spec.")
            raise ValueError("job is not valid", job)
        
        try:
            proc = subprocess.run([job['path'],job['args'].split(' ')],capture_output=True)
            logger.debug(f"Job Complete: {proc.stdout}")
        except subprocess.CalledProcessError as e:
            logger.critical(f"Exception occured durring processing of job:")
            logger.critical(f"\tcommand: {e.cmd}")
            logger.critical(f"\tReturn: {e.returncode} - {e.stderr}")
            logger.critical(str(e))

    def check_job(self,schedule:str) -> bool:
        time_slots = ['tm_minute','tm_hour','tm_mday','tm_mon','tm_wday']
        cron = schedule.split(' ')
        ltime = time.localtime()
        go = True
        
        if ltime.tm_sec <= 0 and schedule == "* * * * *":
            return True
        
        for x in range(len(cron)):
            slot = cron[x]
            if len(slot) >= 3:
                if getattr(ltime,time_slots[x]) % int(cron[x].split('/')[1]) == 0:
                    go = True
                else:
                    go = False
            elif (cron[x] == '*'
                   or getattr(ltime,time_slots[x]) == int(cron[x])):
                go = True
            else:
                go = False

            if not go:
                break

        return go


if __name__ == "__main__":
    Runner()