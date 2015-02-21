import logging
import types
from multiprocessing import Process
import sys
import time
from utilities.multiprocessing.dispatcher import Dispatcher
from utilities.logger import LoggerTool

# Credit for solution came from Roger Stuckey's example


try:
   import cPickle as pickle
except:
   import pickle

__author__ = 'jmeline'

tool = LoggerTool()
logger = tool.setupLogger(__name__, __name__ + '.log', 'w', logging.DEBUG)



class TaskServerMP:
    """
    The TaskServerMP class provides a target worker class method for queued processes.
    """

    def __init__(self, numproc=1, engine=None):
        """
        Initialise the TaskServerMP and create the dispatcher and processes.
        """
        self.numprocesses = numproc
        self.tasks = []

        self.engine = engine

        # Create the dispatcher
        self.dispatcher = Dispatcher()

        self.Processes = []

        # begin processes before entering app.MainLoop()
        # attempting to start them before will crash wxPython. Don't do it
        for n in range(numproc):
            process = Process(target=TaskServerMP.worker, args=(self.dispatcher, self.engine))
            process.start()
            self.Processes.append(process)

    def setEngine(self, engine):
        self.engine = engine

    def setTasks(self, taskList):
        """
        Sets the tasks for the TaskServerMP to handle.
        """
        #logger.debug("tasklist: %s" % taskList)
        self.tasks.extend(taskList)
        self.numtasks = len(taskList)


    def worker(cls, dispatcher, engine):
        """
        The worker creates a TaskProcessor object to calculate the result.
        """

        while True:
            args = dispatcher.getTask()
            task_type = args[0]
            task_args = args[1]
            print "WORKER! ", str(task_args)

            if task_type == 'AddModels':
                eng_type = task_args['type']
                eng_attrib = task_args['attrib']
                model = engine.add_model(type=eng_type, attrib=eng_attrib)

                print "Model! ", model

                pickled = pickle.dumps(model)
                print "Picked! ", pickled, type(pickled)

                print "Loads! ", pickle.loads(pickled)

                dispatcher.putResult(pickled)



    # The multiprocessing worker must not require any existing object for execution!
    worker = classmethod(worker)


    def processTasks(self, resfunc=None):
        """
        Start the execution of tasks by the processes.
        """
        logger.debug("Entering Process Tasks")
        # put task in
        for task in self.tasks:
            self.dispatcher.putTask(task)

        # get output
        model = self.dispatcher.getResult()
        print "In ProcessTasks: ", pickle.loads(model)

    def processStop(self, resfunc=None):
        """
        Stop the execution of tasks by the processes.
        """
        self.keepgoing = False

        while (self.j < self.i):
            # Get and print any results remining in the done queue
            output = self.getOutput()
            if (isinstance(resfunc, (types.FunctionType, types.MethodType))):
                resfunc(output)

    def processTerminate(self):
        """
        Stop the execution of tasks by the processes.
        """
        for n in range(self.numprocesses):
            # Terminate any running processes
            self.Processes[n].terminate()

        # Wait for all processes to stop
        while (self.anyAlive()):
            time.sleep(0.5)

    def anyAlive(self):
        """
        Check if any processes are alive.
        """
        isalive = False
        for n in range(self.numprocesses):
            isalive = (isalive or self.Processes[n].is_alive())
        return isalive

    def getOutput(self):
        """
        Get the output from one completed task.
        """
        self.j += 1

        if (self.numprocesses == 0):
            # Use the single-process method
            self.worker_sp()

        output = self.dispatcher.getResult()
        # Calculate the time remaining
        self.timeRemaining(self.j + 1, self.numtasks, output['process']['pid'])

        return output

    def timeRemaining(self, tasknum, numtasks, pid):
        """
        Calculate the time remaining for the processes to complete N tasks.
        """
        timeNow = time.time()
        self.timeElapsed = timeNow - self.timeStart

        pid_str = '%d' % pid
        self.processTime[pid_str] = self.timeElapsed

        # Calculate the average time elapsed for all of the processes
        timeElapsedAvg = 0.0
        numprocesses = self.numprocesses
        if (numprocesses == 0): numprocesses = 1
        for pid_str in self.processTime.keys():
            timeElapsedAvg += self.processTime[pid_str] / numprocesses
        self.timeRemain = timeElapsedAvg * (float(numtasks) / float(tasknum) - 1.0)

    def update(self, output):
        """
        Get and print the results from one completed task.
        """
        # sys.stdout.write('%s [%d] calculate(%d) = %.2f' % ( output['process']['name'], output['process']['pid'], output['result'][0], output['result'][1] ))
        sys.stdout.write('  [Complete: %2d / %2d  Time Elapsed: %s  Remaining: %s]' % (
        self.j + 1, self.numtasks, time.strftime('%M:%S', time.gmtime(self.timeElapsed)),
        time.strftime('%M:%S', time.gmtime(self.timeRemain))))
        sys.stdout.write('\n')



