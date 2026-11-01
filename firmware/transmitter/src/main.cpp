#include <Arduino.h>
#include <SPI.h>
#include <RF24.h>
struct __attribute__((packed)) RadioPacket {
  uint8_t magic,version;uint16_t seq;int16_t x,y,yaw;uint8_t gait,flags;uint32_t uptime;
};
static_assert(sizeof(RadioPacket)==16,"Radio wire size");
RF24 radio(9,10);const uint8_t address[6]="HX24A";
uint16_t seq=0;uint32_t lastSend=0,lastReport=0,sent=0,acked=0;
int16_t axis(uint8_t pin){int v=analogRead(pin)-512;if(abs(v)<55)return 0;return constrain(v*1000L/511,-1000,1000);}
void setup(){
  Serial.begin(115200);pinMode(4,INPUT_PULLUP);pinMode(5,INPUT_PULLUP);pinMode(6,INPUT_PULLUP);
  if(!radio.begin()){Serial.println(F("Radio initialization failed"));while(true){}}
  radio.setChannel(90);radio.setDataRate(RF24_250KBPS);radio.setPALevel(RF24_PA_LOW);
  radio.setPayloadSize(sizeof(RadioPacket));radio.setCRCLength(RF24_CRC_16);
  radio.setAutoAck(true);radio.setRetries(3,5);radio.openWritingPipe(address);radio.stopListening();
}
void loop(){
  uint32_t now=millis();
  if(now-lastSend>=20){
    lastSend=now;
    uint8_t gait=digitalRead(5)==LOW?1:(digitalRead(6)==LOW?2:0);
    RadioPacket p={0xA5,1,seq++,axis(A0),axis(A1),axis(A2),gait,uint8_t(digitalRead(4)==LOW),now};
    sent++;if(radio.write(&p,sizeof(p)))acked++;
  }
  if(now-lastReport>=1000){
    lastReport=now;Serial.print(F("{\"sent\":"));Serial.print(sent);Serial.print(F(",\"acked\":"));Serial.print(acked);Serial.println('}');
  }
}
