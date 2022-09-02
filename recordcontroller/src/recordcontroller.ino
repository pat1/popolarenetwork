#define INTERRUPTEVENT CHANGE
#define DEBOUNCINGTIME 100
#define MIN_COMMUTATION_TIME 3000
//#define MAX_COMMUTATION_TIME 500
#define RECORDPIN 2

unsigned long antirimb=0;
long fallingtime=0;
long risingtime=0;
uint8_t oldstatus = 0;


/*
void record()
{
  //uint8_t status = digitalRead(RECORDPIN);
  //unsigned long now=millis();
  
  //if ((now-antirimb) < DEBOUNCINGTIME && status != oldstatus) return;
  
  //oldstatus=status;
  //antirimb=now;
  
  if (digitalRead(RECORDPIN)==LOW){
    //fallingtime=now;
    status=LOW;
    strcpy(command,"stop");
  }  else {
    //risingtime=now;
    status=HIGH;
    strcpy(command,"start");
  }
  
  //if (abs(risingtime-fallingtime) > MIN_COMMUTATION_TIME){
  //Serial.print("{\"m\":\"record\",\"p\":[{\"command\": \"");
  //Serial.print(command);
  //Serial.println("\"}]}");
  //}
  //} 
}
*/

void setup() {

  Serial.begin(115200);        // connect to the serial port
  Serial.print(F("Start firmware version: "));
  Serial.print(F("interrupt...init"));
  pinMode(RECORDPIN,INPUT_PULLUP);  // connected to rain sensor switch
  //attachInterrupt(digitalPinToInterrupt(RECORDPIN), record, INTERRUPTEVENT);
  Serial.println(F("end setup"));
}

void loop() {

  char command[30];
  unsigned long now=millis();
  uint8_t status = digitalRead(RECORDPIN);  
  if (status == oldstatus) return;
  if ((now-antirimb) < DEBOUNCINGTIME) return;
  antirimb=now;
  if (status==LOW){
    strcpy(command,"start");
  }  else {
    strcpy(command,"stop");
  }
  
  Serial.print("{\"m\":\"record\",\"p\":[{\"command\": \"");
  Serial.print(command);
  Serial.println("\"}]}");
  oldstatus = status;
    
}



