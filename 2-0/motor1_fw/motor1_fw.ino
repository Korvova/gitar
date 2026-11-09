// Стенд мотора в тележке (вики 19.30–19.32): гимбал на SimpleFOC Mini V2 (DRV8316), без датчика (open loop).
// 04.11: SimpleFOC на этой плате ESP32 мотор не крутил (позиция в прошивке менялась, ток не шёл), а синус прямо
// на IN1–IN3 через ledc крутит — поэтому синус считаем сами, без библиотеки. Команды прежние — пульт
// 2-0/websim/motor1_pult.html работает как был:
//   x <мм>    куда ехать, ±22          s <мм/с>  скорость          u <В>  напряжение на мотор (сила и нагрев), до 8
//   on / off  включить / отпустить (без тока вал свободен)          z  здесь ноль
//   dir       поменять направление     p <n>     пар полюсов (только при off)          ?  состояние
//   v <мс>    вздрогнуть (только при on)    va <мм>  размах вибрации, до 1.5    vf <Гц>  частота, 5…200
// Путь тележки = угол вала × 6 мм (шестерня m1 z12, стенд 114; на стенде 101 было 13). Подключение: IN1 25, IN2 26, IN3 27, EN 14 (nSLEEP).
#define EN_PIN 14
#define LED_PIN 2
const int HALL[3] = {32, 33, 34};   // три 49E: питание 3.3 В

const int PINS[3] = {25, 26, 27};
const float RP = 6.0;           // мм — делительный радиус шестерни (стенд 114: m1 z12)
const float TRAVEL = 22.0;      // ход ±22
const float U_SUPPLY = 12.0;    // питание драйвера
const float U_MAX = 8.0;        // выше не даём: без датчика тока мотор греется

float shaft = 0, zeroRad = 0, targetMm = 0, speedMm = 50, uMot = 2.0, sgn = 1;
int polePairs = 7;
bool on = false;
float buzzA = 0.5, buzzF = 40;        // вибрация: качаем поле вокруг текущего положения, тележка остаётся на месте
unsigned long buzzEnd = 0, buzzT0 = 0;
String line;
unsigned long tPrint = 0, tLast = 0;

float posMm() { return sgn * (shaft - zeroRad) * RP; }

void writePhases() {
  float off = 0;
  if (buzzEnd && millis() < buzzEnd) off = buzzA / RP * sin(2 * PI * buzzF * (micros() - buzzT0) * 1e-6);
  else buzzEnd = 0;
  float th = polePairs * (shaft + off);               // электрический угол
  float amp = on ? constrain(uMot / U_SUPPLY, 0, 0.48) : 0;
  for (int i = 0; i < 3; i++) {
    float d = 0.5 + amp * sin(th - i * 2 * PI / 3);
    ledcWrite(PINS[i], (uint32_t)(d * 1023));
  }
}

void status() {
  Serial.printf("pos %.2f tgt %.2f u %.1f s %.0f on %d p %d dir %d\n", posMm(), targetMm, uMot, speedMm, on, polePairs, (int)sgn);
}

void setOn(bool v) {
  on = v;
  if (v) targetMm = posMm();                          // не прыгать: держать там, где стоит
  digitalWrite(EN_PIN, v ? HIGH : LOW);
  digitalWrite(LED_PIN, v ? HIGH : LOW);
  writePhases();
}

void handle(String s) {
  s.trim();
  if (!s.length()) return;
  int sp = s.indexOf(' ');
  String c = sp < 0 ? s : s.substring(0, sp);
  float v = sp < 0 ? 0 : s.substring(sp + 1).toFloat();
  if (c == "x") targetMm = constrain(v, -TRAVEL, TRAVEL);
  else if (c == "s") speedMm = constrain(v, 2, 300);
  else if (c == "u") uMot = constrain(v, 0, U_MAX);
  else if (c == "v") {
    if (!on) { Serial.println("err v: сначала on"); return; }
    buzzT0 = micros(); buzzEnd = millis() + (unsigned long)constrain(v, 20, 2000);
  }
  else if (c == "va") buzzA = constrain(v, 0.05, 1.5);
  else if (c == "vf") buzzF = constrain(v, 5, 200);
  else if (c == "on") setOn(true);
  else if (c == "off") setOn(false);
  else if (c == "z") { zeroRad = shaft; targetMm = 0; }
  else if (c == "dir") { sgn = -sgn; zeroRad = shaft; targetMm = 0; }
  else if (c == "p") { if (!on && v >= 1) polePairs = (int)v; else Serial.println("err p: сначала off"); }
  else if (c != "?") { Serial.println("err: " + s); return; }
  status();
}

void setup() {
  Serial.begin(115200);
  pinMode(EN_PIN, OUTPUT);
  pinMode(LED_PIN, OUTPUT);
  analogReadResolution(12);
  for (int i = 0; i < 3; i++) analogSetPinAttenuation(HALL[i], ADC_11db);
  for (int i = 0; i < 3; i++) ledcAttach(PINS[i], 20000, 10);
  setOn(false);                                       // после включения вал свободен — «on» с пульта
  tLast = micros();
  Serial.println("motor1 ready (свой синус, без SimpleFOC)");
  status();
}

void loop() {
  unsigned long now = micros();
  float dt = (now - tLast) * 1e-6;
  tLast = now;
  if (on) {
    float tgt = zeroRad + sgn * targetMm / RP;        // куда повернуть вал, рад
    float step = speedMm / RP * dt;                   // не быстрее заданной скорости
    float e = tgt - shaft;
    shaft += constrain(e, -step, step);
    writePhases();
  }
  while (Serial.available()) {
    char ch = Serial.read();
    if (ch == '\n') { handle(line); line = ""; }
    else if (ch != '\r') line += ch;
  }
  if (millis() - tPrint >= 5) {               // 200 значений в секунду: пик магнита узкий
    tPrint = millis();
    long h[3] = {0, 0, 0};
    for (int k = 0; k < 3; k++) { for (int i = 0; i < 4; i++) h[k] += analogRead(HALL[k]); h[k] /= 4; }
    Serial.printf("pos %.2f h %ld %ld %ld\n", posMm(), h[0], h[1], h[2]);
  }
}
