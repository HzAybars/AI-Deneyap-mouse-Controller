# Hz.Aybars AI-Deneyap-mouse-Controller

![Python](https://img.shields.io/badge/Python-3.9%2B-blue) ![OpenCV](https://img.shields.io/badge/Computer_Vision-OpenCV-green) ![MediaPipe](https://img.shields.io/badge/AI-MediaPipe-orange) ![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)

**AI Mouse**, standart web kameralarını ve **Deneyap Kart (ESP32)** modüllerini kullanarak bilgisayarınızı el hareketleriyle yönetmenizi sağlayan gelişmiş bir sanal fare projesidir. 

Bu projenin en büyük farkı **Multi-Camera Fusion (Çoklu Kamera Füzyonu)** teknolojisidir. Birden fazla kamera farklı açılardan eli izler, veriler birleştirilir ve kör noktalar ortadan kaldırılarak kesintisiz bir fare deneyimi sunulur.

## Ozellikler

* **Coklu Kamera Destegi:** Istenildigi kadar Deneyap Kart (IP Kamera) sisteme eklenebilir.
* **Veri Fuzyonu:** Farkli kameralardan gelen koordinatlar birlestirilerek titreme (jitter) en aza indirilir.
* **Akilli Wi-Fi (WiFiManager):** Deneyap Kartlar acilista ag bulamazsa kendi agini kurar; kod icine sifre gommeye gerek kalmaz.
* **Dinamik Derinlik Algisi:** Elin kameraya olan uzakligina gore tiklama hassasiyeti otomatik ayarlanir.
* **Kullanici Arayuzu (GUI):** Kameralari yonetmek icin modern bir kontrol paneli.
* **Hareketler:**
    * **Isaret Parmagi:** Imlec hareketi.
    * **Isaret + Basparmak:** Sol Tik.
    * **Orta + Basparmak:** Sag Tik.
    * **Yumruk:** Surukle ve Birak (Drag & Drop).

## Donanim Gereksinimleri

* **Ana Bilgisayar:** Python calistirabilen Windows PC.
* **Kamera Dugumleri:** Deneyap Kart, ESP32-CAM veya benzeri ESP32 tabanli kartlar.
* **Kamera Modulu:** OV2640.

## Kurulum

Proje iki ana bolumden olusur: PC Yazilimi ve Deneyap Kart Yazilimi.

###  PC Tarafi (Python)

1.  Repoyu klonlayin veya indirin.
2.  Gerekli kutuphaneleri yukleyin:
    ```bash
    pip install -r requirements.txt
    ```
3.  Uygulamayi baslatin:
    ```bash
    python main.py
    ```

###  Deneyap Kart Tarafi (Arduino IDE)

1.  `deneyapyazilim` klasorundeki kodu Arduino IDE ile acin.
2.  Kutuphane Yoneticisinden **"WiFiManager"** (by tzapu) kutuphanesini yukleyin.
3.  Kart ayarlarinda "Partition Scheme" -> **"Huge APP"** secenegini isaretleyin.
4.  Kodu karta yukleyin.

## Kullanim

1.  **Kart Kurulumu:** Deneyap Kart'a guc verin. Ilk acilista `Deneyap_Mouse_Kurulum` isimli bir Wi-Fi agi yayacaktir. Telefonla baglanip ev/okul aginizi secin.
2.  **IP Adresi:** Kart aga baglandiginda Seri Port ekraninda bir IP adresi verecektir (Orn: `http://192.168.1.45/stream`).
3.  **PC Baglantisi:** Bilgisayarda `main.py` calistirin.
4.  Arayuzdeki kutuya IP adresini girin ve **"+ KAMERA EKLE"** butonuna basin.
5.  **"SISTEMI BASLAT"** diyerek kontrolu elinize alin!


MIT License

Copyright (c) 2026 HzAybars

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
