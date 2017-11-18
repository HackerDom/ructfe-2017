from geth_api.api import run_raw_command


class GethController:
    def __init__(self, ipc_path):
        self.ipc_addr = ipc_path

    def __run_geth_js_script(self, text_line):
        return run_raw_command(
            "geth --exec {script} attach ipc:{ipc_adr}"
            .format(script=text_line, ipc_adr=self.ipc_addr))

    def get_current_block(self):
        return self.__run_geth_js_script("eth.blockNumber")

    def stop_miner(self):
        return self.__run_geth_js_script("miner.stop()")

    def start_miner(self):
        return self.__run_geth_js_script("miner.start()")