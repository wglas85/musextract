'''
Created on 29.04.2017

@author: wglas
'''

import logging
import getopt
import sys
from musextract.extract import parse_mscz

log = logging.getLogger(__name__)

def usage(argv0):
    
    print("Usage: %s [options...] <input> [<voice1> [<voice2> [...]]]"%argv0,file=sys.stderr)
    print("  Supported options are:",file=sys.stderr)
    print("    -h Print this help.",file=sys.stderr)


def run_musextract(argv):
    
    try:
        opts, args = getopt.getopt(argv,"h", ["help"])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err,file=sys.stderr)  # will print something like "option -a not recognized"
        usage(sys.argv[0])
        sys.exit(64)
        
    for o, a in opts:  # @UnusedVariable
        if o in ("--help"):
            usage(sys.argv[0])
            sys.exit(0)
#        elif o in ("-u", "--url"):
#            url = urlparse(a)
        else:
            assert False, "unhandled option"

    if len(args) < 1:
        print("No input file given",file=sys.stderr)
        usage(sys.argv[0])
        sys.exit(64)
            
    filename = args[0]
    
    voices = set(args[1:])

    parse_mscz(filename,voices,sys.stdout)
    