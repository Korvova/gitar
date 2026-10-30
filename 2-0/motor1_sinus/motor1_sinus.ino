// Проба стенда 2204 без SimpleFOC: три синуса со сдвигом 120° прямо на IN1/IN2/IN3 (ШИМ 20 кГц), EN (nSLEEP) всегда HIGH.
// Амплитуда ~3.5 В из 12, ~0.4 об/с. Если так крутится, а с SimpleFOC нет — дело в библиотеке, не в плате.
#define EN_PIN 14
#define LED_PIN 2
const int PINS[3] = {25, 26, 27};
const float AMP = 0.3;          // доля от 12 В
const float F_EL = 3.0;         // Гц электрических = 3/7 об/с

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
  float th = millis() / 1000.0 * 2 * PI * F_EL;
  for (int i = 0; i < 3; i++) {
    float d = 0.5 + AMP * sin(th - i * 2 * PI / 3);      // 0.5 ± 0.3
    ledcWrite(PINS[i], (uint32_t)(d * 1023));
  }
  static unsigned long tp = 0;
  if (millis() - tp > 1000) { tp = millis(); Serial.println("sinus"); }
}
