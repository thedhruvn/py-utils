import threading
import ast
import inspect
from typing import Callable
import warnings
import textwrap

class StoppableLoopingThread(threading.Thread):
    """
        Extension of the Thread Object that performs a task repetitively
        at a given frequency until the thread is stopped

        ## TODO: handle Thread.join()

        Note:  will return an error if the target function has a while loop in the source code
    """
    def __init__(self,delay=0.005,max_loops=None, *args, **kwargs):
        #self.args1 = args
        #self.kwargs1 = kwargs
        #self.delay = delay
        #self.group = None
        threading.Thread.__init__(self, *args, **kwargs)
        # super().__init__(self)
        self._stop_event = threading.Event()
        self.delay = delay
        self.max_loops = max_loops

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def run(self):
        """
            Main Function - taken from the Thread class
                - checks to see if the target function has a while loop (note: this isn't really working...)
                - Runs the target function over and over again, checking to see if a stop function has been called for the thread
                - The target function is run with a given delay (currently set to 0.005 seconds)
                - Can be extended to run the target function a certain number of times
                - Alternatively, can remove all of this and write a custom run() function for each motor motion that we desire (i.e., recoater blade, main lift, etc.)
                - We can use the same structure where the stop() function can force this thread to stop running. Otherwise, #thread.join() will always wait for the run() to finish before stoppping the thread.

        """
        try:
            if self._target:
                if self.uses_while(self._target):
                    raise RuntimeError("Target function has a while loop")
                if self.max_loops is not None:
                    for i in range(0,self.max_loops):
                        if not self._stop_event.wait(timeout=self.delay):
                            self._target(*self._args, **self._kwargs)
                        else:
                            break
                else:
                    while not self._stop_event.wait(timeout=self.delay):
                        self._target(*self._args, **self._kwargs)
            else:
                warnings.warn("Target not specified...")
        finally:
            # Avoid a refcycle if the thread is running a function with
            # an argument that has a member that points to the thread.
            del self._target, self._args, self._kwargs

    def uses_while(self, fn: Callable) -> bool:
        try:
            nodes = ast.walk(ast.parse(textwrap.dedent(inspect.getsource(fn))))
            return any(isinstance(node, ast.While) for node in nodes)
        #except IndentationError as e:
        #    return False
        except Exception as e:
            warnings.warn(f"Alert: {type(e)} occurred when checking the target: {e}. Continuing onwards...")
            return False
