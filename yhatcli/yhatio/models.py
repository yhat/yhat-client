import sys
import json

from colorama import init
from colorama import Fore, Back, Style

from input_and_output import df_to_df, parse_json, preprocess

init()

class YhatModel(object):
    """
    A simple class structure for your model. Place all of the code you want to
    execute in the `execute` method.

    The `run` method provides you with a basic development "server" for testing
    locally. It will give you the same results as you will see on a Yhat server
    99% of the time.
    """

    def execution_plan(self, data):
        return self.execute(data)

    @preprocess
    def execute(self, data):
        """
        This is the execution plan for your model. It defines what routines you
        will execute and how the input and output will be handled.

        data - dict or DataFrame
            the datatype is decided by the IO Specification; (df_to_df,
            dict_to_dict, etc.). 
        """
        pass

    def run(self, testcase=None):
        """
        Runs a local 'Yhat Server' that mimics the production environment. Data
        can be passed to the server via stdin (by pasting data into the terminal
        ).
        
        If your data is too big to paste into the terminal, try setting up a 
        testcase which will run automatically. To do this, use the json module
        and run json.dumps({ YOUR DATA}) to generate acceptable input for Yhat.

        testcase - optional, JSON string
            If a testcase is included, it will automatically execute when `run`
            is called.
        """
        print "Paste your test data here"
        print "Data should be formatted as valid JSON."
        print Fore.CYAN + "Hit <ENTER> to execute your model"
        print Fore.RED + "Press <CTRL + C> or type 'quit' to exit"
        print Fore.RESET + "="*40
        if testcase:
            sys.stdout.write("[In] %s\n" % testcase)
            data = parse_json(testcase + '\n')
            sys.stdout.write("[Out]\n")
            print self.execute(data)
        while True:
            sys.stdout.write("[In] ")
            data = sys.stdin.readline()
            if data.strip()=="quit":
                sys.exit()
            data = parse_json(data)
            sys.stdout.write("[Out]\n")
            print self.execute(data)

