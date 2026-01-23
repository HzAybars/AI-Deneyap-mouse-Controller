import tkinter as tk
from tkinter import simpledialog, messagebox
from PIL import Image, ImageTk
import cv2
import mediapipe as mp
import numpy as np
import win32api, win32con
import time
import math
import threading
from queue import Queue

# ==========================================
#        AYARLAR (CONFIG)
# ==========================================
class Config:
    FRAME_W, FRAME_H = 640, 480
    SCREEN_W = win32api.GetSystemMetrics(0)
    SCREEN_H = win32api.GetSystemMetrics(1)
    
    # Hareket Alanı
    PAD_X, PAD_Y = 80, 60
    
    # Hassasiyet
    SMOOTHING = 5
    JITTER_THRESH = 2.0
    CLICK_RATIO = 0.23
    
    # GUI Renkleri
    BG_COLOR = "#2c3e50"
    BTN_COLOR = "#e74c3c"
    TXT_COLOR = "#ecf0f1"

# ==========================================
#      THREADED KAMERA İŞLEYİCİ
# ==========================================
class CameraStream:
    """
    Her kamera için ayrı bir thread (iş parçacığı) çalıştırır.
    Bu sayede bir kamera yavaşlasa bile ana program donmaz.
    """
    def __init__(self, url, cam_id):
        self.url = url
        self.id = cam_id
        self.cap = cv2.VideoCapture(url)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.running = True
        self.latest_frame = None
        self.lock = threading.Lock()
        
        # Arka planda okumayı başlat
        self.thread = threading.Thread(target=self.update, daemon=True)
        self.thread.start()

    def update(self):
        while self.running:
            if self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret:
                    with self.lock:
                        # İşlemciyi yormamak için aynalama ve boyutlandırmayı burada yapmıyoruz
                        # Sadece ham veriyi alıyoruz.
                        self.latest_frame = frame
                else:
                    # Bağlantı koptuysa yeniden dene
                    self.cap.release()
                    time.sleep(1)
                    self.cap = cv2.VideoCapture(self.url)
            else:
                time.sleep(1)

    def get_frame(self):
        with self.lock:
            return self.latest_frame

    def stop(self):
        self.running = False
        self.cap.release()

# ==========================================
#      AI & MOUSE MOTORU
# ==========================================
class AIEngine:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7,
            model_complexity=0 # Performans için en hafif model
        )
        self.mouse_ctrl = MouseController()
        
    def process_fusion(self, cameras):
        """
        Tüm kameralardan gelen görüntüleri işler ve koordinatları birleştirir.
        """
        x_list, y_list = [], []
        click_cmds, drag_cmds = [], []
        debug_frames = []

        for cam in cameras:
            raw_frame = cam.get_frame()
            if raw_frame is None: continue

            # Görüntüyü hazırla
            frame = cv2.flip(raw_frame, 1)
            imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # MediaPipe İşlemesi
            results = self.hands.process(imgRGB)
            
            if results.multi_hand_landmarks:
                lms = results.multi_hand_landmarks[0]
                h, w, c = frame.shape
                
                # Koordinatları al
                lm_pts = [(int(l.x * w), int(l.y * h)) for l in lms.landmark]
                
                # Mouse Pozisyonunu Hesapla (Interpolasyon)
                idx_x, idx_y = lm_pts[8] # İşaret parmağı ucu
                
                screen_x = np.interp(idx_x, (Config.PAD_X, w - Config.PAD_X), (0, Config.SCREEN_W))
                screen_y = np.interp(idx_y, (Config.PAD_Y, h - Config.PAD_Y), (0, Config.SCREEN_H))
                
                x_list.append(screen_x)
                y_list.append(screen_y)

                # Hareket Mantığı (Tıklama/Sürükleme)
                scale = math.hypot(lm_pts[9][0]-lm_pts[0][0], lm_pts[9][1]-lm_pts[0][1])
                dist_click = math.hypot(lm_pts[4][0]-lm_pts[8][0], lm_pts[4][1]-lm_pts[8][1])
                
                # Sürükleme (Yumruk kontrolü - Basit)
                is_fist = dist_click < scale * 0.2 and \
                          math.hypot(lm_pts[12][0]-lm_pts[0][0], lm_pts[12][1]-lm_pts[0][1]) < scale * 0.8
                
                drag_cmds.append(is_fist)
                
                if not is_fist and dist_click < scale * Config.CLICK_RATIO:
                    click_cmds.append('left')

                # Debug için çizim
                cv2.circle(frame, (idx_x, idx_y), 10, (0, 255, 0), -1)

            # Önizleme için resmi küçült
            small_frame = cv2.resize(frame, (320, 240))
            cv2.putText(small_frame, f"CAM {cam.id}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)
            debug_frames.append(small_frame)

        # KARAR MEKANİZMASI (FÜZYON)
        if x_list:
            avg_x = sum(x_list) / len(x_list)
            avg_y = sum(y_list) / len(y_list)
            self.mouse_ctrl.move(avg_x, avg_y)
            
            if 'left' in click_cmds: self.mouse_ctrl.click()
            self.mouse_ctrl.drag(any(drag_cmds))
        else:
            self.mouse_ctrl.drag(False)

        return debug_frames

class MouseController:
    def __init__(self):
        self.px, self.py = 0, 0
        self.last_click = 0
        self.dragging = False

    def move(self, x, y):
        dist = math.hypot(x - self.px, y - self.py)
        if dist < Config.JITTER_THRESH: return
        
        nx = self.px + (x - self.px) / Config.SMOOTHING
        ny = self.py + (y - self.py) / Config.SMOOTHING
        
        win32api.SetCursorPos((int(nx), int(ny)))
        self.px, self.py = nx, ny

    def click(self):
        if time.time() - self.last_click > 0.3:
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0)
            self.last_click = time.time()

    def drag(self, active):
        if active and not self.dragging:
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0)
            self.dragging = True
        elif not active and self.dragging:
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0)
            self.dragging = False

# ==========================================
#           GRAFİK ARAYÜZ (GUI)
# ==========================================
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Hz.Aybars Multi-Cam AI Mouse Panel")
        self.root.geometry("1000x700")
        self.root.configure(bg=Config.BG_COLOR)

        self.cameras = [] # Aktif kamera nesneleri
        self.ai_engine = AIEngine()
        self.is_running = False

        self._setup_ui()
        
    def _setup_ui(self):
        # Üst Panel (Kontroller)
        control_frame = tk.Frame(self.root, bg=Config.BG_COLOR)
        control_frame.pack(pady=10, fill=tk.X)

        tk.Label(control_frame, text="Kamera IP Adresi:", bg=Config.BG_COLOR, fg=Config.TXT_COLOR).pack(side=tk.LEFT, padx=10)
        
        self.ip_entry = tk.Entry(control_frame, width=30)
        self.ip_entry.insert(0, "http://192.168.1.35/stream")
        self.ip_entry.pack(side=tk.LEFT, padx=5)

        add_btn = tk.Button(control_frame, text="+ KAMERA EKLE", bg="#27ae60", fg="white", command=self.add_camera)
        add_btn.pack(side=tk.LEFT, padx=10)

        self.start_btn = tk.Button(control_frame, text="SİSTEMİ BAŞLAT", bg=Config.BTN_COLOR, fg="white", command=self.toggle_system)
        self.start_btn.pack(side=tk.RIGHT, padx=20)

        # Kamera Listesi Paneli
        self.list_frame = tk.LabelFrame(self.root, text="Aktif Kameralar", bg=Config.BG_COLOR, fg=Config.TXT_COLOR)
        self.list_frame.pack(pady=5, padx=10, fill=tk.X)
        self.lbl_status = tk.Label(self.list_frame, text="Henüz kamera eklenmedi.", bg=Config.BG_COLOR, fg="#95a5a6")
        self.lbl_status.pack()

        # Önizleme Alanı
        self.preview_canvas = tk.Label(self.root, bg="black")
        self.preview_canvas.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

    def add_camera(self):
        url = self.ip_entry.get()
        if not url.startswith("http"):
            messagebox.showerror("Hata", "Geçerli bir IP adresi girin (http:// ile başlamalı)")
            return
            
        cam_id = len(self.cameras) + 1
        new_cam = CameraStream(url, cam_id)
        self.cameras.append(new_cam)
        
        self.update_camera_list_ui()
        messagebox.showinfo("Başarılı", f"Kamera {cam_id} eklendi!")

    def update_camera_list_ui(self):
        # Listeyi temizle ve yeniden yaz
        for widget in self.list_frame.winfo_children():
            widget.destroy()
            
        if not self.cameras:
            tk.Label(self.list_frame, text="Kamera yok.", bg=Config.BG_COLOR, fg="#95a5a6").pack()
            return

        for cam in self.cameras:
            status = "Aktif" if cam.cap.isOpened() else "Bağlantı Yok"
            txt = f"KAMERA {cam.id} | {cam.url} | Durum: {status}"
            tk.Label(self.list_frame, text=txt, bg=Config.BG_COLOR, fg=Config.TXT_COLOR, font=("Arial", 10, "bold")).pack(anchor="w", padx=10)

    def toggle_system(self):
        if not self.is_running:
            if not self.cameras:
                messagebox.showwarning("Uyarı", "Lütfen önce en az bir kamera ekleyin.")
                return
            self.is_running = True
            self.start_btn.config(text="SİSTEMİ DURDUR", bg="#c0392b")
            self.loop()
        else:
            self.is_running = False
            self.start_btn.config(text="SİSTEMİ BAŞLAT", bg="#27ae60")

    def loop(self):
        if not self.is_running: return

        # AI Motorunu Çalıştır
        debug_imgs = self.ai_engine.process_fusion(self.cameras)

        # Önizleme Görüntülerini Birleştir ve Göster
        if debug_imgs:
            # Görüntüleri yan yana diz (numpy hstack)
            combined = np.hstack(debug_imgs)
            
            # Tkinter uyumlu formata çevir
            combined = cv2.cvtColor(combined, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(combined)
            img_tk = ImageTk.PhotoImage(image=img_pil)
            
            self.preview_canvas.config(image=img_tk)
            self.preview_canvas.image = img_tk # Garbage collection engellemek için referans tut

        # Döngüyü tekrarla (10ms sonra)
        self.root.after(10, self.loop)

    def on_close(self):
        self.is_running = False
        for cam in self.cameras:
            cam.stop()
        self.root.destroy()

# ==========================================
#               BAŞLATMA
# ==========================================
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()