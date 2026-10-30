// Проба стенда 2204: мотор сам крутится в одну сторону (~0.5 об/с, тележку снять с рельсов), без пульта, 4 В.
// EN (GPIO 14, на плате это nSLEEP) всегда HIGH — драйвер не спит. IN1 25, IN2 26, IN3 27.
#include <SimpleFOC.h>

#define EN_PIN 14
#define LED_PIN 2

BLDCMotor motor(7);
BLDCDriver3PWM driver(25, 26, 27);     // EN ведём сами

void setup() {
  Serial.begin(115200);
  pinMode(EN_PIN, OUTPUT);
  pinMode(LED_PIN, OUTPUT);
  driver.voltage_power_supply = 12;
  driver.voltage_limit = 6;
  driver.init();
  motor.linkDriver(&driver);
  motor.controller = MotionControlType::velocity_openloop;
  motor.voltage_limit = 4.0;
  motor.velocity_limit = 20;
  motor.init();
  Serial.println("motor1_test");
}

void loop() {
  unsigned long t = millis();
  digitalWrite(EN_PIN, HIGH);
  digitalWrite(LED_PIN, HIGH);
  motor.move(3.0);                                     // 3 рад/с ≈ полоборота в секунду
  static unsigned long tp = 0;
  if (t - tp > 1000) { tp = t; Serial.println("spin"); }
}
