// Веб-пульт тренажёра: ESP32 DevKit + TMC2209 + NEMA14 (1 канал, тележка 1)
// Страница: http://gitar-esp32.local (http://192.168.1.4). OTA порт 3232.
// STEP=25, DIR=26, EN=27 (LOW = включен). LED GPIO2: в сети = горит.
//
// v2: + управление по USB (Web Serial, 115200). Команды текстом, по строке:
//   status | move <mm> [мм/с] | deg <градусы> [об/мин] | stop | free | hold
//   markl | markr | center | demo 1|0 | cur <мА> | mmrev <мм/об>
//   sw <полуугол°> [об/мин]  — КАЧАНИЕ для стенда (туда-сюда), sw 0 = стоп
// Страница-пульт: websim/serial_pult.html (открыть в Chrome, «Подключить»).
//
// Калибровка (тросовая версия): довести тележку до края -> «Это ЛЕВЫЙ край»,
// до другого -> «Это ПРАВЫЙ край». Движения зажимаются в границы (запас 1 мм).

#include <WiFi.h>
#include <WebServer.h>
#include <ArduinoOTA.h>
#include <TMCStepper.h>

const char* WIFI_SSID = "MTS_GPON_BC14";
const char* WIFI_PASS = "444YYdc4";

#define LED_PIN 2
const int PIN_STEP = 25, PIN_DIR = 26, PIN_EN = 27;
#define TMC_RX 16
#define TMC_TX 17
TMC2209Stepper drv(&Serial2, 0.11f, 0);
int curMA = 350;

const long STEPS_PER_REV = 1600;      // 200*1/8
// намотка зависит от привода — переключается на странице:
//   диск Ø54 = 171.2 | диск Ø27 = 86.4 | барабан-стопка = 29.8
float MM_PER_REV = 171.2;
const float EDGE_GAP = 1.0;           // запас от краёв, мм

float posMM = 0;                      // текущая позиция (условная)
float posDeg = 0;                     // угол вала для стенда, градусы
bool hasL = false, hasR = false;
float valL = 0, valR = 0;
volatile bool abortMove = false;
bool demoOn = false;
uint32_t demoNextAt = 0;
float swHalf = 0, swRpm = 30;         // качание стенда: полуугол и скорость
int swDir = 1;

void tmcSetup() {
  Serial2.begin(115200, SERIAL_8N1, TMC_RX, TMC_TX);
  drv.begin();
  drv.pdn_disable(true);
  drv.I_scale_analog(false);
  drv.mstep_reg_select(true);
  drv.microsteps(8);
  drv.rms_current(curMA);
  drv.en_spreadCycle(false);          // StealthChop — тихо
  drv.toff(4);
  drv.iholddelay(2);
  drv.ihold(8);
}

WebServer server(80);

// ---- низкоуровневое движение шагами (прерываемое) ----
void doSteps(long n, bool dirPositive, float sps) {
  if (n <= 0) return;
  abortMove = false;
  digitalWrite(PIN_EN, LOW);
  digitalWrite(PIN_DIR, dirPositive);
  long ramp = min(n / 4, (long)(sps * 0.15));
  long done = 0;
  for (long i = 0; i < n; i++) {
    long k = min(i, n - 1 - i);
    float f = (ramp > 0 && k < ramp) ? (0.25 + 0.75 * k / (float)ramp) : 1.0;
    unsigned us = (unsigned)(1e6 / (sps * f) / 2);
    digitalWrite(PIN_STEP, HIGH); delayMicroseconds(us);
    digitalWrite(PIN_STEP, LOW);  delayMicroseconds(us);
    done++;
    if ((i & 0x7F) == 0) {
      server.handleClient(); ArduinoOTA.handle();
      if (Serial.available() && Serial.peek() == 's') abortMove = true;  // stop по USB
      if (abortMove) break;
    }
  }
  float rev = done * 1.0 / STEPS_PER_REV;
  posMM += (dirPositive ? 1 : -1) * rev * MM_PER_REV;
  posDeg += (dirPositive ? 1 : -1) * rev * 360.0;
}

// движение на mm (может быть прервано abortMove); обновляет posMM
void doMove(float mm, float mmps) {
  if (fabs(mm) < 0.01) return;
  long n = (long)(fabs(mm) / MM_PER_REV * STEPS_PER_REV);
  float sps = mmps / MM_PER_REV * STEPS_PER_REV;
  doSteps(n, mm > 0, sps);
}

// поворот вала на градусы (для стенда-кривошипа)
void doDeg(float deg, float rpm) {
  if (fabs(deg) < 0.5) return;
  long n = (long)(fabs(deg) / 360.0 * STEPS_PER_REV);
  float sps = rpm / 60.0 * STEPS_PER_REV;
  if (sps < 40) sps = 40;
  doSteps(n, deg > 0, sps);
}

// целевое движение с зажимом в границы
void moveClamped(float mm, float mmps) {
  if (hasL && hasR) {
    float lo = min(valL, valR) + EDGE_GAP, hi = max(valL, valR) - EDGE_GAP;
    float tgt = posMM + mm;
    if (tgt < lo) tgt = lo;
    if (tgt > hi) tgt = hi;
    mm = tgt - posMM;
  }
  doMove(mm, mmps);
}

String statusStr() {
  String s = "поз " + String(posMM, 1) + " мм | вал " + String(posDeg, 0) + "°";
  if (hasL) s += " | L=" + String(valL, 1);
  if (hasR) s += " | R=" + String(valR, 1);
  if (hasL && hasR) s += " (ход " + String(fabs(valR - valL), 1) + ")";
  if (demoOn) s += " | ТРЕНАЖЁР";
  if (swHalf > 0) s += " | КАЧАНИЕ ±" + String(swHalf, 0) + "°";
  return s;
}

// ---- USB-команды (Web Serial) ----
String rxBuf;

void serialReply(const String& s) { Serial.println(s); }

void execCmd(String line) {
  line.trim();
  if (!line.length()) return;
  int sp1 = line.indexOf(' ');
  String cmd = sp1 < 0 ? line : line.substring(0, sp1);
  String rest = sp1 < 0 ? "" : line.substring(sp1 + 1);
  float a1 = rest.toFloat();
  int sp2 = rest.indexOf(' ');
  float a2 = sp2 < 0 ? 0 : rest.substring(sp2 + 1).toFloat();

  if (cmd == "status") serialReply(statusStr());
  else if (cmd == "stop") { demoOn = false; swHalf = 0; abortMove = true; serialReply("ok стоп"); }
  else if (cmd == "free") { demoOn = false; swHalf = 0; digitalWrite(PIN_EN, HIGH); serialReply("ok мотор отпущен"); }
  else if (cmd == "hold") { digitalWrite(PIN_EN, LOW); serialReply("ok мотор держит"); }
  else if (cmd == "move") { demoOn = false; swHalf = 0; moveClamped(a1, a2 > 0 ? a2 : 10); serialReply("ok " + statusStr()); }
  else if (cmd == "deg")  { demoOn = false; swHalf = 0; doDeg(a1, a2 > 0 ? a2 : 30); serialReply("ok " + statusStr()); }
  else if (cmd == "sw") {                      // качание стенда: sw 60 [rpm]
    demoOn = false;
    swHalf = constrain(a1, 0, 180);
    if (a2 > 0) swRpm = constrain(a2, 5, 120);
    swDir = 1;
    serialReply(swHalf > 0 ? "ok качание ±" + String(swHalf, 0) + "° " + String(swRpm, 0) + " об/мин"
                           : "ok качание стоп");
  }
  else if (cmd == "cur") {
    int ma = (int)a1;
    if (ma >= 100 && ma <= 900) { curMA = ma; drv.rms_current(curMA); serialReply("ok ток " + String(curMA) + " мА"); }
    else serialReply("err нужно 100..900");
  }
  else if (cmd == "mmrev") {
    if (a1 >= 10 && a1 <= 300) { MM_PER_REV = a1; hasL = hasR = false; serialReply("ok " + String(a1, 1) + " мм/об, края заново"); }
    else serialReply("err 10..300");
  }
  else if (cmd == "markl") { hasL = true; valL = posMM; serialReply("ok левый = " + String(valL, 1)); }
  else if (cmd == "markr") { hasR = true; valR = posMM; serialReply("ok правый = " + String(valR, 1)); }
  else if (cmd == "center") {
    demoOn = false;
    if (!(hasL && hasR)) serialReply("err сначала отметь края");
    else { moveClamped((valL + valR) / 2 - posMM + 0.001, 15); serialReply("ok центр"); }
  }
  else if (cmd == "demo") {
    if (!(hasL && hasR)) serialReply("err сначала отметь края");
    else { demoOn = a1 != 0; demoNextAt = millis() + 500; serialReply(demoOn ? "ok тренажёр" : "ok тренажёр стоп"); }
  }
  else if (cmd == "zero") { posDeg = 0; posMM = 0; hasL = hasR = false; serialReply("ok ноль здесь"); }
  else if (cmd == "mode") {                    // mode 1 = SpreadCycle (сила), 0 = StealthChop (тихо)
    drv.en_spreadCycle(a1 != 0);
    serialReply(a1 != 0 ? "ok SpreadCycle (сила)" : "ok StealthChop (тихо)");
  }
  else serialReply("err ? " + cmd);
}

void pollSerial() {
  while (Serial.available()) {
    char c = (char)Serial.read();
    if (c == '\n' || c == '\r') {
      if (rxBuf.length()) { execCmd(rxBuf); rxBuf = ""; }
    } else if (rxBuf.length() < 120) rxBuf += c;
  }
}

const char PAGE[] PROGMEM = R"html(
<!DOCTYPE html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Тренажёр</title><style>
body{font-family:sans-serif;max-width:440px;margin:16px auto;text-align:center}
button{font-size:20px;padding:12px 10px;margin:5px;border-radius:12px;border:1px solid #999;min-width:84px}
.big{font-size:28px;min-width:110px}
.edge{background:#ffe8cc}
.go{background:#d7f5d7;font-size:24px;min-width:200px}
.stop{background:#ffd7d7}
.row{margin:8px 0}
select{font-size:18px;padding:6px}
#st{color:#444;margin-top:12px;min-height:24px}
</style></head><body>
<h2>🎸 Тренажёр — канал 1</h2>
<div class="row">Шаг:
<select id="mm"><option>1</option><option>2</option><option selected>5</option><option>10</option><option>20</option></select> мм
&nbsp; Скорость:
<select id="v"><option>5</option><option selected>10</option><option>20</option><option>40</option></select> мм/с
</div>
<div class="row">
<button class="big" onclick="go(-1)">⬅</button>
<button class="big" onclick="go(1)">➡</button>
</div>
<div class="row">
<button class="edge" onclick="cmd('/markl')">📍 Это ЛЕВЫЙ край</button>
<button class="edge" onclick="cmd('/markr')">📍 Это ПРАВЫЙ край</button>
</div>
<div class="row">
<button class="go" onclick="cmd('/demo?on=1')">▶ Запустить тренажёр</button>
<button class="stop" onclick="cmd('/stop')">⏹ Стоп</button>
</div>
<div class="row">
<button onclick="cmd('/center')">🎯 В центр</button>
<button onclick="cmd('/free')">🖐 Отпустить</button>
<button onclick="cmd('/hold')">✊ Держать</button>
</div>
<div class="row">Ток:
<select id="cur" onchange="cmd('/cur?ma='+this.value)">
<option>200</option><option selected>350</option><option>500</option><option>700</option>
</select> мА
&nbsp; Привод:
<select id="drv" onchange="cmd('/mmrev?v='+this.value)">
<option value="171.2" selected>диск Ø54</option>
<option value="86.4">диск Ø27</option>
<option value="29.8">барабан</option>
</select>
</div>
<div id="st">...</div>
<script>
function cmd(u){return fetch(u).then(r=>r.text()).then(t=>st.innerText=t)}
function go(s){const mm=s*document.getElementById('mm').value;
const v=document.getElementById('v').value;
cmd('/move?mm='+mm+'&v='+v)}
setInterval(()=>{fetch('/status').then(r=>r.text()).then(t=>st.innerText=t).catch(()=>{})},1200)
</script></body></html>)html";

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  pinMode(PIN_STEP, OUTPUT); pinMode(PIN_DIR, OUTPUT); pinMode(PIN_EN, OUTPUT);
  digitalWrite(PIN_EN, HIGH);

  // WiFi не блокирует USB: ждём сеть максимум 8 секунд и живём дальше
  WiFi.mode(WIFI_STA);
  WiFi.setHostname("gitar-esp32");
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  uint32_t t0 = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - t0 < 8000) {
    digitalWrite(LED_PIN, !digitalRead(LED_PIN)); delay(200);
  }
  digitalWrite(LED_PIN, WiFi.status() == WL_CONNECTED ? HIGH : LOW);
  Serial.print("IP: "); Serial.println(WiFi.localIP());

  ArduinoOTA.setHostname("gitar-esp32");
  ArduinoOTA.begin();

  tmcSetup();

  server.on("/", []() { server.send_P(200, "text/html", PAGE); });
  server.on("/status", []() { server.send(200, "text/plain; charset=utf-8", statusStr()); });
  server.on("/cur", []() {
    int ma = server.arg("ma").toInt();
    if (ma >= 100 && ma <= 900) {
      curMA = ma; drv.rms_current(curMA);
      server.send(200, "text/plain; charset=utf-8", String("ток ") + curMA + " мА");
    } else server.send(200, "text/plain; charset=utf-8", "нужно 100..900");
  });
  server.on("/move", []() {
    demoOn = false;
    float mm = server.arg("mm").toFloat();
    float v  = server.arg("v").toFloat();
    if (v < 1) v = 10;
    server.send(200, "text/plain; charset=utf-8", "едем...");
    moveClamped(mm, v);
  });
  server.on("/mmrev", []() {                    // смена привода: мм на оборот
    float v = server.arg("v").toFloat();
    if (v >= 10 && v <= 300) {
      MM_PER_REV = v;
      hasL = hasR = false;                      // края калибровать заново!
      server.send(200, "text/plain; charset=utf-8",
                  "привод " + String(v, 1) + " мм/об — отметь края заново");
    } else server.send(200, "text/plain; charset=utf-8", "10..300");
  });
  server.on("/markl", []() {
    hasL = true; valL = posMM;
    server.send(200, "text/plain; charset=utf-8", "левый край = " + String(valL, 1) + " мм");
  });
  server.on("/markr", []() {
    hasR = true; valR = posMM;
    server.send(200, "text/plain; charset=utf-8", "правый край = " + String(valR, 1) + " мм");
  });
  server.on("/center", []() {
    demoOn = false;
    if (!(hasL && hasR)) { server.send(200, "text/plain; charset=utf-8", "сначала отметь оба края"); return; }
    server.send(200, "text/plain; charset=utf-8", "в центр");
    moveClamped((valL + valR) / 2 - posMM + 0.001, 15);
  });
  server.on("/demo", []() {
    if (!(hasL && hasR)) { server.send(200, "text/plain; charset=utf-8", "сначала отметь оба края!"); return; }
    demoOn = server.arg("on").toInt() != 0;
    demoNextAt = millis() + 500;
    server.send(200, "text/plain; charset=utf-8", demoOn ? "тренажёр запущен" : "тренажёр остановлен");
  });
  server.on("/stop", []() {
    demoOn = false; swHalf = 0; abortMove = true;
    server.send(200, "text/plain; charset=utf-8", "стоп");
  });
  server.on("/free", []() {
    demoOn = false; swHalf = 0; digitalWrite(PIN_EN, HIGH);
    server.send(200, "text/plain; charset=utf-8", "мотор отпущен (позиция может сбиться!)");
  });
  server.on("/hold", []() {
    digitalWrite(PIN_EN, LOW);
    server.send(200, "text/plain; charset=utf-8", "мотор держит");
  });
  server.begin();
  serialReply("ok gitar-esp32 v2 готов (команды: status/move/deg/sw/stop/...)");
}

void loop() {
  server.handleClient();
  ArduinoOTA.handle();
  pollSerial();
  if (demoOn && millis() > demoNextAt) {
    float lo = min(valL, valR) + EDGE_GAP, hi = max(valL, valR) - EDGE_GAP;
    float tgt = lo + (hi - lo) * (esp_random() % 1000) / 1000.0;
    float v = 10 + esp_random() % 25;             // 10..35 мм/с
    doMove(tgt - posMM, v);
    demoNextAt = millis() + 250 + esp_random() % 700;  // пауза 0.25..0.95 с
  }
  if (swHalf > 0) {                                // КАЧАНИЕ стенда:
    float target = swDir * swHalf;                 // махи к ±полууглу от нуля
    doDeg(target - posDeg, swRpm);                 // (сделай zero в нейтрали!)
    swDir = -swDir;
  }
}
