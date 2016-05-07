import logging
import inspect

def log(msg):
    (frame, filename, line_number, function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
    print(filename, line_number, function_name, msg)

