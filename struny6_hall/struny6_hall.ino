// ШЕСТИСТРУНКА НА ХОЛЛАХ: 6 x 49E прямо в ADC1 (без I2C и мультиплексора)
// Стример для websim/struny6_pult.html (формат тот же: 6 чисел в строке)
//
// Подключение каждого модуля-картриджа (49E надписью вверх в туннель):
//   ножка 1 (левая)   -> шина 3.3V   (клеммник WAGO)
//   ножка 2 (средняя) -> шина GND
//   ножка 3 (правая)  -> свой пин ESP32:
//     струна 1 -> GPIO32   струна 4 -> GPIO35
//     струна 2 -> GPIO33   струна 5 -> GPIO36 (VP)
//     струна 3 -> GPIO34   струна 6 -> GPIO39 (VN)
//
// Покой каждой струны ~2048 (середина питания). ~650 полных опросов/с.

const int PINS[6] = {32, 33, 34, 35, 36, 39};

void setup() {
  Serial.begin(460800);
  analogReadResolution(12);              // 0..4095
  for (int i = 0; i < 6; i++) analogSetPinAttenuation(PINS[i], ADC_11db);
  delay(100);
  Serial.println("# 6 x 49E на ADC: 32 33 34 35 36 39, покой ~2048");
  for (int i = 0; i < 6; i++) {          // стартовый замер: видно, что живо
    Serial.print("# струна ");
    Serial.print(i + 1);
    Serial.print(" (GPIO");
    Serial.print(PINS[i]);
    Serial.print("): ");
    Serial.println(analogRead(PINS[i]));
  }
}

void loop() {
  static uint32_t next_us = 0;
  uint32_t now = micros();
  if (now < next_us) return;
  next_us = now + 1500;                  // ~650 опросов/с (как SR страницы)
  char buf[48];
  int n = 0;
  for (int i = 0; i < 6; i++) {
    uint32_t s = 0;                      // усреднение 4 замеров: шум ADC вниз
    for (int k = 0; k < 4; k++) s += analogRead(PINS[i]);
    n += snprintf(buf + n, sizeof(buf) - n, i ? " %d" : "%d", (int)(s >> 2));
  }
  Serial.println(buf);
}
