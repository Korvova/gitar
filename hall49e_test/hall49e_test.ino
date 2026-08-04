// ТЕСТ ДАТЧИКА ХОЛЛА 49E (SS49E/OH49E) — замена AS5600 на стенде струны?
// Стример для websim/struna_pult.html (тот же формат, что struna_test)
//
// Подключение (49E плоской стороной с надписью к себе, ножки вниз):
//   ножка 1 (левая)  -> 3V3
//   ножка 2 (средняя) -> GND
//   ножка 3 (правая)  -> GPIO34 (ADC)
// Датчик под магнитом плоской стороной к нему, зазор 2-3 мм.
//
// Шлёт ~1000 значений ADC (0..4095) в секунду; покой ~2048 (середина).

const int PIN = 34;                    // ADC1_CH6, только вход

void setup() {
  Serial.begin(115200);
  analogReadResolution(12);            // 0..4095 — как у AS5600
  analogSetPinAttenuation(PIN, ADC_11db);   // полный размах до ~3.3 В
  Serial.println("# 49E на GPIO34: покой ~2048, поле сдвигает вверх/вниз");
}

void loop() {
  static uint32_t next_us = 0;
  uint32_t now = micros();
  if (now < next_us) return;
  next_us = now + 1000;                // 1000 выборок/сек
  Serial.println(analogRead(PIN));
}
