#!/usr/bin/env python

import jsonrpc as jsonrpc
import threading
try:
    import queue
except:
    import Queue as queue
import gi
gi.require_version('Gst', '1.0')
#gi.require_version('GstPbutils', '1.0')
gi.require_version('GLib', '2.0')
gi.require_version('GObject', '2.0')
from gi.repository import GLib, GObject, Gst
#import ctypes
import os,sys
from datetime import datetime, timedelta
import signal
import os,signal,time

ROOTPATH="/home/audio_condivisi/info/Radio Popolare/notiziari"
PREFIX="notiziario_"
POSTFIX=".oga"
MAXLEN=30  # minutes max of recorded notiziario

q = queue.Queue()

def purge(dir_to_search,prefix,postfix):
    #dir_to_search = os.path.curdir
    for dirpath, dirnames, filenames in os.walk(dir_to_search):
        for myfile in filenames:
            print("check file",myfile," with ",prefix, " and ",postfix)
            # checking the file match
            if (myfile.startswith(prefix) and myfile.endswith(postfix)):
                    curpath = os.path.join(dirpath, myfile)
                    file_modified = datetime.fromtimestamp(os.path.getmtime(curpath))
                    print("modified:",file_modified)
                    if (datetime.now() - file_modified) > timedelta(hours=12):
                        print("remove file:", curpath)
                        os.remove(curpath)


def round_time(dt, resolution):
    """
    round_time(datetime, resolution (sec)) => datetime rounded to nearest interval
    """

    starttime=dt.replace(year=dt.year-1,month=1,day=1,hour=0,minute=0,second=0, microsecond=0)
    seconds=(dt-starttime).total_seconds()
    roundedseconds=seconds+resolution/2 - ((seconds+resolution/2) % (resolution))
    return starttime + timedelta(seconds=roundedseconds)

# define some procedures and register them (so they can be called via RPC)
def record(s):
    print ("execute record command: ",s["command"])
    q.put(s["command"])
    return "{\"r\":\"ok\"}"

def ping():
    global _lastping 
    _lastping = datetime.now()
    print ("excute ping command",_lastping)
    purge(ROOTPATH,PREFIX,POSTFIX)
    return "{\"r\":\"ok\"}"

class jsrpc_thread(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name

        # create a JSON-RPC-server

        self.server = jsonrpc.Server(jsonrpc.JsonRpc20(radio=True), jsonrpc.TransportTcpIp(addr=("127.0.0.1", 31415), logfunc=jsonrpc.log_file("rpc.log")))
        #self.server = jsonrpc.Server(jsonrpc.JsonRpc20(radio=True), jsonrpc.TransportSERIAL(port="/dev/ttyACM0",baudrate=115200,timeout=60, logfunc=jsonrpc.log_stdout))

        self.server.register_function( record, name="record")
        self.server.register_function( ping, name="ping")
        global _lastping
        _lastping = datetime.now()
        print("start: ",_lastping)


    
    def run(self):
        try:

            while ((datetime.now() - _lastping) < timedelta(seconds = 60)):
                # start server
                self.server.serve(1)  # wait for one rpc
                #self.server.serve()   # for ever!
                print((datetime.now() - _lastping), timedelta(seconds = 60))

            print ('Ping timeout!')
        
        finally:
            print ('ended')
            raise
            try:
                signal.signal.raise_signal(signal.SIGINT)
            except:
                os.kill(os.getpid(), signal.SIGUSR1)


#    def get_id(self):
#        
#        # returns id of the respective thread
#        if hasattr(self, '_thread_id'):
#            return self._thread_id
#        for id, thread in threading._active.items():
#            if thread is self:
#                return id
#            
#    def raise_exception(self):
#        thread_id = self.get_id()
#        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
#                                                         ctypes.py_object(SystemExit))
#        if res > 1:
#            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
#            print('Exception raise failure')

def bus_call(bus, message, loop):
    t = message.type
    #Gst.debug_bin_to_dot_file_with_ts(pipeline, Gst.DebugGraphDetails.ALL, "test")
    if t == Gst.MessageType.EOS:
        sys.stdout.write("End-of-stream\n")
        loop.quit()
    elif t == Gst.MessageType.ERROR:
        err, debug = message.parse_error()
        sys.stderr.write("Error: %s: %s\n" % (err, debug))
        loop.quit()
    return True

def execute_command(loop, pipeline):
    _, position = pipeline.query_position(Gst.Format.TIME)
    #print("Position: %s\r" % Gst.TIME_ARGS(position))
    try:
        command = q.get_nowait()
    except queue.Empty:
        command = None
        pass

    if (not command is None):
        print ("command",command)
    
    if command == "start":
        print("Starting")
        
        canonicaldatetime=round_time(datetime.now(), 900)
        URL=ROOTPATH + "/" + PREFIX + canonicaldatetime.strftime('%H-%M') + POSTFIX
        print(URL,filesink)
        #pipeline.remove(filesink)
        filesink.set_property("location",URL)        
        #pipeline.add( filesink)
        #oggmux.link( filesink)
        pipeline.set_state(Gst.State.PLAYING)
            
    if position > MAXLEN*60 * Gst.SECOND or command == "stop":
        #loop.quit()
        print("Stopping")
        pipeline.set_state(Gst.State.NULL)

    return True

def get_microphone():
    monitor = Gst.DeviceMonitor.new()
    monitor.add_filter("Audio/Source", None)
    monitor.start()

    # This is happening synchonously, use the GstBus based API and
    # monitor.start() to avoid blocking the main thread.
    devices = monitor.get_devices()

    if not devices:
        print("No microphone found...")
        sys.exit(1)

    default = [d for d in devices if d.get_properties().get_value("is-default") is True]
    if len(default) == 1:
        device = default[0]
    else:
        print("Avalaible microphones:")
        for i, d in enumerate(devices):
            print("%d - %s" % (i, d.get_display_name()))
        res = int(input("Select device: "))
        device = devices[res]
    
    source = device.create_element()
    return source

def main():

    global filesink
    
    #GObject.threads_init()
    Gst.init(None)
    
    pipeline = Gst.Pipeline()
    #source=get_microphone()
    source = Gst.ElementFactory.make("autoaudiosrc", "autoaudiosrc")
    audioconvert = Gst.ElementFactory.make("audioconvert", "audioconvert")
    vorbisenc = Gst.ElementFactory.make("vorbisenc", "vorbisenc")
    oggmux = Gst.ElementFactory.make("oggmux", "oggmux")
    filesink = Gst.ElementFactory.make("filesink", "filesink")
    
    pipeline.add( source)
    pipeline.add( audioconvert)
    pipeline.add( vorbisenc)
    pipeline.add( oggmux)
    pipeline.add( filesink)
    
    source.link( audioconvert)
    audioconvert.link( vorbisenc)
    vorbisenc.link( oggmux)
    oggmux.link( filesink)

    pipeline.set_state(Gst.State.NULL)
    pipeline.get_state(Gst.CLOCK_TIME_NONE)
        
    bus = pipeline.get_bus()
    bus.add_signal_watch()
    
    loop = GLib.MainLoop()
    GLib.timeout_add(100, execute_command, loop, pipeline)
    bus.connect ("message", bus_call, loop)

    #thread = threading.Thread(target=jsrpc_thread)
    thread = jsrpc_thread('Record')
    thread.daemon = True
    thread.start()

    try:
        loop.run()
    except KeyboardInterrupt:
        print("terminate process")
        pipeline.get_state(Gst.CLOCK_TIME_NONE)
        loop.quit()
        #thread.raise_exception()
        #thread.join()

if __name__ == "__main__":
    main()
    
