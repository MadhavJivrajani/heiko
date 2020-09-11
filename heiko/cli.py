import os
import argparse
from pathlib import Path
import glob

from heiko.daemon import Daemon
from heiko.main import main

class HeikoDaemon(Daemon):
    def run(self):
        main()

# Parse CLI args
parser = argparse.ArgumentParser(prog='heiko')
subparsers = parser.add_subparsers(dest='command')

parser_run = subparsers.add_parser('start', help='Starts heiko daemon')
parser_run.add_argument('--name', help='a unique name for the daemon', required=True)

parser_stop = subparsers.add_parser('stop', help='Stops heiko daemon')
parser_stop.add_argument('--name', help='a unique name for the daemon', required=True)

parser_restart = subparsers.add_parser('restart', help='Restarts heiko daemon')
parser_restart.add_argument('--name', help='a unique name for the daemon', required=True)

parser_list = subparsers.add_parser('list', help='lists all running heiko daemons')

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

else:
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
