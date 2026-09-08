// ШЕСТИСТРУНКА: 6 x AS5600/AS5600L через мультиплексор TCA9548A (CJMCU-9548)
// Стример для websim/struny6_pult.html
//
// Подключение (терминал-адаптер ESP32 30pin):
//   3V3 -> VIN мультиплексора и VCC всех 6 плат AS5600
//   GND -> GND мультиплексора, всех плат и DIR каждой платы
//   D21 -> SDA мультиплексора, D22 -> SCL мультиплексора
//   SD0/SC0 .. SD5/SC5 -> SDA/SCL плат струн 1..6
//   A0,A1,A2 мультиплексора -> GND (адрес 0x70); RST не подключать
//
// Шлёт ~650 строк/с: "v0 v1 v2 v3 v4 v5" (углы 0..4095, -1 = датчика нет)

#include <Wire.h>

uint8_t tca = 0;                       // адрес TCA9548A (скан 0x70..0x77)
uint8_t addr[6] = {0};                 // адрес AS5600 на канале (0 = нет)

void tcaSelect(uint8_t ch) {
  Wire.beginTransmission(tca);
  Wire.write(1 << ch);
  Wire.endTransmission();
}

uint16_t readAngle(uint8_t a) {
  Wire.beginTransmission(a);
  Wire.write(0x0C);                    // RAW ANGLE (2 байта)
  if (Wire.endTransmission(false) != 0) return 0xFFFF;
  Wire.requestFrom((int)a, 2);
  if (Wire.available() < 2) return 0xFFFF;
  uint16_t hi = Wire.read(), lo = Wire.read();
  return ((hi & 0x0F) << 8) | lo;
}

void setup() {
  Serial.begin(460800);
  Wire.begin(21, 22, 400000);          // SDA, SCL, 400 кГц
  delay(200);
  for (uint8_t a = 0x70; a <= 0x77; a++) {   // ищем мультиплексор
    Wire.beginTransmission(a);
    if (Wire.endTransmission() == 0) { tca = a; break; }
  }
  if (!tca) {
    Serial.println("# TCA9548A НЕ НАЙДЕН: проверь SDA=21 SCL=22 и питание");
    return;
  }
  Serial.print("# TCA9548A найден, адрес 0x");
  Serial.println(tca, HEX);
  for (uint8_t ch = 0; ch < 6; ch++) {       // ищем датчики по каналам
    tcaSelect(ch);
    for (uint8_t a : {0x36, 0x40}) {
      Wire.beginTransmission(a);
      if (Wire.endTransmission() == 0) { addr[ch] = a; break; }
    }
    Serial.print("# канал ");
    Serial.print(ch);
    if (addr[ch]) {
      Serial.print(": AS5600 на 0x");
      Serial.println(addr[ch], HEX);
    } else {
      Serial.println(": пусто");
    }
  }
}

void loop() {
  static uint32_t next_us = 0;
  uint32_t now = micros();
  if (now < next_us) return;
  next_us = now + 1500;                // ~650 полных опросов/с
  if (!tca) { delay(500); return; }
  char buf[48];
  int n = 0;
  for (uint8_t ch = 0; ch < 6; ch++) {
    int v = -1;
    if (addr[ch]) {
      tcaSelect(ch);
      uint16_t r = readAngle(addr[ch]);
      if (r != 0xFFFF) v = r;
    }
    n += snprintf(buf + n, sizeof(buf) - n, ch ? " %d" : "%d", v);
  }
  Serial.println(buf);
}
