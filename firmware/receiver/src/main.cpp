#include <Arduino.h>
#include <Servo.h>
#include <SPI.h>
#include <RF24.h>
// Calibration gate: set true ONLY after single-joint bench calibration.
constexpr bool HARDWARE_CALIBRATED = false;
constexpr uint8_t N=24, FRAME=56;
constexpr uint8_t ESTOP=4, ENABLE=5, TRIG=6, ECHO=7;
const uint8_t pins[N]={28,29,30,25,26,27,22,23,24,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45};
// Must match config/robot.json. Tighten limits after mechanical inspection.
const uint8_t lo[N]={45,10,10,45,10,10,45,10,10,45,10,10,45,10,10,45,10,10,10,10,10,10,10,10};
const uint8_t hi[N]={135,170,170,135,170,170,135,170,170,135,170,170,135,170,170,135,170,170,170,170,170,170,170,170};
struct __attribute__((packed)) RadioPacket {
  uint8_t magic,version; uint16_t seq;
  int16_t x,y,yaw; uint8_t gait,flags; uint32_t uptime;
};
static_assert(sizeof(RadioPacket)==16,"Radio wire size");
RF24 radio(2,3);
const uint8_t address[6]="HX24A";
RadioPacket rc={}; Servo servos[N];
uint8_t buf[FRAME],used=0; bool attached=false,requestArm=false,latchedStop=true,seenRadio=false;
uint16_t goals[N],current[N];
uint32_t lastHost=0,lastRadio=0,lastByte=0,lastTick=0,lastReport=0,lastRange=0;
long distanceMm=-1;
uint16_t read16(const uint8_t *p){return uint16_t(p[0])|(uint16_t(p[1])<<8);}
uint16_t crc16(const uint8_t *p,uint8_t n){
  uint16_t crc=0xffff;
  while(n--){crc^=uint16_t(*p++)<<8;for(uint8_t j=0;j<8;j++) crc=(crc&0x8000)?(crc<<1)^0x1021:crc<<1;}
  return crc;
}
void detachAll(){for(uint8_t i=0;i<N;i++) if(servos[i].attached()) servos[i].detach();attached=false;}
void acceptFrame(){
  if(buf[2]!=1 || (buf[3]&~3) || crc16(buf,54)!=read16(buf+54)) return;
  // Valid stop/disarm has priority over angle validation.
  if(buf[3]&2){lastHost=millis();latchedStop=true;requestArm=false;detachAll();return;}
  if(!(buf[3]&1)){
    lastHost=millis();requestArm=false;detachAll();
    if(digitalRead(ESTOP)==LOW) latchedStop=false;
    return;
  }
  for(uint8_t i=0;i<N;i++){
    uint16_t v=read16(buf+6+2*i);
    if(v<10*lo[i] || v>10*hi[i]) return;
  }
  lastHost=millis();requestArm=true;
  for(uint8_t i=0;i<N;i++) goals[i]=read16(buf+6+2*i);
}
void readHost(){
  if(used && millis()-lastByte>30) used=0;
  while(Serial.available()){
    uint8_t b=Serial.read();lastByte=millis();
    if(used==0 && b!='H') continue;
    if(used==1 && b!='X'){used=(b=='H')?1:0;continue;}
    buf[used++]=b;
    if(used==FRAME){acceptFrame();used=0;}
  }
}
void setup(){
  Serial.begin(115200);pinMode(ESTOP,INPUT_PULLUP);pinMode(ENABLE,INPUT_PULLUP);
  pinMode(TRIG,OUTPUT);digitalWrite(TRIG,LOW);pinMode(ECHO,INPUT);
  pinMode(53,OUTPUT);
  for(uint8_t i=0;i<N;i++) current[i]=goals[i]=900;
  if(!radio.begin()){while(true){Serial.println(F("{\"type\":\"error\",\"message\":\"radio initialization failed\"}"));delay(500);}}
  radio.setChannel(90);radio.setDataRate(RF24_250KBPS);radio.setPALevel(RF24_PA_LOW);
  radio.setPayloadSize(sizeof(RadioPacket));radio.setCRCLength(RF24_CRC_16);radio.setAutoAck(true);
  radio.openReadingPipe(1,address);radio.startListening();
}
void loop(){
  readHost();uint32_t now=millis();
  while(radio.available()){
    RadioPacket p;radio.read(&p,sizeof(p));
    if(p.magic==0xA5 && p.version==1 && p.gait<3 && !(p.flags&~1) && abs(p.x)<=1000 && abs(p.y)<=1000 && abs(p.yaw)<=1000){rc=p;lastRadio=now;seenRadio=true;}
  }
  if(now-lastRange>=100){
    lastRange=now;digitalWrite(TRIG,HIGH);delayMicroseconds(10);digitalWrite(TRIG,LOW);
    unsigned long us=pulseIn(ECHO,HIGH,12000);distanceMm=us?long(us*0.1715):-1;
    now=millis();
  }
  bool stop=digitalRead(ESTOP)!=LOW;
  if(stop) latchedStop=true;
  bool radioOk=seenRadio && now-lastRadio<250;
  bool enabled=HARDWARE_CALIBRATED && !latchedStop && !stop && digitalRead(ENABLE)==LOW && radioOk && (rc.flags&1) && requestArm && now-lastHost<250 && distanceMm>=250;
  if(!enabled){if(attached)detachAll();}
  else if(!attached){
    // First pose is sent immediately: servo position cannot be measured by this
    // hardware. Mechanically support robot and pre-position it before enabling.
    for(uint8_t i=0;i<N;i++){current[i]=goals[i];servos[i].writeMicroseconds(map(current[i],0,1800,544,2400));servos[i].attach(pins[i],544,2400);}
    attached=true;lastTick=now;
  }
  if(attached && now-lastTick>=20){
    lastTick=now;
    for(uint8_t i=0;i<N;i++){
      int delta=int(goals[i])-int(current[i]);delta=constrain(delta,-12,12);current[i]+=delta;
      servos[i].writeMicroseconds(map(current[i],0,1800,544,2400));
    }
  }
  if(now-lastReport>=100){
    lastReport=now;
    Serial.print(F("{\"type\":\"status\",\"radio_ok\":"));Serial.print(radioOk?F("true"):F("false"));
    Serial.print(F(",\"deadman\":"));Serial.print((radioOk && (rc.flags&1))?F("true"):F("false"));
    Serial.print(F(",\"physical_enable\":"));Serial.print(digitalRead(ENABLE)==LOW?F("true"):F("false"));
    Serial.print(F(",\"estop\":"));Serial.print(stop?F("true"):F("false"));
    Serial.print(F(",\"output_enabled\":"));Serial.print(attached?F("true"):F("false"));
    Serial.print(F(",\"distance_mm\":"));if(distanceMm<0)Serial.print(F("null"));else Serial.print(distanceMm);
    Serial.print(F(",\"axes\":["));Serial.print(rc.x);Serial.print(',');Serial.print(rc.y);Serial.print(',');Serial.print(rc.yaw);
    Serial.print(F("],\"gait\":"));Serial.print(rc.gait);Serial.print(F(",\"radio_seq\":"));Serial.print(rc.seq);Serial.println('}');
  }
}
