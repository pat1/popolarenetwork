#!/usr/bin/env python

from popolarenetwork import jsonrpc
import logging
import time
import datetime
from autoradio.gest_palimpsest import gest_palimpsest
from threading import *


def rpc_onair(client,clientlock,status):
    # call a remote-procedure over serial transport
    logging.info(f"jsonrpc onair {status}")
    with clientlock:
        result = client.onair(status=status)

    logging.info(f"jsonrpc onair result: {result}")

class Rpc(Timer):
    def __init__(self, interval, client,clientlock, status):
        Timer.__init__(self, interval, self.onair, [client, clientlock, status])
    
    def onair(self, client, clientlock, status):
        rpc_onair(client, clientlock, status)
        
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
    clientlock=Lock()
    
    rpc_onair(client, clientlock, False)
    
    rpcs=[]
    first=True
    
    try:
        while (True):

            if (first):
                # il primo run elabora 20 minuti nel passato e 20 nel futuro
                SCHEDULE_MINUTES=40
                SCHEDULE_SECONDS=SCHEDULE_MINUTES*60
                SCHEDULE_SHIFT_SECONDS=0
                SCHEDULE_TOLLERANCE_START_SECONDS=300
                SCHEDULE_TOLLERANCE_STOP_SECONDS=900
                # this is the first and last time that I set now with the current time
                scheduletimedelta=datetime.timedelta(minutes=SCHEDULE_MINUTES)
                scheduleshifttimedelta=datetime.timedelta(seconds=SCHEDULE_SHIFT_SECONDS)
                datetimeelab=datetime.datetime.now()+scheduleshifttimedelta

            else:
                
                # il run successivi elaborano da 20 minuti nel futuro a 2h e venti nel futuro
                SCHEDULE_MINUTES=120
                SCHEDULE_SECONDS=SCHEDULE_MINUTES*60
                SCHEDULE_SHIFT_SECONDS=SCHEDULE_SECONDS/3*2
                SCHEDULE_TOLLERANCE_START_SECONDS=300
                SCHEDULE_TOLLERANCE_STOP_SECONDS=900
                # this is the first and last time that I set now with the current time
                scheduletimedelta=datetime.timedelta(minutes=SCHEDULE_MINUTES)
                scheduleshifttimedelta=datetime.timedelta(seconds=SCHEDULE_SHIFT_SECONDS)
                datetimeelab=datetime.datetime.now()+scheduleshifttimedelta
            
            #select the programs
            logging.info(f"datetimeelab: {datetimeelab}")
            # get programs in intervall datetimeelab +/- (SCHEDULE_MINUTES/2)
            pro=gest_palimpsest(datetimeelab,SCHEDULE_MINUTES/2)

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
                    delay=max(((pdatetime_start-datetime.timedelta(seconds=SCHEDULE_TOLLERANCE_START_SECONDS))-now).total_seconds(),0)
                    rpc = Rpc(delay, client, clientlock, status)
                    logging.info(f"timer start {delay}")
                    rpc.start()
                    rpcs.append(rpc)

                    now=datetime.datetime.now()
                    status = False
                    # 15 secondi dopo per assicurasi che tutti gli start siano già stati eseguiti
                    delay=max(((pdatetime_end+datetime.timedelta(seconds=SCHEDULE_TOLLERANCE_STOP_SECONDS))-now).total_seconds(),15)
                    rpc = Rpc(delay, client, clientlock, status)
                    logging.info(f"timer stop  {delay}")
                    rpc.start()
                    rpcs.append(rpc)

            f = open(timestampfile, "w")
            f.write(str(datetime.datetime.now()))
            f.close()

            for rpc in rpcs:
                if (not rpc.is_alive()):
                    logging.info(f"remove obsolete RPC: {rpc}")
                    rpcs.remove(rpc)
            logging.info (f"alive RPCS: {rpcs}")

            now=datetime.datetime.now()
            datetimeelab=datetimeelab+scheduletimedelta

            if (not first):
                delay=(datetimeelab-scheduleshifttimedelta)-now
                logging.info(f"delay for {delay}")
                time.sleep(delay.total_seconds())
            else:
                first=False
                
    #except KeyboardInterrupt:
    except:
        logging.info("terminate process")
        for rpc in rpcs:
            try:
                rpc.cancel()
            except:
                pass

        rpc_onair(client, clientlock, False)


if __name__ == "__main__":
    main()
    
