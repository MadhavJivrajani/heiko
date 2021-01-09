import subprocess
import os
from heiko.config import Node

def sync_folder(node: Node):
    pwd = os.getcwd()
    if node.password:
        subprocess.run(["sshpass", "-p", node.password, 
                "rsync", "-a", "-v", "-e", f"ssh -p {node.port}","--exclude-from=rsync-ignore",
                pwd, f"{node.username}@{node.host}:~/.heiko/"])
    else:
        subprocess.run(["rsync", "-a", "-v", "--exclude-from=rsync-ignore",
                pwd, f"{node.username}@{node.host}:~/.heiko/"])

