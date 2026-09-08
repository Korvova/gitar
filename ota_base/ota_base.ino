// Базовая OTA-прошивка для ESP32 DevKit (проект gitar)
// Первый раз заливается по USB, дальше — по Wi-Fi (ArduinoOTA, порт 3232)
// Светодиод GPIO2 мигает, показывая что плата жива и в сети

#include <WiFi.h>
#include <ArduinoOTA.h>

const char* WIFI_SSID = "MTS_GPON_BC14";
const char* WIFI_PASS = "444YYdc4";

#define LED_PIN 2

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);

  WiFi.mode(WIFI_STA);
  WiFi.setHostname("gitar-esp32");
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  Serial.print("WiFi connecting");
  while (WiFi.status() != WL_CONNECTED) {
    digitalWrite(LED_PIN, !digitalRead(LED_PIN)); // частое мигание = подключаемся
    Serial.print(".");
    delay(200);
  }
  Serial.println();
  Serial.print("Connected! IP: ");
  Serial.println(WiFi.localIP());

  ArduinoOTA.setHostname("gitar-esp32");
  ArduinoOTA.onStart([]() { Serial.println("OTA start"); });
  ArduinoOTA.onEnd([]()   { Serial.println("OTA done, reboot"); });
  ArduinoOTA.onError([](ota_error_t e) { Serial.printf("OTA error %u\n", e); });
  ArduinoOTA.begin();
  Serial.println("OTA ready (port 3232)");
}

void loop() {
  ArduinoOTA.handle();

  // медленное мигание = прошивка v3, залита по воздуху на плату от зарядки
  static uint32_t t = 0;
  if (millis() - t >= 1000) {
    t = millis();
    digitalWrite(LED_PIN, !digitalRead(LED_PIN));
  }
}
