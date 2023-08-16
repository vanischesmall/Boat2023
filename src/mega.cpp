#include <Arduino.h>
#include <IBusBM.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Max72xxPanel.h>

#define rpi  Serial2
#define nano Serial3

const int compassAddr = 0x01;
unsigned long timer = millis();
const byte M[8] = {0b11000011, 0b11000011, 0b11000011, 0b11011011, 0b11111111, 0b11111111, 0b11100111, 0b11000011},
           A[8] = {0b01100110, 0b01100110, 0b01111110, 0b01111110, 0b01100110, 0b01100110, 0b01111110, 0b00111100},
           G[8] = {0b00011000, 0b00111100, 0b00111100, 0b00011000, 0b11000011, 0b11100111, 0b11100111, 0b11000011},
           N[8] = {0b11000011, 0b11000111, 0b11001111, 0b11011111, 0b11111011, 0b11110011, 0b11100011, 0b11000011},
           O[8] = {0b00111100, 0b01111110, 0b01100110, 0b01100110, 0b01100110, 0b01100110, 0b01111110, 0b00111100},
           B[8] = {0b00011110, 0b00111111, 0b10111111, 0b10111111, 0b10111111, 0b10011110, 0b01001100, 0b00111000};
byte       L[8] = {0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000};

IBusBM ibus;
Max72xxPanel matrix = Max72xxPanel(53, 1, 1);

int errorold = 0;
int st = 0;
int spnano[4];
int error, speed, goal, azimuth;
bool boolauto = true;
byte boolgun = 0, boolbomb = 0, boolomni = 0;



int readChannel(byte channel, int min, int max, int defvalue) {
    uint16_t ch = ibus.readChannel(channel);
    if (ch < 100) return defvalue;
    return map(ch, 1000, 2000, min, max);
}

bool key() {
    return !digitalRead(A0);
}

void loading() {
    for (int i = 0; i < 8; ++i) {
        L[i] = 0b11111111;
        for (int l = 0; l < 8; ++l) for (int j = 0; j < 8; ++j) matrix.drawPixel(j, l, L[l] & (1 << j));

        matrix.write();
        delay(1000);
    }
    delay(3000);
}

void mat() {
    matrix.fillScreen(LOW);

    if (st == 0) for (int i = 0; i < 8; ++i) for (int j = 0; j < 8; ++j) matrix.drawPixel(j, i, N[i] & (1 << j)); else
    if (st == 1) {
        for (int i = 0; i < 8; ++i) for (int j = 0; j < 8; ++j) matrix.drawPixel(j, i, M[i] & (1 << j));
        if (boolomni) for (int i = 0; i < 8; ++i) for (int j = 0; j < 8; ++j) matrix.drawPixel(j, i, O[i] & (1 << j)); else
        if (boolbomb) for (int i = 0; i < 8; ++i) for (int j = 0; j < 8; ++j) matrix.drawPixel(j, i, B[i] & (1 << j)); else
        if (boolgun ) for (int i = 0; i < 8; ++i) for (int j = 0; j < 8; ++j) matrix.drawPixel(j, i, G[i] & (1 << j));
    } else
    if (st == 2) if (!boolgun && !boolbomb) for (int i = 0; i < 8; ++i) for (int j = 0; j < 8; ++j) matrix.drawPixel(j, i, A[i] & (1 << j));

    matrix.write();
}

void debug() {
    rpi.print(st);            // boat mode
    rpi.print(azimuth + 100); // azimuth
}

void state() {
    key() ?
    st = 1 : st =    readChannel(8, 0, 2, 0);

    st != 2 ? boolauto = true : boolauto = false; // autonomous

    boolgun  = readChannel(6, 0, 1, 1);
    boolomni = readChannel(7, 0, 1, 1);
    boolbomb = readChannel(9, 0, 1, 1);

    mat();
}

void compass() {
    Wire.beginTransmission(compassAddr);
    Wire.write(0x44);
    Wire.endTransmission();

    Wire.requestFrom(compassAddr, 2);
    while (Wire.available() < 2);

    byte lowbyte = Wire.read();
    byte highbyte = Wire.read();

    azimuth = word(highbyte, lowbyte);
}

void pid() {
    speed = 100;
    if (abs(error) < 2) error = 0;

    int u = int((float)error * 1.2 + (float)(error - errorold) * 10);

    spnano[0] = -speed,
    spnano[1] =  speed,
    spnano[2] =  constrain(speed-u, -100, 100),
    spnano[3] =  constrain(speed+u, -100, 100);



    errorold = error;
}

void neutral() {
    boolauto = true;
    for (auto & i : spnano) i = 0;
    Serial.println("Neutral");
}

void manual() {
    error = readChannel(3, -100, 100, 0),
    speed = readChannel(1, -100, 100, 0);

    if (!boolomni) { // default movement
        spnano[0] = constrain(speed + error, -100, 100),
        spnano[1] = constrain(speed + error, -100, 100),
        spnano[2] = constrain(speed - error, -100, 100),
        spnano[3] = constrain(speed + error, -100, 100);

    } else { // omni movement
        int angle = 0;

        if (error == 0) for (auto &i : spnano) i = speed;
        else {
            if (speed > 0 && error > 0) angle =       atan(tan(error / speed)); else
            if (speed < 0 && error > 0) angle = 90  + atan(tan(speed / error)); else
            if (speed < 0 && error < 0) angle = 180 + atan(tan(error / speed)); else
            if (speed > 0 && error < 0) angle = 270 + atan(tan(speed / error));

            if (angle == 30  || angle == 150) spnano[0] = speed, spnano[1] = 0, spnano[2] = 0, spnano[3] = speed; else
            if (angle == 210 || angle == 330) spnano[0] = 0, spnano[1] = speed, spnano[2] = speed, spnano[3] = 0;
            else {
                if (angle > 0 && angle < 30) {  // 0
                    int speeda = (int)speed * tan((30 - angle) * PI / 180);
                    spnano[0] = speed, spnano[1] = speeda, spnano[2] = speeda, spnano[3] = speed;
                } else
                if (angle > 30 && angle < 90) { // 1
                    int errora = (int)error * tan((angle - 30) * PI / 180);
                    spnano[0] = error, spnano[1] = -errora, spnano[2] = -errora, spnano[3] = error;
                } else
                if (angle > 90 && angle < 150) { // 2
                    int errora = (int)error * tan((150 - angle) * PI / 180);
                    spnano[0] = errora, spnano[1] = -error, spnano[2] = -error, spnano[3] = errora;
                } else
                if (angle > 150 && angle < 180) { // 3
                    int speeda = (int)speed * tan((angle - 150) * PI / 180);
                    spnano[0] = -speeda, spnano[1] = -speed, spnano[2] = -speed, spnano[3] = -speeda;
                } else
                if (angle > 180 && angle < 210) { // 4
                    int speeda = (int)speed * tan((angle + 150) * PI / 180);
                    spnano[0] = -speed, spnano[1] = -speeda, spnano[2] = -speeda, spnano[3] = -speed;
                } else
                if (angle > 210 && angle < 270) { // 5
                    int errora = (int)error * tan((angle - 270) * PI / 180);
                    spnano[0] = -error, spnano[1] = errora, spnano[2] = errora, spnano[3] = -error;
                } else
                if (angle > 270 && angle < 330) { // 6
                    int errora = (int)error * tan((angle - 270) * PI / 180);
                    spnano[0] = -errora, spnano[1] = speed, spnano[2] = speed, spnano[3] = -errora;
                } else
                if (angle > 330 && angle < 360) { // 7
                    int speeda = (int)speed * tan((angle - 270) * PI / 180);
                    spnano[0] = speeda, spnano[1] = speed, spnano[2] = speed, spnano[3] = speeda;
                }
            }
        }
    }
}

void uartrpi() {
    compass();
    if (boolauto) goal = azimuth, boolbomb = false;

    if (rpi.available() > 0) {
        String strrpi = rpi.readStringUntil('$'); rpi.flush();
        byte   strpi  = strrpi.substring(0, 1).toInt();


        if (strpi == 1) {
            for (int i = 0; i < 4; ++i) spnano[i] = strrpi.substring(1 * (i + 1), 3 + (i + 1)).toInt();

            boolgun  = strrpi.substring(12, 13).toInt(),
            boolbomb = strrpi.substring(13, 14).toInt();
        }
        else {
            if     (strpi == 0) error = strrpi.substring(1, 4).toInt(), speed = strrpi.substring(4, 7).toInt();
            else if(strpi == 2) { // compass
                goal  = strrpi.substring(1, 4).toInt(),
                speed = strrpi.substring(4, 7).toInt();

                error = goal - azimuth;
                goal < azimuth ? error += 360 : goal == azimuth ? error = 0 : 0;
                error > 180 ? error = -(360 - error) : 0;
            }

            boolgun  = strrpi.substring(6, 7).toInt(),
            boolbomb = strrpi.substring(7, 8).toInt();
        }

        pid();
//        debug();
    }
}

void uart2nano() {
    if (timer + 50 < millis()){
        for (auto &i : spnano) nano.print(i + 200);

        nano.print(String(boolgun) + String(boolbomb) + "$");

        timer = millis();
    }
}

void setup() {
    ibus.begin(Serial1); // receiver

    matrix.setIntensity(2); // brightness
    matrix.setRotation (2); // rotation
    matrix.fillScreen(LOW);
    matrix.write();

    Wire.begin();
    Wire.beginTransmission(compassAddr);
    Wire.write(0x01);
    Wire.endTransmission();
    while (Wire.available() > 0) Wire.read();

    Serial.begin(9600); // monitor
    rpi.begin(115200); // uart2rpi
    nano.begin(9600); // strnano

    pinMode(A0, INPUT_PULLUP);
    pinMode(13, OUTPUT);
    digitalWrite(13, 1);

    loading();
    rpi.flush();
}



void loop() {
    state();

    if (st == 0) neutral(); // neutral     mode
    if (st == 1) manual();  // manual mode
    if (st == 2) uartrpi(); // autonomous      mode

    uart2nano();
}