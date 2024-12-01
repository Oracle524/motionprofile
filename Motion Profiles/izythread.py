# |IzyThread: First Edition|---------------------------------------------------
#
# Project: IzyThread
# Program: izythread.py
#
# Description:
#   This class is designed for the execution of a periodic task. This module is
# not designed for high accuracy or frequencies as it is limited by the 
# performance of datetime module. The timeleft variable can be averaged to show
# if there is a timed delay required between function calls. This version
# expects the period in microseconds.
#
# Input Arguments:
#   func    - The method to execute.
#   period  - The period between function calls in milliseconds.
#   test - Flag to print out
#
# Initialization:
#   et = TimedThread(func, period, test)
#   et.setDaemon(True)
#
# Start:
#   if not et.is_alive():
#       et = TimedThread(func, period)
#       et.setDaemon(True)
#       et.start()
# Stop:
#   if et.is_alive():
#       et.stop.set()
#       et.join()
#
# Original Author: Isaiah Regacho
#
# Version:
# 16/03/21: Created
# 18/06/21: Resolution increased to microseconds
# -----------------------------------------------------------------------------

# |MODULES|--------------------------------------------------------------------
import datetime
import threading

class TimedThread(threading.Thread):
    def __init__(self, name, func, period, test, strict=True):
        threading.Thread.__init__(self)
        self.stop = threading.Event()
        self.func = func
        self.period = period
        self.setDaemon(True)
        self.test = test
        self.name = name
        self.strict = strict

    def run(self):
        print("Starting Timed Thread:{}...".format(self.name))
        end = datetime.datetime.now()
        timeleft = 0
        avg = 0
        count = 0
        period = datetime.timedelta(microseconds=self.period)
        while not self.stop.wait(timeleft):
            count += 1
            end += period
            self.func()
            if self.strict:
                timeleft = (end - datetime.datetime.now()).total_seconds()
            else:
                timeleft = period.total_seconds()
            avg += timeleft

        if self.test:
            print("Average Excess Thread Time: {}".format(avg/count))

        print("...Ending Timed Thread:{}".format(self.name))

class TimedThreadExample():
    def __init__(self, count):
        print("This example will end in:")
        self.i = count

    def examplefunc(self):
        # print(self.i)
        self.i -= 1

if __name__ == "__main__":
    
    # Start Example
    example = TimedThreadExample(100)
    example2 = TimedThreadExample(100)
    period = 10000
    period2 = 100000

    # Initialize and Start Thread
    et = TimedThread("Example One", example.examplefunc, period, True)
    et2 = TimedThread("Example Two", example2.examplefunc, period2, True)
    et.start()

    # Pause Program Until Count Finishes
    while example2.i >= 0:
        if example.i < 5 and not et2.is_alive():
            et2.start()
        pass

    # Raise Stop and Join Thread
    et2.stop.set()
    et2.join()
    et.stop.set()
    et.join()
    
    print("Success!!!")
