// Стенд 2204 «мотор в тележке» (вики 19.30–19.32): SimpleFOC Mini V2 (DRV8316), гимбал 2204, без датчика (open loop).
// Тележка едет по рейке: путь = угол вала × 13 мм (шестерня m1 z26). Команды по USB 115200 строками
// (пульт 2-0/websim/motor1_pult.html через Web Serial):
//   x <мм>    куда ехать, ±22          s <мм/с>  скорость          u <В>  напряжение на мотор (сила и нагрев), до 8
//   on / off  включить / отпустить (без тока тележку двигает палец)       z  здесь ноль
//   dir       поменять направление     p <n>     пар полюсов (только при off)          ?  состояние
// Подключение: IN1 25, IN2 26, IN3 27, EN 14, GND общий; питание платы 12 В от PD-триггера.
#include <SimpleFOC.h>

const float RP = 13.0;          // мм — делительный радиус шестерни
const float TRAVEL = 22.0;      // ход ±22 (6 струн, шаг 8.8)
const float U_MAX = 8.0;        // выше не даём: мотор без датчика тока греется

BLDCMotor motor(7);             // 2204 — 12N14P, 7 пар полюсов (проверить: «p»)
BLDCDriver3PWM driver(25, 26, 27, 14);

float zeroRad = 0, targetMm = 0, speedMm = 50, sgn = 1;
bool on = false;
String line;
unsigned long tPrint = 0;

float posMm() { return sgn * (motor.shaft_angle - zeroRad) * RP; }

void status() {
  Serial.printf("pos %.2f tgt %.2f u %.1f s %.0f on %d p %d dir %d\n", posMm(), targetMm, motor.voltage_limit, speedMm, on,
                motor.pole_pairs, (int)sgn);
}

void setOn(bool v) {
  on = v;
  if (v) {
    targetMm = posMm();         // не прыгать: держать там, где стоит
    motor.enable();
  } else {
    motor.disable();
  }
}

void handle(String s) {
  s.trim();
  if (!s.length()) return;
  int sp = s.indexOf(' ');
  String c = sp < 0 ? s : s.substring(0, sp);
  float v = sp < 0 ? 0 : s.substring(sp + 1).toFloat();
  if (c == "x") targetMm = constrain(v, -TRAVEL, TRAVEL);
  else if (c == "s") { speedMm = constrain(v, 2, 300); motor.velocity_limit = speedMm / RP; }
  else if (c == "u") motor.voltage_limit = constrain(v, 0, U_MAX);
  else if (c == "on") setOn(true);
  else if (c == "off") setOn(false);
  else if (c == "z") { zeroRad = motor.shaft_angle; targetMm = 0; }
  else if (c == "dir") { sgn = -sgn; zeroRad = motor.shaft_angle; targetMm = 0; }
  else if (c == "p") { if (!on && v >= 1) motor.pole_pairs = (int)v; else Serial.println("err p: сначала off"); }
  else if (c != "?") { Serial.println("err: " + s); return; }
  status();
}

void setup() {
  Serial.begin(115200);
  driver.voltage_power_supply = 12;
  driver.voltage_limit = U_MAX;
  driver.init();
  motor.linkDriver(&driver);
  motor.controller = MotionControlType::angle_openloop;
  motor.voltage_limit = 2.0;                  // начать слабо, прибавлять с пульта
  motor.velocity_limit = speedMm / RP;
  motor.init();
  motor.disable();                            // после включения тележка свободна — «on» с пульта
  Serial.println("motor1 ready");
  status();
}

void loop() {
  if (on) motor.move(zeroRad + sgn * targetMm / RP);
  while (Serial.available()) {
    char ch = Serial.read();
    if (ch == '\n') { handle(line); line = ""; }
    else if (ch != '\r') line += ch;
  }
  if (millis() - tPrint > 100) {
    tPrint = millis();
    Serial.printf("pos %.2f\n", posMm());
  }
}
