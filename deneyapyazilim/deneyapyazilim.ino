/*
 * PROJE: Deneyap AI Mouse - Akıllı Kamera Düğümü
 * ÖZELLİK: WiFi Manager ile şifre girmeden ağa bağlanma.
 */

#include <WiFiManager.h> // Yüklemeniz gereken kütüphane: WiFiManager by tzapu
#include "esp_camera.h"

// --- Deneyap Kart Pin Tanımları ---
#define CAMD2  CAMD2
#define CAMD3  CAMD3
#define CAMD4  CAMD4
#define CAMD5  CAMD5
#define CAMD6  CAMD6
#define CAMD7  CAMD7
#define CAMD8  CAMD8
#define CAMD9  CAMD9
#define CAMXC  CAMXC
#define CAMPC  CAMPC
#define CAMV   CAMV
#define CAMH   CAMH
#define CAMSD  CAMSD
#define CAMSC  CAMSC

void startCameraServer();

void setup() {
  Serial.begin(115200);
  Serial.setDebugOutput(true);
  Serial.println();

  // 1. KAMERA YAPILANDIRMASI
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = CAMD2;
  config.pin_d1 = CAMD3;
  config.pin_d2 = CAMD4;
  config.pin_d3 = CAMD5;
  config.pin_d4 = CAMD6;
  config.pin_d5 = CAMD7;
  config.pin_d6 = CAMD8;
  config.pin_d7 = CAMD9;
  config.pin_xclk = CAMXC;
  config.pin_pclk = CAMPC;
  config.pin_vsync = CAMV;
  config.pin_href = CAMH;
  config.pin_sscb_sda = CAMSD;
  config.pin_sscb_scl = CAMSC;
  config.pin_pwdn = -1;
  config.pin_reset = -1;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  
  // Performans Ayarı: 
  // VGA (640x480) görüntü işleme için ideal dengedir.
  config.frame_size = FRAMESIZE_VGA; 
  config.jpeg_quality = 12; // Düşük sayı = Yüksek kalite
  config.fb_count = 1;

  // Kamera Başlat
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Kamera Başlatılamadı! Hata: 0x%x", err);
    return;
  }

  // 2. WIFI MANAGER (AKILLI BAĞLANTI)
  WiFiManager wifiManager;
  
  // Eğer önceden kayıtlı ağ yoksa veya bağlanamazsa
  // "Deneyap_Mouse_Kurulum" adında şifresiz bir ağ yayını yapar.
  // Bu ağa bağlanınca otomatik bir sayfa açılır ve evdeki Wi-Fi seçilir.
  bool res = wifiManager.autoConnect("Deneyap_Mouse_Kurulum");

  if(!res) {
      Serial.println("Bağlantı zaman aşımına uğradı, resetleniyor...");
      ESP.restart();
  } 
  
  // Buraya geldiyse Wi-Fi'ye bağlanmış demektir.
  Serial.println("\n--- BAĞLANTI BAŞARILI ---");
  Serial.print("Kartın IP Adresi: http://");
  Serial.print(WiFi.localIP());
  Serial.println("/stream");
  
  // Kamerayı sunucu moduna al
  startCameraServer();
  
  // Dahili LED varsa yansın (Hazır olduğunu belirtmek için)
  pinMode(LEDB, OUTPUT);
  digitalWrite(LEDB, LOW);
}

void loop() {
  // İşlemciyi meşgul etmemek için boş döngü
  delay(10000);
}