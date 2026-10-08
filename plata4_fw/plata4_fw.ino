// Плата 4 моторов грифа: ESP32 DevKit + 4 x TMC2209 (S2209 V4) на общей линии UART.
// Ножки — вики «Т. Плата для 4-х моторов», пункт 9.8. Адрес драйвера = номер мотора.
// Управление по USB (115200), тот же пульт websim/serial_pult.html. Команды:
//   m <0..3>              — выбрать мотор, дальше все команды к нему
//   deg <°> [об/мин]      — повернуть выбранный мотор
//   sw <полуугол> [rpm]   — качание туда-сюда, sw 0 = стоп
//   stop | hold | free    — стоп / держать / отпустить (выбранный); off — отпустить все
//   cur <мА>              — ток всех драйверов (100..900); holdpct <10..100> — ток удержания в покое, % рабочего
//   zero                  — текущее место выбранного мотора = 0 шагов
//   ms <8|16|32|64>       — дробление шага выбранного мотора (катушка: 32 — микрошаг 0.25 мм на 15×5); шаги в at/tgt — в этих единицах
//   tgt <шаги> [об/мин]    — плавное следование (ползунок): бегунок едет к цели с разгоном/торможением, цель меняется на ходу, без ответа
//   acc <шагов/с²>         — разгон для tgt
//   at <шаги> [об/мин]     — ехать в абсолютное положение (микрошаги от нуля), ответ «ok at N» — для ползунка в пульте катушки
//   curup <мА> | curdn <мА> — ток выбранного мотора при движении вверх / вниз (0 = как cur); up 1|-1 — какой знак deg «вверх»
//                           (катушка-бегунок в руках стоит вертикально: вверх поднимает свой вес, вниз вес помогает)
//   init                  — заново настроить все драйверы (после включения питания моторов)
//   diag                  — опрос всех 4 адресов; diag N — полный тест драйвера N с катушками
//   status
//   spread 1/0            — режим драйверов: 1 = spreadCycle (жёсткий ток, для катушки-бегунка), 0 = stealthChop (тихий, моторы)
// Калибровка струн (Т. Тележки 11.8–11.9), к выбранному мотору:
//   save N    — запомнить текущее положение как струну N (1..6), хранится в памяти ESP
//   ref N     — сверка: «сейчас тележка на струне N» (в начале сессии, мотор не знает, где стоит)
//   go N [rpm] — ехать на струну N;  to M N [rpm] — мотор M на струну N (для мелодий)
//   cal       — таблица калибровки всех моторов;  calclr — стереть калибровку выбранного
#include <TMCStepper.h>
#include <Preferences.h>

const uint8_t P_EN[4]   = {23, 19, 25, 14};
const uint8_t P_STEP[4] = {22, 4, 33, 27};
const uint8_t P_DIR[4]  = {21, 2, 32, 26};
#define TMC_RX 16
#define TMC_TX 17
TMC2209Stepper d0(&Serial2, 0.11f, 0), d1(&Serial2, 0.11f, 1), d2(&Serial2, 0.11f, 2), d3(&Serial2, 0.11f, 3);
TMC2209Stepper* DRV[4] = {&d0, &d1, &d2, &d3};

const long STEPS_PER_REV = 1600;      // 200 * 1/8 — при ms 8; у мотора с ms N — × N/8
int msMul[4] = {1, 1, 1, 1};          // 08.10: дробление/8 по моторам (ms)
float spr(uint8_t m) { return STEPS_PER_REV * msMul[m]; }
// 08.10: плавное следование к цели (tgt) — не блокирует, крутится в loop()
bool fol[4] = {false, false, false, false};
long ftgt[4] = {0, 0, 0, 0};
float fv[4] = {0, 0, 0, 0}, fvmax[4] = {400, 400, 400, 400}, facc[4] = {3000, 3000, 3000, 3000}, fAcc[4] = {0, 0, 0, 0};
unsigned long fLast[4] = {0, 0, 0, 0};
int fDir[4] = {0, 0, 0, 0};
int curMA = 350;
int curUp[4] = {0, 0, 0, 0}, curDn[4] = {0, 0, 0, 0};   // 08.10: ток вверх/вниз, 0 — как curMA
int upSign[4] = {1, 1, 1, 1};                           // направление «вверх» = знак deg
bool useSpread = false;               // 04.10: катушка-бегунок почти без индуктивности — stealthChop может «гулять»
float HOLD_MULT = 0.2;                // ток удержания в покое, доля рабочего: команда holdpct 20/50/100 (палец проворачивает мотор при 20%)
uint8_t sel = 0;
float posDeg[4] = {0, 0, 0, 0};
long posStep[4] = {0, 0, 0, 0};       // положение вала в шагах от включения (или от сверки)
const long NOCAL = -2147483647L;
long cal[4][7];                        // cal[мотор][струна 1..6] — шаги; NOCAL = не задано
Preferences prefs;

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
    d.microsteps(8 * msMul[i]);
    d.rms_current(curMA, HOLD_MULT);
    d.en_spreadCycle(useSpread);
    d.toff(4);
    d.iholddelay(2);
    d.TPOWERDOWN(20);
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
  d.rms_current(curMA, HOLD_MULT);
  digitalWrite(P_EN[addr], LOW);
  delay(5);
  r += d.enn() ? " | EN НЕ ДОХОДИТ (на ножке EN драйвера высокий)" : " | EN доходит";
  bool ola = false, olb = false, s2a = false, s2b = false;
  uint16_t ms0 = d.MSCNT(); bool stepOk = false;   // счётчик микрошагов растёт от каждого STEP, даже если вал зажат
  for (int i = 0; i < 400; i++) {
    digitalWrite(P_STEP[addr], HIGH); delayMicroseconds(1500);
    digitalWrite(P_STEP[addr], LOW);  delayMicroseconds(1500);
    if (i % 50 == 49) {
      ola |= d.ola(); olb |= d.olb();
      if (d.MSCNT() != ms0) stepOk = true;
      s2a |= d.s2ga() || d.s2vsa(); s2b |= d.s2gb() || d.s2vsb();
    }
  }
  r += " | катушка A: " + String(s2a ? "ЗАМЫКАНИЕ" : ola ? "ОБРЫВ" : "ок");
  r += " | катушка B: " + String(s2b ? "ЗАМЫКАНИЕ" : olb ? "ОБРЫВ" : "ок");
  digitalWrite(P_EN[addr], HIGH);                 // после теста мотор отпускаем
  r += stepOk ? " | STEP доходит" : " | STEP НЕ ДОХОДИТ (дорожка STEP или EN)";
  if (d.otpw()) r += " | ПЕРЕГРЕВ";
  return r;
}

void doSteps(uint8_t m, long n, bool fwd, float sps) {
  if (n <= 0) return;
  abortMove = false;
  int dirMA = ((fwd ? 1 : -1) == upSign[m]) ? curUp[m] : curDn[m];
  if (dirMA > 0) DRV[m]->rms_current(dirMA, HOLD_MULT);
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
  posDeg[m] += (fwd ? 1 : -1) * done * 360.0 / spr(m);
  posStep[m] += (fwd ? 1 : -1) * done;
  if (dirMA > 0) DRV[m]->rms_current(curMA, HOLD_MULT);    // в покое — обычный ток (удержание от него)
}

bool calRange(uint8_t m, long &lo, long &hi);
// границы хода по калибровке (струны 1 и 6 ± LIM_MARGIN) — для кривошипов с сектором (R7.5, R10 ×3.25).
// По умолчанию ВЫКЛ (03.10): стенд с шатуном и гриф ×2 крутятся полным оборотом. Включить: «lim 1».
bool useLim = false;
void doDeg(uint8_t m, float deg, float rpm) {
  if (fabs(deg) < 0.5) return;
  long lo, hi;
  if (useLim && calRange(m, lo, hi)) {
    long tgt = posStep[m] + (long)(deg / 360.0 * spr(m));
    if (tgt < lo) tgt = lo;
    if (tgt > hi) tgt = hi;
    deg = (tgt - posStep[m]) * 360.0 / spr(m);
    if (fabs(deg) < 0.2) return;
  }
  float sps = rpm / 60.0 * spr(m);
  if (sps < 4) sps = 4;                  // 04.10: было 40 — катушке-бегунку нужно медленнее (4 мкшага/с ≈ 2 мм/с)
  doSteps(m, lround(fabs(deg) / 360.0 * spr(m)), deg > 0, sps);
}

void calLoad() {
  prefs.begin("gitar", true);
  for (uint8_t m = 0; m < 4; m++)
    for (uint8_t n = 1; n <= 6; n++) {
      char k[8]; snprintf(k, sizeof(k), "c%u_%u", m, n);
      cal[m][n] = prefs.getLong(k, NOCAL);
    }
  prefs.end();
}

void calSave(uint8_t m, uint8_t n) {
  prefs.begin("gitar", false);
  char k[8]; snprintf(k, sizeof(k), "c%u_%u", m, n);
  if (cal[m][n] == NOCAL) prefs.remove(k); else prefs.putLong(k, cal[m][n]);
  prefs.end();
}

const long LIM_MARGIN = 40;             // ~9° за крайние струны
bool calRange(uint8_t m, long &lo, long &hi) {
  if (cal[m][1] == NOCAL || cal[m][6] == NOCAL) return false;
  lo = min(cal[m][1], cal[m][6]) - LIM_MARGIN;
  hi = max(cal[m][1], cal[m][6]) + LIM_MARGIN;
  return true;
}

String calStr(uint8_t m) {
  String r = "cal " + String(m) + ":";
  for (uint8_t n = 1; n <= 6; n++) r += " " + (cal[m][n] == NOCAL ? String("-") : String(cal[m][n]));
  return r;
}

// ехать мотором m на струну n; false — струна не откалибрована
bool goString(uint8_t m, uint8_t n, float rpm) {
  if (n < 1 || n > 6 || cal[m][n] == NOCAL) return false;
  long d = cal[m][n] - posStep[m];
  float sps = rpm / 60.0 * spr(m);
  if (sps < 40) sps = 40;
  doSteps(m, labs(d), d > 0, sps);
  return true;
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
  else if (cmd == "stop") { swHalf = 0; abortMove = true; for (uint8_t i = 0; i < 4; i++) { if (fol[i]) ftgt[i] = posStep[i]; } reply("ok стоп"); }
  else if (cmd == "free") { swHalf = 0; fol[sel] = false; digitalWrite(P_EN[sel], HIGH); reply("ok мотор " + String(sel) + " отпущен"); }
  else if (cmd == "holdpct") {
    int pc = rest.toInt();
    if (pc < 10 || pc > 100) { reply("holdpct 10..100"); return; }
    HOLD_MULT = pc / 100.0;
    for (uint8_t i = 0; i < 4; i++) DRV[i]->rms_current(curMA, HOLD_MULT);
    reply("ok удержание " + String(pc) + "% (" + String((int)(curMA * HOLD_MULT)) + " мА)");
  }
  else if (cmd == "off") { swHalf = 0; for (uint8_t i = 0; i < 4; i++) fol[i] = false; for (uint8_t i = 0; i < 4; i++) digitalWrite(P_EN[i], HIGH); reply("ok все моторы отпущены"); }
  else if (cmd == "hold") { digitalWrite(P_EN[sel], LOW); reply("ok мотор " + String(sel) + " держит"); }
  else if (cmd == "cur") {
    int ma = (int)a1;
    if (ma >= 100 && ma <= 900) { curMA = ma; for (uint8_t i = 0; i < 4; i++) DRV[i]->rms_current(curMA, HOLD_MULT); reply("ok ток " + String(curMA) + " мА"); }
    else reply("ток 100..900");
  }
  else if (cmd == "curup" || cmd == "curdn") {
    int ma = (int)a1;
    if (ma == 0 || (ma >= 100 && ma <= 900)) {
      (cmd == "curup" ? curUp : curDn)[sel] = ma;
      reply("ok мотор " + String(sel) + " ток " + (cmd == "curup" ? "вверх " : "вниз ") + (ma ? String(ma) + " мА" : String("как cur")));
    } else reply("ток 0 или 100..900");
  }
  else if (cmd == "up") { upSign[sel] = a1 < 0 ? -1 : 1; reply("ok мотор " + String(sel) + " вверх = " + (upSign[sel] > 0 ? "+" : "-")); }
  else if (cmd == "save" || cmd == "ref" || cmd == "go") {
    int n = rest.toInt();
    if (n < 1 || n > 6) { reply("струна 1..6"); return; }
    if (cmd == "save") { cal[sel][n] = posStep[sel]; calSave(sel, n); reply("ok мотор " + String(sel) + " струна " + String(n) + " запомнена | " + calStr(sel)); }
    else if (cmd == "ref") {
      if (cal[sel][n] == NOCAL) { reply("струна " + String(n) + " у мотора " + String(sel) + " не откалибрована"); return; }
      posStep[sel] = cal[sel][n]; reply("ok сверка: мотор " + String(sel) + " стоит на струне " + String(n));
    } else {
      swHalf = 0;
      reply(goString(sel, n, a2 > 0 ? a2 : 60) ? "ok мотор " + String(sel) + " на струне " + String(n) : "струна " + String(n) + " не откалибрована");
    }
  }
  else if (cmd == "to") {
    int m = rest.toInt();
    int sp = rest.indexOf(' ');
    String r2 = sp < 0 ? "" : rest.substring(sp + 1);
    int n = r2.toInt();
    int sp3 = r2.indexOf(' ');
    float rpm = sp3 < 0 ? 90 : r2.substring(sp3 + 1).toFloat();
    if (m < 0 || m > 3) { reply("нет такого мотора"); return; }
    swHalf = 0;
    reply(goString(m, n, rpm) ? "ok to " + String(m) + " " + String(n) : "струна " + String(n) + " у мотора " + String(m) + " не откалибрована");
  }
  else if (cmd == "cal") { for (uint8_t m = 0; m < 4; m++) reply(calStr(m)); }
  else if (cmd == "spread") { useSpread = a1 > 0; for (uint8_t i = 0; i < 4; i++) DRV[i]->en_spreadCycle(useSpread); reply(String("ok режим ") + (useSpread ? "spreadCycle" : "stealthChop")); }
  else if (cmd == "lim") { useLim = a1 > 0; reply(String("ok границы хода по калибровке ") + (useLim ? "вкл" : "выкл")); }
  else if (cmd == "calclr") { for (uint8_t n = 1; n <= 6; n++) { cal[sel][n] = NOCAL; calSave(sel, n); } reply("ok калибровка мотора " + String(sel) + " стёрта"); }
  else if (cmd == "zero") { posStep[sel] = 0; posDeg[sel] = 0; ftgt[sel] = 0; fv[sel] = 0; fAcc[sel] = 0; reply("ok zero " + String(sel)); }
  else if (cmd == "ms") {
    int n = (int)a1;
    if (n == 8 || n == 16 || n == 32 || n == 64) {
      int k = n / 8;
      posStep[sel] = posStep[sel] * k / msMul[sel]; ftgt[sel] = ftgt[sel] * k / msMul[sel];
      msMul[sel] = k; DRV[sel]->microsteps(n);
      reply("ok мотор " + String(sel) + " дробление 1/" + String(n));
    } else reply("ms 8|16|32|64");
  }
  else if (cmd == "tgt") {
    swHalf = 0;
    if (!fol[sel]) { fol[sel] = true; ftgt[sel] = posStep[sel]; fv[sel] = 0; fAcc[sel] = 0; fDir[sel] = 0; fLast[sel] = micros(); }
    ftgt[sel] = (long)a1;
    if (a2 > 0) fvmax[sel] = max(4.0f, (float)(a2 / 60.0 * spr(sel)));
    digitalWrite(P_EN[sel], LOW);
  }
  else if (cmd == "acc") { if (a1 > 0) facc[sel] = a1; reply("ok разгон " + String(facc[sel], 0) + " шагов/с²"); }
  else if (cmd == "at") {
    swHalf = 0; fol[sel] = false;
    long d = (long)a1 - posStep[sel];
    float sps = (a2 > 0 ? a2 : 30) / 60.0 * spr(sel);
    if (sps < 4) sps = 4;
    doSteps(sel, labs(d), d > 0, sps);
    reply("ok at " + String(posStep[sel]));
  }
  else if (cmd == "deg") { swHalf = 0; fol[sel] = false; doDeg(sel, a1, a2 > 0 ? a2 : 30); reply("ok " + statusStr()); }
  else if (cmd == "sw") {
    swHalf = fabs(a1); swRpm = a2 > 0 ? a2 : 30; swDir = 1; fol[sel] = false;
    reply(swHalf > 0 ? "ok качание мотора " + String(sel) : "ok качание стоп");
  }
  else reply("? команды: m deg sw stop hold free off cur init diag status save ref go to cal calclr zero at tgt acc ms curup curdn up spread");
}

String rxBuf;

// плавное следование: желаемая скорость к цели — не больше vmax и не больше sqrt(2·a·путь) (успеть затормозить),
// к ней скорость подтягивается с разгоном a; шаги выдаём по накопленному пути
void followService(uint8_t m) {
  unsigned long now = micros();
  float dt = (now - fLast[m]) * 1e-6f; fLast[m] = now;
  if (dt > 0.05f) dt = 0.05f;
  long d = ftgt[m] - posStep[m];
  float vdes = d == 0 ? 0 : (d > 0 ? 1 : -1) * min(fvmax[m], sqrtf(2 * facc[m] * labs(d)));
  float v = fv[m];
  if (v < vdes) v = min(vdes, v + facc[m] * dt); else v = max(vdes, v - facc[m] * dt);
  fv[m] = v;
  int dir = v > 1 ? 1 : (v < -1 ? -1 : 0);
  if (dir != fDir[m]) {                                  // ток вверх/вниз (curup/curdn), в покое — обычный
    int ma = dir == 0 ? curMA : (dir == upSign[m] ? curUp[m] : curDn[m]);
    if (ma <= 0) ma = curMA;
    DRV[m]->rms_current(ma, HOLD_MULT);
    fDir[m] = dir;
  }
  fAcc[m] += v * dt;
  while (fAcc[m] >= 1 && posStep[m] < ftgt[m] + 1) {
    digitalWrite(P_DIR[m], HIGH); digitalWrite(P_STEP[m], HIGH); delayMicroseconds(3); digitalWrite(P_STEP[m], LOW);
    posStep[m]++; fAcc[m] -= 1;
  }
  while (fAcc[m] <= -1 && posStep[m] > ftgt[m] - 1) {
    digitalWrite(P_DIR[m], LOW); digitalWrite(P_STEP[m], HIGH); delayMicroseconds(3); digitalWrite(P_STEP[m], LOW);
    posStep[m]--; fAcc[m] += 1;
  }
  if (d == 0 && fabsf(v) < 1) { fv[m] = 0; fAcc[m] = 0; }
  posDeg[m] = posStep[m] * 360.0 / spr(m);
}

void setup() {
  for (uint8_t i = 0; i < 4; i++) {
    pinMode(P_EN[i], OUTPUT); digitalWrite(P_EN[i], HIGH);   // все драйверы выключены
    pinMode(P_STEP[i], OUTPUT); digitalWrite(P_STEP[i], LOW);
    pinMode(P_DIR[i], OUTPUT); digitalWrite(P_DIR[i], LOW);
  }
  Serial.begin(115200);
  Serial2.begin(115200, SERIAL_8N1, TMC_RX, TMC_TX);
  tmcSetupAll();
  calLoad();
  reply("ok плата 4 моторов готова (m N, deg, sw, stop, hold, free, cur, init, diag, status)");
}

void loop() {
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n' || c == '\r') { if (rxBuf.length()) { execCmd(rxBuf); rxBuf = ""; } }
    else if (rxBuf.length() < 80) rxBuf += c;
  }
  for (uint8_t m = 0; m < 4; m++) if (fol[m]) followService(m);
  if (swHalf > 0) {
    doDeg(sel, swDir * 2 * swHalf, swRpm);
    swDir = -swDir;
    if (abortMove) swHalf = 0;
  }
}
