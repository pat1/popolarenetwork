/*
 Toggle the status of a LED by sending a
 json message to the arduino over the serial connection.
 
 The following python script can be used to toggle the LED
 after the sketch has been uploaded to the arduino:
 
 import sys
 import serial
 import time
 
 port = '/dev/ttyACM0'
 ser = serial.Serial(port, 115200)
 
 # give the serial connection 2 seconds to settle
 time.sleep(2)
 
 ser.write('{"jsonrpc":"2.0","method":"onair","params":{"status":true},"id":0}')
 time.sleep(5)
 ser.write('{"jsonrpc":"2.0","method":"onair","params":{"status":false},"id":0}')
 
 # wait 2 seconds before closing the serial connection
 time.sleep(2)
 ser.close()


use those for radio mode:

 ser.write('{"m":"onair","p": {"status": true},"i":0}')
 time.sleep(5)
 ser.write('{"m": "onair", "p": {"status": false},"i":0}')


 */

// include the arduinoJsonRPC library
#include <arduinoJsonRPC.h>

// initialize an instance of the JsonRPC library for registering 
// exactly 1 local method
//radio mode is false; do not use compact protocoll
JsonRPC rpc(false);

// on most arduino boards, pin 13 is connected to a LED
int outpin = 2;

void setup()
{
  // initialize the digital pin as an output
  pinMode(outpin, OUTPUT);
  
  // start up the serial interface
  Serial.begin(115200);
  Serial.println("#Started");

  // set timeout for stream read in parse json
  //Serial.setTimeout(3000);
  
  // and register the local onair method
  rpc.registerMethod("onair", &onair);
}


int onair(JsonObject params, JsonObject result)
{
  if (params.containsKey("status")){
    boolean requestedStatus = params["status"];
    
    if (requestedStatus)
      {
	//Serial.println("#switch on PIN");
	digitalWrite(outpin, HIGH);
      }
    else
      {
	//Serial.println("#switch off PIN");
	digitalWrite(outpin, LOW);
      }
    result["state"]="done";
    return 0;
    
  }else{
    return 1;
  }
}


void loop()
{
  bool is_active=true;
  while (is_active){
    rpc.parseStream(&is_active,&Serial);
  }
}
