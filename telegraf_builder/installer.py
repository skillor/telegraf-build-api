import os
import subprocess


def git_clone(git_url: str, git_branch: str, output_dir: str):
    result = subprocess.run(['git', 'clone', '--depth', '1', '--branch', git_branch, git_url, output_dir],
                            shell=True,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL)
    if result.returncode != 0:
        raise Exception('Git clone failed')


def install(git_url: str, git_branch: str, telegraf_dir: str):
    if not os.path.exists(telegraf_dir):
        print('cloning git ' + git_url)
        git_clone(git_url, git_branch, telegraf_dir)


def get_git_info(telegraf_dir: str):
    process = subprocess.Popen(['git', 'rev-parse', 'HEAD'],
                               cwd=telegraf_dir,
                               shell=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    head = process.stdout.read().decode().strip()
    process = subprocess.Popen(['git', 'config', '--get', 'remote.origin.url'],
                               cwd=telegraf_dir,
                               shell=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    remote_url = process.stdout.read().decode().strip()
    return {'head': head, 'remote': remote_url}
