#!/usr/bin/env python

from popolarenetwork import jsonrpc
import logging
import time
import datetime
from autoradio.gest_palimpsest import gest_palimpsest
from threading import *

SCHEDULE_MINUTES=3
SCHEDULE_HALF_MINUTES=SCHEDULE_MINUTES/2
SCHEDULE_SECONDS=SCHEDULE_MINUTES*60
SCHEDULE_SHIFT_SECONDS=SCHEDULE_SECONDS/3


def rpc_onair(client,status):
    # call a remote-procedure over serial transport
    result = client.onair(status=status)
    logging.info(f"jsonrpc onair {status}; result: {result}")
    

class Rpc(Timer):
    def __init__(self, interval, client, status):
        Timer.__init__(self, interval, self.onair, client, status)
    
    def onair(client,status):
        rpc_onair(client,status)

        
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

    rpc_onair(client,False)

    # this is the first and last time that I set now with the current time
    scheduletimedelta=datetime.timedelta(minutes=SCHEDULE_MINUTES)
    shiftscheduletimedelta=datetime.timedelta(seconds=SCHEDULE_SHIFT_SECONDS)
    datetimeelab=datetime.datetime.now()+shiftscheduletimedelta
    rpcs=[]
    
    try:
        while (True):
            #select the programs
            logging.info(f"datetimeelab: {datetimeelab}")
            pro=gest_palimpsest(datetimeelab,SCHEDULE_HALF_MINUTES)

            # do a list
            for program in pro.get_program():

                code=program.show.type.code
                if (code =="1a"):
                    length=program.show.length
                    if length is None:
                        logging.warning("get_palimpsest: %s legth is None; setting default to 900 sec",str(program))
                        length = 900
                    pdatetime_start=program.ar_scheduledatetime
                    title=str(program)
                    pdatetime_end=program.ar_scheduledatetime+datetime.timedelta(seconds=length)
                    type=program.show.type.type
                    subtype=program.show.type.subtype
                    production=program.show.production
                    note=program.show.description

                    logging.info(f"code: {code}, type: {type}, subtype: {subtype}; title: {title}, start: {pdatetime_start}, end: {pdatetime_end}")
                    now=datetime.datetime.now()
                    status = True
                    delay=max((pdatetime_start-now).seconds,0)
                    rpc = Rpc(delay, [client,status])
                    logging.info(f"timer start {delay}")
                    rpc.start()
                    rpcs.append(rpc)

                    now=datetime.datetime.now()
                    status = False
                    delay=max((pdatetime_end-now).seconds,0)
                    rpc = Rpc(delay, [client,status])
                    logging.info(f"timer stop  {delay}")
                    rpcs.append(rpc)

            f = open(timestampfile, "w")
            f.write(str(datetime.datetime.now()))
            f.close()

            for rpc in rpcs:
                if (not rpc.is_alive()):
                    logging.info("remove obsolete rpc")
                    rpc.remove(rpc)
            logging.info (f"waiting RPC: {rpcs}")
            
            now=datetime.datetime.now()
            datetimeelab=datetimeelab+scheduletimedelta
            delay=(datetimeelab-shiftscheduletimedelta)-now
            logging.info(f"delay for {delay}")
            time.sleep(delay.seconds)
    
    except KeyboardInterrupt:
    #except:
        logging.info("terminate process")
        try:
            for rpc in rpcs:
                rpc.cancel()
        except:
            pass

        rpc_onair(client,False)


if __name__ == "__main__":
    main()
    
