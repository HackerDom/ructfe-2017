from utils import run_raw_command


class SolidityCompiler:
    def __init__(self, src_dir):
        self.__contracts_src_dir = src_dir

    def compile(self, contract_name) -> dict:
        return {
            "bytecode": self.__get_compilation(contract_name),
            "json_abi":  self.__get_compilation(contract_name, "abi")
        }

    def __get_compilation(self, contract_name, comp_type="bin"):
        bytecode = run_raw_command("solc --{} {}".format(
            comp_type,
            self.__contracts_src_dir + contract_name))
        return bytecode.split("\n")[-1]
