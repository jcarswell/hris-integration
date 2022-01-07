import time
import logging
import signal

from multiprocessing import Process

from .helpers import job_manager,config

logger = logging.getLogger('cron.manager')

class Runner:

    def get_jobs(self) -> dict:
        self._jobs = job_manager.get_jobs()

    def __init__(self):
        if not config.Config()(config.CONFIG_CAT,config.CONFIG_ENABLED):
            logger.info("Cron is currently disabled")
            return

        self.get_jobs()

        if self._jobs == {}:
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
            for job,instance in self.runners.items():
                if not instance.is_alive:
                    logger.debug(f"QM: {job} is dead joining to close")
                    instance.join()
                    logger.info(f"QM: {job} completes")
                    self.runners.pop(job)

    def run(self):
        self.runners = {}
        last_min = time.localtime().tm_min-1
        while self.running:
            if time.localtime().tm_min != last_min:
                last_min = time.localtime().tm_min
                for job in self._jobs:
                    if self.check_job(job.sechedule) and job.name not in self.queue.keys():
                        self.exec(job)
                    else:
                        pjob = getattr(self.runners,job.name,None)
                        try:
                            if not pjob.is_alive:
                                self.exec(job)
                        except AttributeError:
                            pass

                if time.localtime().tm_min == 0:
                    self.get_jobs()

            time.sleep(10)

    def exec(self, job:job_manager.Job):
        logger.info(f"Running job {job.name}")
        self.runners[job.name] = Process(target=job.module, args=job.args)
        self.runners[job.name].start()

    def check_job(self,schedule) -> bool:
        time_slots = ['tm_minute','tm_hour','tm_mday','tm_mon','tm_wday']
        ltime = time.localtime()
        
        for x in range(5):
            if getattr(ltime,time_slots[x]) not in schedule[x]:
                return False

        return True


if __name__ == "__main__":
    Runner()