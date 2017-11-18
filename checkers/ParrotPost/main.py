from geth_api.commands import GethController


PATH_TO_GETH_IPC = "/Users/ximik/ether_test_net/ructfe/geth.ipc"
controller = GethController(PATH_TO_GETH_IPC)

controller.start_miner()
print(controller.get_current_block())
controller.stop_miner()
