import sched
import time
import threading
import schedule

class Scheduler():

    def __init__(self) -> None:
        pass

    def funcEveryday(self, func):
        schedule.every(1).days.do(func)
    
    def funcEveryminute(self, func):
        schedule.every(1).minutes.do(func)

    def funcEverysecond(self, func):
        schedule.every(1).seconds.do(func)

    def funcEverytime(self, func, time):
        schedule.every().day.at(time).do(func)