// Тест 2×49E над магнитами ротора (телескоп v6-А). A: OUT -> GPIO34, питание 3.3V. B: OUT -> GPIO12, питание от GPIO13 (HIGH).
// GPIO12 — пин загрузки: при старте датчик B обесточен (GPIO13 ещё LOW), поэтому плата грузится нормально.
// Вывод: A, B (относительно центра), фаза atan2 и развёрнутый угол ротора.
// Команды по Serial: 'z' — заново снять центр (ноль датчиков), 'r' — обнулить угол.
#include <Arduino.h>
const int PA = 34, PB = 12, PWR_B = 13;
float cA = 0, cB = 0, lastPh = 0, unwr = 0;

float rd(int p) {
  float s = 0;
  for (int i = 0; i < 32; i++) s += analogRead(p);
  return s / 32;
}

void calib() {
  cA = cB = 0;
  for (int i = 0; i < 50; i++) { cA += rd(PA); cB += rd(PB); }
  cA /= 50; cB /= 50;
  unwr = 0; lastPh = 0;
  Serial.printf("# zero A=%.0f B=%.0f\n", cA, cB);
}

void setup() {
  Serial.begin(115200);
  pinMode(PWR_B, OUTPUT); digitalWrite(PWR_B, HIGH);   // питание датчика B
  analogReadResolution(12);
  analogSetAttenuation(ADC_11db);
  delay(300);
  calib();
}

void loop() {
  if (Serial.available()) {
    int c = Serial.read();
    if (c == 'z') calib();
    if (c == 'r') unwr = 0;
  }
  float a = rd(PA) - cA, b = rd(PB) - cB;
  float ph = atan2f(b, a) * 57.2958f;          // фаза внутри периода (период = 90° ротора при 8 магнитах)
  float d = ph - lastPh;
  if (d > 180) d -= 360;
  if (d < -180) d += 360;
  unwr += d; lastPh = ph;
  Serial.printf("A:%.0f B:%.0f phase:%.0f turn:%.1f\n", a, b, ph, unwr / 4.0f);   // turn ≈ угол ротора, °
  delay(10);
}
