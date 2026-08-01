// ТЕСТ СТРУНЫ с AS5600 (аналоговый OUT -> GPIO34)
// Подключение платы: VCC -> 3.3V, GND -> GND, OUT -> GPIO34
// (I2C-пины SDA/SCL/GPO/DIR не подключаем — работаем в аналоговом режиме)
//
// Открой Tools -> Serial Plotter (115200) и щипай струну:
// покой = ровная линия, щипок = выброс и затухающие колебания.

const int PIN_OUT = 34;

void setup() {
  Serial.begin(115200);
  analogReadResolution(12);            // 0..4095
}

void loop() {
  static long zero = -1;
  int v = analogRead(PIN_OUT);
  if (zero < 0) zero = v;              // первое чтение = ноль покоя
  zero += (v - zero) / 2048;           // медленная подстройка нуля (дрейф)
  Serial.print(v);                     // сырой сигнал
  Serial.print('\t');
  Serial.println(v - (int)zero);       // отклонение от нуля (щипок)
  delayMicroseconds(500);              // ~2000 выборок/сек
}
