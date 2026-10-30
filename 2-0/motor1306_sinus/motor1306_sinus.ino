// Проба драйвера на моторе квадрокоптера 1306 3000KV без SimpleFOC: три синуса со сдвигом 120° на IN1/IN2/IN3 (ШИМ 20 кГц).
// Обмотки ~0.1–0.2 Ом — амплитуда всего ~0.54 В из 12 (ток ~3–4 А), и через 15 с EN (nSLEEP) LOW — драйвер спит, мотор не греется.
#define EN_PIN 14
#define LED_PIN 2
const int PINS[3] = {25, 26, 27};
const float AMP = 0.045;        // доля от 12 В: 0.54 В (30.10: на 0.36 дёргался)
const float F_EL = 10.0;        // Гц электрических ≈ 1.4 об/с

void setup() {
  Serial.begin(115200);
  pinMode(EN_PIN, OUTPUT);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(EN_PIN, HIGH);
  digitalWrite(LED_PIN, HIGH);
  for (int i = 0; i < 3; i++) ledcAttach(PINS[i], 20000, 10);
  Serial.println("motor1_sinus");
}

void loop() {
  if (millis() > 15000) {                               // 15 с — и спать
    digitalWrite(EN_PIN, LOW);
    digitalWrite(LED_PIN, LOW);
    return;
  }
  float th = millis() / 1000.0 * 2 * PI * F_EL;
  for (int i = 0; i < 3; i++) {
    float d = 0.5 + AMP * sin(th - i * 2 * PI / 3);      // 0.5 ± 0.3
    ledcWrite(PINS[i], (uint32_t)(d * 1023));
  }
  static unsigned long tp = 0;
  if (millis() - tp > 1000) { tp = millis(); Serial.println("sinus"); }
}
