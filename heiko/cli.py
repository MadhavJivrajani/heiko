import os
import sys
import argparse
from pathlib import Path
import glob
import asyncio


from heiko.daemon import Daemon
from heiko.main import main
from heiko.load_utils import HeikoGetNodeDetails
from heiko.config import *

class HeikoDaemon(Daemon):
    def run(self):
        main()

# Parse CLI args
def make_parser():
    """Creates an ArgumentParser, configures and returns it.

    This was made into a separate function to be used with sphinx-argparse

    :rtype: :py:class:`argparse.ArgumentParser`
    """
    parser_ = argparse.ArgumentParser(prog='heiko')
    subparsers = parser_.add_subparsers(dest='command')

    parser_run = subparsers.add_parser('start', help='Starts heiko daemon')
    parser_run.add_argument('--name', help='a unique name for the daemon', required=True)

    parser_stop = subparsers.add_parser('stop', help='Stops heiko daemon')
    parser_stop.add_argument('--name', help='a unique name for the daemon', required=True)

    parser_restart = subparsers.add_parser('restart', help='Restarts heiko daemon')
    parser_restart.add_argument('--name', help='a unique name for the daemon', required=True)

    parser_list = subparsers.add_parser('list', help='lists all running heiko daemons')

    parser_init = subparsers.add_parser('init', help='initialize and benchmark all nodes')

    return parser_

parser = make_parser()

def cli():
    """Entrypoint to the command-line interface (CLI) of heiko.

    It parses arguments from sys.argv and performs the appropriate actions.
    """
    args = parser.parse_args()

    # Get config directory
    heiko_home = Path.home() / '.config' / 'heiko'
    os.makedirs(heiko_home, exist_ok=True)

    # list running daemons
    if args.command == 'list':
        pid_files = glob.glob(str(heiko_home / '*.pid'))
        # store PIDs
        pids = []
        for pid_file in pid_files:
            with open(pid_file, "r") as f:
                pids.append(f.read())
        # get names
        names = [pid_file.split('/')[-1].split('_', 1)[-1].split('.')[0] for pid_file in pid_files]
        print('Currently running daemons:')
        print('name\tPID')
        for name, pid in zip(names, pids):
            print(f'{name}\t{pid}')

    elif args.command == 'init':
        
        c = Config(CONFIG_LOCATION)
        
        for node in c.nodes:
            # Initialization and Benchmarking
            utils = HeikoGetNodeDetails(node=node)
            asyncio.get_event_loop().run_until_complete(utils.getDetails())
            print("Printing node details")
            print("CPU:\n", utils.details['cpu'].stdout) #, "\ntype = ", type(utils.details['cpu']))
            print("\nRAM:\n", utils.details['ram'].stdout)
            print("\nCPU Usage:\n", utils.details['usage'].stdout)
    else:
        if 'name' not in args:
            parser.print_usage()
            sys.exit(1)

        # Manage daemon
        daemon = HeikoDaemon(heiko_home / f'heiko_{args.name}.pid',
                            stdout=heiko_home / f'heiko_{args.name}.out',
                            stderr=heiko_home / f'heiko_{args.name}.out')


        if args.command == 'start':
            daemon.start()
        elif args.command == 'stop':
            daemon.stop()
        elif args.command == 'restart':
            daemon.restart()
