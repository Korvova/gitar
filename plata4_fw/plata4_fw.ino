// Плата 4 моторов грифа: ESP32 DevKit + 4 x TMC2209 (S2209 V4) на общей линии UART.
// Ножки — вики «Т. Плата для 4-х моторов», пункт 9.8. Адрес драйвера = номер мотора.
// Управление по USB (115200), тот же пульт websim/serial_pult.html. Команды:
//   m <0..3>              — выбрать мотор, дальше все команды к нему
//   deg <°> [об/мин]      — повернуть выбранный мотор
//   sw <полуугол> [rpm]   — качание туда-сюда, sw 0 = стоп
//   stop | hold | free    — стоп / держать / отпустить (выбранный)
//   cur <мА>              — ток всех драйверов (100..900)
//   init                  — заново настроить все драйверы (после включения питания моторов)
//   diag                  — опрос всех 4 адресов; diag N — полный тест драйвера N с катушками
//   status
#include <TMCStepper.h>

const uint8_t P_EN[4]   = {23, 19, 25, 14};
const uint8_t P_STEP[4] = {22, 4, 33, 27};
const uint8_t P_DIR[4]  = {21, 2, 32, 26};
#define TMC_RX 16
#define TMC_TX 17
TMC2209Stepper d0(&Serial2, 0.11f, 0), d1(&Serial2, 0.11f, 1), d2(&Serial2, 0.11f, 2), d3(&Serial2, 0.11f, 3);
TMC2209Stepper* DRV[4] = {&d0, &d1, &d2, &d3};

const long STEPS_PER_REV = 1600;      // 200 * 1/8
int curMA = 350;
uint8_t sel = 0;
float posDeg[4] = {0, 0, 0, 0};
float swHalf = 0, swRpm = 30;
int swDir = 1;
volatile bool abortMove = false;

void tmcSetupAll() {
  for (uint8_t i = 0; i < 4; i++) {
    TMC2209Stepper& d = *DRV[i];
    d.begin();
    d.pdn_disable(true);
    d.I_scale_analog(false);
    d.mstep_reg_select(true);
    d.microsteps(8);
    d.rms_current(curMA);
    d.en_spreadCycle(false);
    d.toff(4);
    d.iholddelay(2);
    d.ihold(8);
  }
}

String diagStr(uint8_t addr, bool coils) {
  uint8_t req[4] = {0x05, addr, 0x06, 0};
  uint8_t crc = 0;
  for (int i = 0; i < 3; i++) {
    uint8_t b = req[i];
    for (int j = 0; j < 8; j++) {
      if ((crc >> 7) ^ (b & 1)) crc = (crc << 1) ^ 0x07; else crc <<= 1;
      b >>= 1;
    }
  }
  req[3] = crc;
  while (Serial2.available()) Serial2.read();
  Serial2.write(req, 4);
  delay(30);
  int got = Serial2.available();
  while (Serial2.available()) Serial2.read();
  String r = "адрес " + String(addr) + ": байт " + String(got);
  if (got == 0) return r + " -> линия RX2 мертва";
  if (got < 12) return r + " -> драйвер молчит (нет драйвера, нет VM или не тот адрес)";
  TMC2209Stepper& d = *DRV[addr & 3];
  uint8_t ver = d.version();
  if (d.CRCerror) return r + " -> ответ битый (два драйвера на одном адресе?)";
  r += " | ок, версия 0x" + String(ver, HEX) + " | ток " + String(d.rms_current()) + " мА";
  if (!coils) return r;
  d.rms_current(curMA);
  digitalWrite(P_EN[addr], LOW);
  bool ola = false, olb = false, s2a = false, s2b = false;
  for (int i = 0; i < 400; i++) {
    digitalWrite(P_STEP[addr], HIGH); delayMicroseconds(1500);
    digitalWrite(P_STEP[addr], LOW);  delayMicroseconds(1500);
    if (i % 50 == 49) {
      ola |= d.ola(); olb |= d.olb();
      s2a |= d.s2ga() || d.s2vsa(); s2b |= d.s2gb() || d.s2vsb();
    }
  }
  r += " | катушка A: " + String(s2a ? "ЗАМЫКАНИЕ" : ola ? "ОБРЫВ" : "ок");
  r += " | катушка B: " + String(s2b ? "ЗАМЫКАНИЕ" : olb ? "ОБРЫВ" : "ок");
  if (d.otpw()) r += " | ПЕРЕГРЕВ";
  return r;
}

void doSteps(uint8_t m, long n, bool fwd, float sps) {
  if (n <= 0) return;
  abortMove = false;
  digitalWrite(P_EN[m], LOW);
  digitalWrite(P_DIR[m], fwd);
  long ramp = min(n / 4, (long)(sps * 0.15));
  long done = 0;
  for (long i = 0; i < n; i++) {
    long k = min(i, n - 1 - i);
    float f = (ramp > 0 && k < ramp) ? (0.25 + 0.75 * k / (float)ramp) : 1.0;
    unsigned us = (unsigned)(1e6 / (sps * f) / 2);
    digitalWrite(P_STEP[m], HIGH); delayMicroseconds(us);
    digitalWrite(P_STEP[m], LOW);  delayMicroseconds(us);
    done++;
    if ((i & 0x7F) == 0 && Serial.available() && Serial.peek() == 's') { abortMove = true; break; }
  }
  posDeg[m] += (fwd ? 1 : -1) * done * 360.0 / STEPS_PER_REV;
}

void doDeg(uint8_t m, float deg, float rpm) {
  if (fabs(deg) < 0.5) return;
  float sps = rpm / 60.0 * STEPS_PER_REV;
  if (sps < 40) sps = 40;
  doSteps(m, (long)(fabs(deg) / 360.0 * STEPS_PER_REV), deg > 0, sps);
}

String statusStr() {
  String s = "мотор " + String(sel) + " | вал";
  for (uint8_t i = 0; i < 4; i++) s += " " + String(i) + ":" + String(posDeg[i], 0) + "°";
  if (swHalf > 0) s += " | КАЧАНИЕ ±" + String(swHalf, 0) + "°";
  return s;
}

void reply(const String& s) { Serial.println(s); }

void execCmd(String line) {
  line.trim();
  if (!line.length()) return;
  int sp1 = line.indexOf(' ');
  String cmd = sp1 < 0 ? line : line.substring(0, sp1);
  String rest = sp1 < 0 ? "" : line.substring(sp1 + 1);
  float a1 = rest.toFloat();
  int sp2 = rest.indexOf(' ');
  float a2 = sp2 < 0 ? 0 : rest.substring(sp2 + 1).toFloat();

  if (cmd == "m") {
    int m = rest.toInt();
    if (m < 0 || m > 3) { reply("нет такого мотора"); return; }
    swHalf = 0; sel = m; reply("ok выбран мотор " + String(sel));
  }
  else if (cmd == "status") reply(statusStr());
  else if (cmd == "init") { tmcSetupAll(); reply("ok драйверы настроены, ток " + String(curMA) + " мА"); }
  else if (cmd == "diag") {
    if (rest.length()) reply(diagStr((uint8_t)constrain(rest.toInt(), 0, 3), true));
    else for (uint8_t a = 0; a < 4; a++) reply(diagStr(a, false));
  }
  else if (cmd == "stop") { swHalf = 0; abortMove = true; reply("ok стоп"); }
  else if (cmd == "free") { swHalf = 0; digitalWrite(P_EN[sel], HIGH); reply("ok мотор " + String(sel) + " отпущен"); }
  else if (cmd == "hold") { digitalWrite(P_EN[sel], LOW); reply("ok мотор " + String(sel) + " держит"); }
  else if (cmd == "cur") {
    int ma = (int)a1;
    if (ma >= 100 && ma <= 900) { curMA = ma; for (uint8_t i = 0; i < 4; i++) DRV[i]->rms_current(curMA); reply("ok ток " + String(curMA) + " мА"); }
    else reply("ток 100..900");
  }
  else if (cmd == "deg") { swHalf = 0; doDeg(sel, a1, a2 > 0 ? a2 : 30); reply("ok " + statusStr()); }
  else if (cmd == "sw") {
    swHalf = fabs(a1); swRpm = a2 > 0 ? a2 : 30; swDir = 1;
    reply(swHalf > 0 ? "ok качание мотора " + String(sel) : "ok качание стоп");
  }
  else reply("? команды: m deg sw stop hold free cur init diag status");
}

String rxBuf;

void setup() {
  for (uint8_t i = 0; i < 4; i++) {
    pinMode(P_EN[i], OUTPUT); digitalWrite(P_EN[i], HIGH);   // все драйверы выключены
    pinMode(P_STEP[i], OUTPUT); digitalWrite(P_STEP[i], LOW);
    pinMode(P_DIR[i], OUTPUT); digitalWrite(P_DIR[i], LOW);
  }
  Serial.begin(115200);
  Serial2.begin(115200, SERIAL_8N1, TMC_RX, TMC_TX);
  tmcSetupAll();
  reply("ok плата 4 моторов готова (m N, deg, sw, stop, hold, free, cur, init, diag, status)");
}

void loop() {
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n' || c == '\r') { if (rxBuf.length()) { execCmd(rxBuf); rxBuf = ""; } }
    else if (rxBuf.length() < 80) rxBuf += c;
  }
  if (swHalf > 0) {
    doDeg(sel, swDir * 2 * swHalf, swRpm);
    swDir = -swDir;
    if (abortMove) swHalf = 0;
  }
}
