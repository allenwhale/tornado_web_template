import inspect
import sys


def log(msg, *args, sep=' ', end='\n', file=sys.stdout, flush=False):
    (frame, filename, line_number, function_name, lines, index) =\
            inspect.getouterframes(inspect.currentframe())[1]
    print("[%s,%s,%s]"%(filename, line_number, function_name))
    print(msg, *args, sep=sep, end=end, file=file, flush=flush)
