# create JSON-RPC client
import jsonrpc as jsonrpc
import time

server = jsonrpc.ServerProxy(jsonrpc.JsonRpc20(radio=True,notification=True), jsonrpc.TransportTcpIp(addr=("127.0.0.1", 31415)))

# call a remote-procedure
print("send start")
result = server.record({"command":"start"})
time.sleep(5)

print("send stop")
result = server.record({"command":"stop"})

print ("end")
