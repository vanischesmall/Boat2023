#include <Arduino.h>
#include <Servo.h>

#define mega Serial

Servo MotorZR, MotorZL, MotorPR, MotorPL;

int spmega[4];
byte boolgun = 0, boolbomb = 0;
unsigned long timer = millis();
String MEga;



void uartmega() {
  
    char c = mega.read();

    if (c == '$') {
        spmega[0] = MEga.substring(0, 3).toInt()- 200;
        spmega[1] = MEga.substring(3, 6).toInt()- 200;
        spmega[2] = MEga.substring(6, 9).toInt()- 200;
        spmega[3] = MEga.substring(9, 12).toInt()- 200;

        boolgun  = MEga.substring(12, 13).toInt();
        boolbomb = MEga.substring(13, 14).toInt();

        for (int i = 0; i < 4; ++i) mega.print(String(spmega[i]) + "  ");
        mega.println(String(boolgun) + String(boolbomb));


        MEga = "";
    }
    else MEga += c;


    timer = millis();
}

void move() {
    MotorZR.writeMicroseconds(map(spmega[0], -100, 100, -500, 500) + 1490);
    MotorZL.writeMicroseconds(map(spmega[1], -100, 100, -500, 500) + 1490);
    MotorPR.writeMicroseconds(map(spmega[2], -100, 100, -500, 500) + 1490);
    MotorPL.writeMicroseconds(map(spmega[3], -100, 100, -500, 500) + 1490);
}

void setup() {
    mega.begin(9600);
    //speedreadbyte
    MotorZR.attach(8,   1000, 2000); //right
    MotorZL.attach(10,  1000, 2000); //left

    //rul
    MotorPR.attach(9,  1000, 2000); //right
    MotorPL.attach(11, 1000, 2000); //left
    pinMode(13, 1);

    delay(10000);
    timer = millis();
}

void loop() {
   if (mega.available() > 0) uartmega();
   else if (timer + 5000 < millis()) for(auto &i : spmega) i = 0;



   move();

    // if (mega.available() > 0) {
    //     char c = mega.read();

    //     if (c == '$') mega.println();
    //     else mega.print(c);

    // }


}