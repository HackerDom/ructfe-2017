from utils import run_raw_command
from json import loads


class GethController:
    def __init__(self, ipc_path):
        self.__ipc_addr = ipc_path

    def __run_geth_js_script(self, text_line):
        return run_raw_command(
            "geth --exec {script} attach ipc:{ipc_adr}"
            .format(script=text_line, ipc_adr=self.__ipc_addr))

    def get_current_block(self):
        return self.__run_geth_js_script("eth.blockNumber")

    def get_current_miner_hashrate(self):
        return int(self.__run_geth_js_script("miner.getHashrate()"))

    def add_peer(self, enode):
        return self.__run_geth_js_script("admin.addPeer(\"{}\")".format(enode))

    def stop_miner(self):
        return self.__run_geth_js_script("miner.stop()")

    def start_miner(self, threads_num=1):
        return self.__run_geth_js_script("miner.start({})".format(threads_num))

    def create_account(self, password):
        return self.__run_geth_js_script(
            "personal.newAccount(\"{}\")".format(password))

    def get_accounts(self):
        return loads(self.__run_geth_js_script("personal.listAccounts"))


class GethControllerException(Exception):
    pass
