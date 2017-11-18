from utils import run_raw_command


class GethController:
    def __init__(self, ipc_path, scripts_path):
        self.ipc_addr = ipc_path
        self.scripts_path = scripts_path

    def __run_geth_js_script(self, text_line):
        return run_raw_command(
            "geth --exec {script} attach ipc:{ipc_adr}"
            .format(script=text_line, ipc_adr=self.ipc_addr))

    def get_current_block(self):
        return self.__run_geth_js_script("eth.blockNumber")

    def stop_miner(self):
        return self.__run_geth_js_script("miner.stop()")

    def start_miner(self, threads_num=1):
        return self.__run_geth_js_script("miner.start({})".format(threads_num))

    def run_script(self, script_name):
        command_result = run_raw_command(
            "geth --jspath {} --exec loadScript(\"{}\") attach ipc:{}"
            .format(self.scripts_path, script_name, self.ipc_addr)
        )
        if command_result.split("\n")[-1] == "true":
            return "\n".join(command_result.split()[:-1])
        else:
            raise GethControllerException(
                "Got error on script ({}) running ({})"
                .format(script_name, command_result))


class GethControllerException(Exception):
    pass
