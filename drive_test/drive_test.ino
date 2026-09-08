// Тест привода: ESP32 DevKit (WROOM-32) + TMC2209 standalone + NEMA14 pancake
// OTA как в ota_base: hostname gitar-esp32, порт 3232. LED GPIO2 мигает.
// STEP=25, DIR=26, EN=27 (LOW = включен)

#include <WiFi.h>
#include <ArduinoOTA.h>

const char* WIFI_SSID = "MTS_GPON_BC14";
const char* WIFI_PASS = "444YYdc4";

#define LED_PIN 2
const int PIN_STEP = 25;
const int PIN_DIR  = 26;
const int PIN_EN   = 27;

// 200 шагов/об * 1/8 микрошаг; шестерня ленты 12T шаг 4.347 прямо на валу:
// мм ленты за оборот = 12*4.347 = 52.16
const long STEPS_PER_REV = 1600;
const float MM_PER_REV = 52.16;

void stepN(long n, bool dir, float mmps) {
  digitalWrite(PIN_DIR, dir);
  float sps = mmps / MM_PER_REV * STEPS_PER_REV;
  long ramp = min(n / 4, (long)(sps * 0.15));
  for (long i = 0; i < n; i++) {
    long k = min(i, n - 1 - i);
    float f = (ramp > 0 && k < ramp) ? (0.25 + 0.75 * k / (float)ramp) : 1.0;
    unsigned us = (unsigned)(1e6 / (sps * f) / 2);
    digitalWrite(PIN_STEP, HIGH); delayMicroseconds(us);
    digitalWrite(PIN_STEP, LOW);  delayMicroseconds(us);
    if ((i & 0x3F) == 0) ArduinoOTA.handle();   // OTA живёт и во время движения
  }
}

void moveMM(float mm, float mmps) {
  long n = (long)(fabs(mm) / MM_PER_REV * STEPS_PER_REV);
  stepN(n, mm > 0, mmps);
}

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  pinMode(PIN_STEP, OUTPUT);
  pinMode(PIN_DIR, OUTPUT);
  pinMode(PIN_EN, OUTPUT);
  digitalWrite(PIN_EN, HIGH);            // пока не подключимся - мотор отпущен

  WiFi.mode(WIFI_STA);
  WiFi.setHostname("gitar-esp32");
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  while (WiFi.status() != WL_CONNECTED) {
    digitalWrite(LED_PIN, !digitalRead(LED_PIN));
    delay(200);
  }
  Serial.print("IP: "); Serial.println(WiFi.localIP());

  ArduinoOTA.setHostname("gitar-esp32");
  ArduinoOTA.begin();
  digitalWrite(PIN_EN, LOW);             // драйвер включён
}

void loop() {
  ArduinoOTA.handle();
  digitalWrite(LED_PIN, HIGH);

  moveMM(+30, 15);   delay(400);   // медленно туда
  moveMM(-30, 15);   delay(400);   // и обратно
  moveMM(+30, 50);   delay(300);   // быстрее
  moveMM(-30, 50);

  digitalWrite(PIN_EN, HIGH);            // отпустить мотор: тишина + свободный ход
  digitalWrite(LED_PIN, LOW);
  for (int i = 0; i < 30; i++) { ArduinoOTA.handle(); delay(100); }
  digitalWrite(PIN_EN, LOW);
}
