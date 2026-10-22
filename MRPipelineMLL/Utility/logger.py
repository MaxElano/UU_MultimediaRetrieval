import sys
import os
sys.path.insert(0, os.getcwd() + "\\MRPipelineMLL") # location of src 

from enum import Enum
import datetime
import Utility.utility as util

'''
    We will use the logger instead of normal print() statements, in order to have control about the location it is printing to. 
    We can for example print to a file instead of the terminal
'''
class LogMode(Enum):
    PRINT = 0
    HOLD = 1
    WRITE = 2
    
class Logger:
    mode = LogMode.PRINT
    holding_logs = []
    log_name = "Log1"
    
    def __init__(self, mode = LogMode.PRINT):
        logs = util.get_all_files("Logs")
        if len(logs) > 0:
            self.log_name = "Log" + str(int(logs[-1].split("Log")[-1]) + 1)
        util.create_folder("Logs")
        util.empty_file(f"Logs\\{self.log_name}")
        self.mode = mode
    
    def set_to_print(self):
        self.mode = LogMode.PRINT
    
    def set_to_hold(self):
        self.mode = LogMode.HOLD
    
    def set_to_write(self):
        self.mode = LogMode.WRITE
        self.write("\n ==== STARTING NEW WRITING SESSION ==== \n")
    
    def log(self, text: str):
        now = datetime.datetime.now()
        f = now.strftime("%Y-%m-%d %H:%M:%S")
        new_text = f + '   ' + text
        match (self.mode):
            case LogMode.PRINT:
                self.print(new_text)
            case LogMode.HOLD:
                self.holding_logs.append(new_text)
            case LogMode.WRITE:
                self.write(new_text)
    
    def print(self, text: str):    
        print(text)
    
    def write(self, text: str):
        with open(f"Logs\\{self.log_name}", "a") as file:
            file.write(text + '\n')
    
    def custom_print(self, text: str):
        now = datetime.datetime.now()
        f = now.strftime("%Y-%m-%d %H:%M:%S")
        new_text = f + '   ' + text
        print(new_text)
    
    def dump_log(self, print = False, write = False):
        for i in range(len(self.holding_logs)):
            if (print):
                self.custom_print(self.holding_logs[i])
            if (write):
                self.write(self.holding_logs[i])
                    
    
    