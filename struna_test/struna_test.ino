// ТЕСТ СТРУНЫ с AS5600 (аналоговый OUT -> GPIO34) — стример для страницы
// websim/struna_pult.html (Web Serial, Chrome).
// Подключение платы: VCC -> 3.3V, GND -> GND, OUT -> GPIO34
//
// Шлёт ~1000 сырых значений АЦП в секунду, по строке на значение.
// Работает и с Serial Plotter в Arduino IDE (115200).

const int PIN_OUT = 34;

void setup() {
  Serial.begin(115200);
  analogReadResolution(12);            // 0..4095
  analogSetPinAttenuation(PIN_OUT, ADC_11db);   // весь диапазон до 3.3В
}

void loop() {
  static uint32_t next_us = 0;
  uint32_t now = micros();
  if (now < next_us) return;
  next_us = now + 1000;                // 1000 выборок/сек
  // среднее из 4 чтений — глушим шум АЦП
  int v = 0;
  for (int i = 0; i < 4; i++) v += analogRead(PIN_OUT);
  Serial.println(v >> 2);
}
