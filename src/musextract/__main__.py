'''
Created on 29.04.2017

@author: wglas
'''

import sys
from clazzes.tools.logtools import configureStderr

def main(args=None):
    """The main routine."""
    if args is None:
        args = sys.argv[1:]

    debugModules = None

    for da in ["-d","--debug"]:
        if da in args:
            args.remove(da)
            debugModules = ["musextract"]
    
    configureStderr(debugNames=debugModules)
    
    from musextract.cmdline import run_musextract
    
    run_musextract(args)

if __name__ == "__main__":
    main()

