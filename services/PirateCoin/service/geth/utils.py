from subprocess import Popen, PIPE


def run_raw_command(command_text):
    popen_handler = Popen(
        command_text.split(), stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output, err = popen_handler.communicate(b'')
    return_code = popen_handler.returncode
    if return_code == 0:
        return output.decode().strip()
    raise CommandRunningException(err.decode())


class CommandRunningException(Exception):
    pass
