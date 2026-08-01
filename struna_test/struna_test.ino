// ТЕСТ СТРУНЫ с AS5600/AS5600L по I2C — стример для websim/struna_pult.html
// Подключение: VCC->3.3V, GND->GND, SDA->GPIO21, SCL->GPIO22, DIR->GND
// (у AS5600L аналоговый OUT не работает — читаем угол по I2C)
//
// Шлёт ~1000 значений угла (0..4095) в секунду, по строке на значение.

#include <Wire.h>

uint8_t addr = 0;                      // найдём: 0x36 (AS5600) или 0x40 (L)

uint16_t readAngle() {
  Wire.beginTransmission(addr);
  Wire.write(0x0C);                    // RAW ANGLE (2 байта)
  if (Wire.endTransmission(false) != 0) return 0xFFFF;
  Wire.requestFrom((int)addr, 2);
  if (Wire.available() < 2) return 0xFFFF;
  uint16_t hi = Wire.read(), lo = Wire.read();
  return ((hi & 0x0F) << 8) | lo;
}

void setup() {
  Serial.begin(115200);
  Wire.begin(21, 22, 400000);          // SDA, SCL, 400 кГц
  delay(100);
  for (uint8_t a : {0x36, 0x40}) {     // автопоиск чипа
    Wire.beginTransmission(a);
    if (Wire.endTransmission() == 0) { addr = a; break; }
  }
  if (addr) {
    Serial.print("# AS5600 найден, адрес 0x");
    Serial.println(addr, HEX);
  } else {
    Serial.println("# ЧИП НЕ НАЙДЕН: проверь SDA=21 SCL=22 и питание");
  }
}

void loop() {
  static uint32_t next_us = 0;
  uint32_t now = micros();
  if (now < next_us) return;
  next_us = now + 1000;                // 1000 выборок/сек
  if (!addr) { delay(500); return; }
  uint16_t v = readAngle();
  if (v != 0xFFFF) Serial.println(v);
}
