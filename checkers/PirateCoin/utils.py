from subprocess import Popen, PIPE
from urllib.request import Request
from user_agents import get_useragent


def run_raw_command(command_text):
    popen_handler = Popen(
        command_text.split(), stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output, err = popen_handler.communicate(b'')
    return_code = popen_handler.returncode
    if return_code == 0:
        return output.decode().strip()
    raise CommandRunningException(err.decode())

def create_request_object(team_addr):
    return Request(team_addr, headers={
        'User-Agent': get_useragent(),
        # 'Content-type': 'application/json'
    })

class CommandRunningException(Exception):
    pass
