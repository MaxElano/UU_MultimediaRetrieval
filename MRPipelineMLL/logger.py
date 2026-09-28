'''
    We will use the logger instead of normal print() statements, in order to have control about the location it is printing to. 
    We can for example print to a file instead of the terminal
'''

class logger:
    def __init__(self):
        pass
    
    def log(self, text: str):
        print(text)