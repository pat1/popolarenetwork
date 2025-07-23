#!/usr/bin/env python

from popolarenetwork import jsonrpc
import logging
import time

        
def main(timestampfile="record.timestamp",jsonrpcfile=None):

    logging.info("start")
    
# create JSON-RPC client

    if (jsonrpcfile is None):
        logfunc=jsonrpc.log_dummy
    else:
        logfunc=jsonrpc.log_file(jsonrpcfile)
    
    client = jsonrpc.ServerProxy(jsonrpc.JsonRpc20(radio=False,notification=False),
                             jsonrpc.TransportSERIAL( logfunc=logfunc,
                                                      port='/dev/popolare_onair',baudrate=115200,timeout=5))

    try:
        # call a remote-procedure (with positional parameters)
        while (True):
            result = client.onair(status=True)
            print (result)
            time.sleep(3)
            result = client.onair(status=False)
            print (result)
            time.sleep(3)
    
    #except KeyboardInterrupt:
    except:
        logging.info("terminate process")

if __name__ == "__main__":
    main()
    
