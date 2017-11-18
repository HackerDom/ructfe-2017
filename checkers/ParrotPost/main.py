from geth_api.commands import GethController
from solc_compiler.compiler import SolidityCompiler


PATH_TO_GETH_IPC = "/Users/ximik/ether_test_net/ructfe/geth.ipc"
JS_SCRIPTS_PATH = "geth_scripts"
controller = GethController(PATH_TO_GETH_IPC, JS_SCRIPTS_PATH)


print(controller.get_current_block())  # via cli
print(controller.run_script("get_current_block.js"))  # via external javascript file


compiler = SolidityCompiler("contracts_src/")
print(compiler.compile("voters.col")) #
