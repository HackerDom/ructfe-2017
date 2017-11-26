from utils import run_raw_command
from json import loads


class GethController:
    def __init__(self, ipc_path, scripts_path):
        self.__ipc_addr = ipc_path
        self.__scripts_path = scripts_path

    def __run_geth_js_script(self, text_line):
        return run_raw_command(
            "geth --exec {script} attach ipc:{ipc_adr}"
            .format(script=text_line, ipc_adr=self.__ipc_addr))

    def get_current_block(self):
        return self.__run_geth_js_script("eth.blockNumber")

    def stop_miner(self):
        return self.__run_geth_js_script("miner.stop()")

    def start_miner(self, threads_num=1):
        return self.__run_geth_js_script("miner.start({})".format(threads_num))

    def create_account(self, password):
        return self.__run_geth_js_script(
            "personal.newAccount(\"{}\")".format(password))

    def unlock_account(self, account_id, password):
        return self.__run_geth_js_script(
            "personal.unlockAccount(\"{}\", \"{}\")"
            .format(account_id, password)
        )

    def get_accounts(self):
        return loads(self.__run_geth_js_script("personal.listAccounts"))

    def run_script(self, script_name):
        command_result = run_raw_command(
            "geth --jspath {} --exec loadScript(\"{}\") attach ipc:{}"
            .format(self.__scripts_path, script_name, self.__ipc_addr)
        )
        if command_result.split("\n")[-1] == "true":
            return "\n".join(command_result.split()[:-1])
        else:
            raise GethControllerException(
                "Got error on script ({}) running ({})"
                .format(script_name, command_result))


class GethControllerException(Exception):
    pass
