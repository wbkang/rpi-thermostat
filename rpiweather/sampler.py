import time
import logging
import threading

logger = logging.getLogger(__name__)


class Sampler:
    def __init__(self, sample_interval, sampler, receiver):
        "Sampler(sample_interval, sampler, receiver)"
        self.sample_interval = sample_interval
        self.sampler = sampler
        self.receiver = receiver
        self.thread = None

    def start(self):
        if self.thread is None:
            self.thread = threading.Thread(target=self._run, args=(self,))
            self.thread.daemon = True
            self.thread.start()

    def _run(self, *args):
        def pipe_stuff():
            self.receiver(self.sampler())
        repeat_job(self.sample_interval, pipe_stuff)


def repeat_job(period, fun):
    "repeat_job(period=seconds, fun=function)"
    start_time = time.monotonic()
    while True:
        fun()
        sleep_until = start_time + period
        sleep_time = sleep_until - time.monotonic()
        if sleep_time > 0:
            time.sleep(sleep_time)
        else:
            logger.warn("fun took too long! we are behind %.2fs" % sleep_time)
        start_time = sleep_until
