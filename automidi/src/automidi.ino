#include <Control_Surface.h> // Include the Control Surface library
#include <Adafruit_NeoPixel.h>

#define POLLINGTIME 10000

Adafruit_NeoPixel pixels = Adafruit_NeoPixel(1, 47, NEO_RGB + NEO_KHZ800);

// Instantiate a MIDI over USB interface.
USBMIDI_Interface midi;
bool oldstate1;

// Instantiate a CCButton object
CCButton button1 {
  // Push button on pin 10:
  10,
  // General Purpose Controller #1 on MIDI channel 1:
  {MIDI_CC::General_Purpose_Controller_1, Channel_1},
};
uint32_t polling;
bool first=true;

void setup() {
  Control_Surface.begin(); // Initialize Control Surface

  pixels.begin();            //INITIALIZE NeoPixel strip object (REQUIRED)
  pixels.clear();            // Turn OFF all pixels ASAP
  pixels.show();  
  pixels.setBrightness(255);  // Set BRIGHTNESS (max = 255)
  pixels.setPixelColor(0, 255, 0, 0);
  pixels.show();  
  delay(1000);
  pixels.setPixelColor(0, 0, 255, 0);
  pixels.show();  
  delay(1000);
  pixels.setPixelColor(0, 0, 0, 255);
  pixels.show();  
  delay(1000);

  oldstate1=button1.getButtonState();  
  if (oldstate1){
    pixels.setPixelColor(0, 0, 255, 0);
  }else{
    pixels.setPixelColor(0, 255, 255, 255);      
  }
  pixels.show();  
  polling=millis();
}
 
void loop() {

  while (not first && (millis() < (polling + POLLINGTIME))){
    Control_Surface.loop(); // Update the Control Surface
    bool state;
    state=button1.getButtonState();
    if (oldstate1 != state){
      oldstate1=state;
      if (state){
	pixels.setPixelColor(0, 0, 255, 0);
      }else{
	pixels.setPixelColor(0, 255, 255, 255);      
    }
      pixels.show();  
    }
  }
  uint8_t value;
  if(button1.getButtonState()) {
    value=0;
  }else{
    value=0x7F;
  }
  Control_Surface.sendControlChange ({MIDI_CC::General_Purpose_Controller_1, Channel_1}, value);

  first=false;
  polling=millis();
}
