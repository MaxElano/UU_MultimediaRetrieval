from enum import Enum
import datetime

'''
    We will use the logger instead of normal print() statements, in order to have control about the location it is printing to. 
    We can for example print to a file instead of the terminal
'''
class log_mode(Enum):
    PRINT = 0
    HOLD = 1
    WRITE = 2
    
class logger:
    mode = log_mode.PRINT
    holding_logs = []
    
    def __init__(self, mode = log_mode.PRINT):
        self.mode = mode
    
    def set_to_print(self):
        self.mode = log_mode.PRINT
    
    def set_to_hold(self):
        self.mode = log_mode.HOLD
    
    def set_to_write(self):
        self.mode = log_mode.WRITE
    
    def log(self, text: str):
        now = datetime.datetime.now()
        f = now.strftime("%Y-%m-%d %H:%M:%S")
        new_text = f + '   ' + text
        match (self.mode):
            case log_mode.PRINT:
                self.print(new_text)
            case log_mode.HOLD:
                self.holding_logs.append(new_text)
            case log_mode.WRITE:
                self.write(new_text)
    
    def print(self, text: str):    
        print(text)
    
    def write(self, text: str):
        pass
    
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
                    
    
    