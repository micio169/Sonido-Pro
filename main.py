import sys
import threading
import time
import queue
import os
import json
import subprocess
from datetime import datetime
import numpy as np
import sounddevice as sd
import soundfile as sf
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QStyle, 
                             QDialog, QComboBox, QLineEdit, QFileDialog, 
                             QListWidget, QSplitter)
from PyQt6.QtCore import Qt, QTimer, QUrl
from PyQt6.QtGui import QFont, QPainter, QColor, QPen
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

# 테마 스타일 정의
THEMES = {
    "Cyberpunk": {
        "bg": "#121214", "panel": "#1a1a1e", "btn": "#252529", "btn_hover": "#2f2f35",
        "text": "#ffffff", "accent": "#00ffcc", "accent_rgb": (0, 255, 204), "record": "#ff3366"
    },
    "Slate Gray": {
        "bg": "#2c3e50", "panel": "#34495e", "btn": "#7f8c8d", "btn_hover": "#95a5a6",
        "text": "#ecf0f1", "accent": "#3498db", "accent_rgb": (52, 152, 219), "record": "#e74c3c"
    },
    "Obsidian Black": {
        "bg": "#070708", "panel": "#111112", "btn": "#1c1c1e", "btn_hover": "#2c2c2e",
        "text": "#e5e5ea", "accent": "#e67e22", "accent_rgb": (230, 126, 34), "record": "#d35400"
    }
}

# 다국어 팩
LANGUAGES = {
    "한국어": {
        "title": "Sonido Pro", "ready": "녹음 준비 완료", "recording": "녹음 중...",
        "paused": "일시 정지됨", "saving": "파일 저장 중...", "saved": "저장 완료!",
        "start_btn": " 녹음", "pause_btn": " 일시정지", "resume_btn": " 재개", "stop_btn": " 정지 및 저장",
        "settings_btn": " 설정", "open_folder": "폴더 열기", "history_title": "최근 녹음 기록 (더블클릭 재생)",
        "settings_title": "상세 설정", "lang_label": "언어 (Language):", "path_label": "저장 폴더 경로:",
        "device_label": "입력 마이크 장치:", "theme_label": "UI 테마 스타일:", "rate_label": "샘플 레이트 (음질):",
        "browse_btn": "찾아보기", "apply_btn": "적용", "cancel_btn": "취소", "playing": "재생 중..."
    },
    "English": {
        "title": "Sonido Pro", "ready": "Ready to Record", "recording": "Recording...",
        "paused": "Paused", "saving": "Saving file...", "saved": "Saved successfully!",
        "start_btn": " Record", "pause_btn": " Pause", "resume_btn": " Resume", "stop_btn": " Stop & Save",
        "settings_btn": " Settings", "open_folder": "Open Folder", "history_title": "Recent History (Double-Click to Play)",
        "settings_title": "Advanced Settings", "lang_label": "Language:", "path_label": "Save Directory:",
        "device_label": "Input Microphone:", "theme_label": "UI Theme:", "rate_label": "Sample Rate:",
        "browse_btn": "Browse", "apply_btn": "Apply", "cancel_btn": "Cancel", "playing": "Playing..."
    },
    "Español": {
        "title": "Sonido Pro", "ready": "Listo para grabar", "recording": "Grabando...",
        "paused": "Pausado", "saving": "Guardando...", "saved": "¡Guardado con éxito!",
        "start_btn": " Grabar", "pause_btn": " Pausar", "resume_btn": " Reanudar", "stop_btn": " Detener",
        "settings_btn": " Ajustes", "open_folder": "Abrir Carpeta", "history_title": "Historial Reciente (Doble clic)",
        "settings_title": "Ajustes Avanzados", "lang_label": "Idioma:", "path_label": "Carpeta de guardado:",
        "device_label": "Micrófono de entrada:", "theme_label": "Tema de UI:", "rate_label": "Frecuencia de muestreo:",
        "browse_btn": "Buscar", "apply_btn": "Aplicar", "cancel_btn": "Cancelar", "playing": "Reproduciendo..."
    }
}

class VisualizerWidget(QWidget):
    """실시간 오디오 파형을 그리는 커스텀 위젯"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.points = np.zeros(100)
        self.theme = THEMES["Cyberpunk"]
        self.setMinimumHeight(60)

    def set_theme(self, theme_data):
        self.theme = theme_data
        self.update()

    def update_samples(self, data):
        if len(data) > 0:
            # 절대값 평균을 내어 파형 세기 추출 후 다운샘플링
            mono_data = np.abs(data[:, 0])
            chunks = np.array_split(mono_data, 100)
            self.points = np.array([np.mean(c) for c in chunks])
            # 민감도 스케일링
            self.points = np.clip(self.points * 5, 0, 1)
        else:
            self.points = np.zeros(100)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 배경 그리기
        painter.fillRect(self.rect(), QColor(self.theme["panel"]))
        
        # 파형 선 그리기
        width = self.width()
        height = self.height()
        mid_y = height // 2
        
        r, g, b = self.theme["accent_rgb"]
        pen = QPen(QColor(r, g, b), 2)
        painter.setPen(pen)
        
        step = width / 100
        for i in range(99):
            x1 = i * step
            y1 = mid_y + (self.points[i] * mid_y * 0.8)
            x2 = (i + 1) * step
            y2 = mid_y + (self.points[i+1] * mid_y * 0.8)
            
            # 대칭형 파형 그리기
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))
            painter.drawLine(int(x1), int(mid_y - (self.points[i] * mid_y * 0.8)), int(x2), int(mid_y - (self.points[i+1] * mid_y * 0.8)))


class SettingsDialog(QDialog):
    """모든 확장 커스텀 기능이 취합된 설정 창"""
    def __init__(self, parent, current_config):
        super().__init__(parent)
        self.config = current_config
        self.initUI()
        
    def initUI(self):
        lang_set = LANGUAGES[self.config["lang"]]
        theme_set = THEMES[self.config["theme"]]
        
        self.setWindowTitle(lang_set["settings_title"])
        self.setFixedSize(500, 360)
        self.setStyleSheet(f"""
            QDialog {{ background-color: {theme_set['bg']}; }}
            QLabel {{ color: {theme_set['text']}; font-size: 13px; }}
            QPushButton {{ 
                background-color: {theme_set['btn']}; color: {theme_set['text']}; 
                border-radius: 5px; padding: 6px 12px; border: 1px solid #444;
            }}
            QPushButton:hover {{ background-color: {theme_set['btn_hover']}; }}
            QComboBox, QLineEdit {{ 
                background-color: {theme_set['panel']}; color: {theme_set['text']}; 
                border: 1px solid #555; padding: 5px; border-radius: 4px;
            }}
        """)
        
        layout = QVBoxLayout(self)
        
        # 1. 언어 선택
        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel(lang_set["lang_label"]))
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(list(LANGUAGES.keys()))
        self.lang_combo.setCurrentText(self.config["lang"])
        lang_layout.addWidget(self.lang_combo)
        layout.addLayout(lang_layout)
        
        # 2. 테마 선택
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel(lang_set["theme_label"]))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(list(THEMES.keys()))
        self.theme_combo.setCurrentText(self.config["theme"])
        theme_layout.addWidget(self.theme_combo)
        layout.addLayout(theme_layout)

        # 3. 마이크 선택
        dev_layout = QHBoxLayout()
        dev_layout.addWidget(QLabel(lang_set["device_label"]))
        self.dev_combo = QComboBox()
        
        # 시스템 사운드 장치 파싱
        self.devices = sd.query_devices()
        self.input_device_indices = []
        default_idx = sd.query_devices(kind='input').get('index', 0)
        
        select_idx = 0
        for i, dev in enumerate(self.devices):
            if dev['max_input_channels'] > 0:
                self.dev_combo.addItem(f"{dev['name']}")
                self.input_device_indices.append(i)
                if i == self.config.get("device_index", default_idx):
                    select_idx = self.dev_combo.count() - 1
                    
        self.dev_combo.setCurrentIndex(select_idx)
        dev_layout.addWidget(self.dev_combo)
        layout.addLayout(dev_layout)

        # 4. 샘플레이트 음질 설정
        rate_layout = QHBoxLayout()
        rate_layout.addWidget(QLabel(lang_set["rate_label"]))
        self.rate_combo = QComboBox()
        self.rate_combo.addItems(["44100", "48000", "96000"])
        self.rate_combo.setCurrentText(str(self.config["rate"]))
        rate_layout.addWidget(self.rate_combo)
        layout.addLayout(rate_layout)
        
        # 5. 경로 설정
        layout.addWidget(QLabel(lang_set["path_label"]))
        path_layout = QHBoxLayout()
        self.path_input = QLineEdit(self.config["save_dir"])
        self.browse_btn = QPushButton(lang_set["browse_btn"])
        self.browse_btn.clicked.connect(self.browse_folder)
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(self.browse_btn)
        layout.addLayout(path_layout)
        
        layout.addSpacing(20)
        
        # 하단 제어 단추
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.apply_btn = QPushButton(lang_set["apply_btn"])
        self.apply_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton(lang_set["cancel_btn"])
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.apply_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Directory", self.path_input.text())
        if folder:
            self.path_input.setText(os.path.normpath(folder))

    def get_selected_device_index(self):
        combo_idx = self.dev_combo.currentIndex()
        if combo_idx >= 0 and combo_idx < len(self.input_device_indices):
            return self.input_device_indices[combo_idx]
        return None


class AudioRecorder(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")
        
        # 오디오 및 레코딩 코어 상태 변수
        self.audio_queue = queue.Queue()
        self.is_recording = False
        self.is_paused = False
        self.recorded_chunks = []
        self.elapsed_paused_time = 0
        self.start_time = 0
        self.pause_start_time = 0
        
        # 재생 플레이어 컴포넌트 초기화
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(0.8) # 기본 볼륨 80%
        
        self.load_settings()
        self.initUI()
        self.update_ui_theme()
        self.update_ui_language()
        self.refresh_history_list()
        
        # 타이머 구성
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer_label)

    def load_settings(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        default_save_dir = os.path.join(current_dir, "save")
        
        try:
            default_device = sd.query_devices(kind='input').get('index', 0)
        except Exception:
            default_device = 0

        self.config = {
            "lang": "한국어",
            "theme": "Cyberpunk",
            "save_dir": default_save_dir,
            "rate": 44100,
            "device_index": default_device
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    self.config.update(saved)
            except Exception:
                pass
                
        os.makedirs(self.config["save_dir"], exist_ok=True)

    def save_settings(self):
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(self.config, f, ensure_ascii=False, indent=4)

    def initUI(self):
        self.setMinimumSize(700, 420)
        
        # 메인 가로 분할 뷰 레이아웃 구조 (메인 컨트롤러 vs 기록 히스토리 패널)
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(main_splitter)
        
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # 1. 탑 바 (설정 및 폴더 열기)
        top_layout = QHBoxLayout()
        self.open_folder_btn = QPushButton()
        self.open_folder_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogOpenButton))
        self.open_folder_btn.clicked.connect(self.open_save_folder)
        self.open_folder_btn.setVisible(False) # 녹음 완료시에만 가변 팝업
        
        self.settings_btn = QPushButton()
        self.settings_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
        self.settings_btn.clicked.connect(self.open_settings)
        
        top_layout.addWidget(self.open_folder_btn)
        top_layout.addStretch()
        top_layout.addWidget(self.settings_btn)
        left_layout.addLayout(top_layout)
        
        # 2. 메인 표시계 정보창
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        
        self.time_label = QLabel("00:00:00")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setFont(QFont("Arial", 42, QFont.Weight.Bold))
        
        left_layout.addWidget(self.status_label)
        left_layout.addSpacing(5)
        left_layout.addWidget(self.time_label)
        
        # 3. 실시간 파형 시각화 공간 배정
        self.visualizer = VisualizerWidget()
        left_layout.addWidget(self.visualizer)
        left_layout.addSpacing(10)
        
        # 4. 제어 조작 버튼 행 레이아웃
        btn_layout = QHBoxLayout()
        self.record_btn = QPushButton()
        self.record_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.record_btn.clicked.connect(self.start_recording)
        
        self.pause_btn = QPushButton()
        self.pause_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
        self.pause_btn.clicked.connect(self.toggle_pause)
        self.pause_btn.setEnabled(False)
        
        self.stop_btn = QPushButton()
        self.stop_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaStop))
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_recording)
        
        btn_layout.addWidget(self.record_btn)
        btn_layout.addWidget(self.pause_btn)
        btn_layout.addWidget(self.stop_btn)
        left_layout.addLayout(btn_layout)
        
        # 우측 히스토리 패널 세팅
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        self.history_title_label = QLabel()
        self.history_title_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.history_list = QListWidget()
        self.history_list.itemDoubleClicked.connect(self.play_history_file)
        
        right_layout.addWidget(self.history_title_label)
        right_layout.addWidget(self.history_list)
        
        # 스플리터에 장착
        main_splitter.addWidget(left_widget)
        main_splitter.addWidget(right_widget)
        main_splitter.setSizes([420, 280])

    def update_ui_theme(self):
        theme = THEMES[self.config["theme"]]
        self.visualizer.set_theme(theme)
        
        self.setStyleSheet(f"""
            QMainWindow, QSplitter {{ background-color: {theme['bg']}; }}
            QLabel {{ color: {theme['text']}; }}
            QListWidget {{ 
                background-color: {theme['panel']}; color: {theme['text']}; 
                border: 1px solid {theme['btn']}; border-radius: 6px; font-size: 12px;
            }}
            QListWidget::item:hover {{ background-color: {theme['btn']}; }}
            QListWidget::item:selected {{ background-color: {theme['accent']}; color: #000; font-weight: bold; }}
            QPushButton {{ 
                background-color: {theme['btn']}; color: {theme['text']}; 
                border-radius: 8px; border: 1px solid #3d3d3d; font-size: 13px; padding: 10px;
            }}
            QPushButton:hover {{ background-color: {theme['btn_hover']}; }}
            QPushButton:disabled {{ background-color: {theme['bg']}; color: #555; border-color: #222; }}
        """)
        self.time_label.setStyleSheet(f"color: {theme['accent']};")

    def update_ui_language(self):
        lang_set = LANGUAGES[self.config["lang"]]
        theme_set = THEMES[self.config["theme"]]
        
        self.setWindowTitle(lang_set["title"])
        self.history_title_label.setText(lang_set["history_title"])
        self.settings_btn.setText(lang_set["settings_btn"])
        self.open_folder_btn.setText(lang_set["open_folder"])
        
        if self.is_recording:
            if self.is_paused:
                self.status_label.setText(lang_set["paused"])
                self.status_label.setStyleSheet("color: #ffcc00;")
            else:
                self.status_label.setText(lang_set["recording"])
                self.status_label.setStyleSheet(f"color: {theme_set['record']};")
        else:
            self.status_label.setText(lang_set["ready"])
            self.status_label.setStyleSheet(f"color: {theme_set['text']};")
            
        self.record_btn.setText(lang_set["start_btn"])
        self.stop_btn.setText(lang_set["stop_btn"])
        
        if self.is_paused:
            self.pause_btn.setText(lang_set["resume_btn"])
            self.pause_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        else:
            self.pause_btn.setText(lang_set["pause_btn"])
            self.pause_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))

    def refresh_history_list(self):
        self.history_list.clear()
        if os.path.exists(self.config["save_dir"]):
            files = [f for f in os.listdir(self.config["save_dir"]) if f.endswith('.wav')]
            # 최신 파일이 위로 오도록 정렬
            files.sort(reverse=True)
            self.history_list.addItems(files)

    def open_settings(self):
        dialog = SettingsDialog(self, self.config)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.config["lang"] = dialog.lang_combo.currentText()
            self.config["theme"] = dialog.theme_combo.currentText()
            self.config["rate"] = int(dialog.rate_combo.currentText())
            
            dev_idx = dialog.get_selected_device_index()
            if dev_idx is len(dialog.input_device_indices) or dev_idx is not None:
                self.config["device_index"] = dev_idx
                
            self.config["save_dir"] = dialog.path_input.text()
            
            os.makedirs(self.config["save_dir"], exist_ok=True)
            self.save_settings()
            self.update_ui_theme()
            self.update_ui_language()
            self.refresh_history_list()

    def open_save_folder(self):
        if os.path.exists(self.config["save_dir"]):
            if sys.platform == 'win32':
                os.startfile(self.config["save_dir"])
            else:
                subprocess.Popen(['xdg-open', self.config["save_dir"]])

    def start_recording(self):
        self.is_recording = True
        self.is_paused = False
        self.audio_queue = queue.Queue()
        self.recorded_chunks = []
        self.elapsed_paused_time = 0
        self.start_time = time.time()
        
        # 입력 오디오 장치 채널 검증 하드웨어 감지
        try:
            dev_info = sd.query_devices(self.config["device_index"], 'input')
            max_ch = dev_info.get('max_input_channels', 1)
            self.channels = 2 if max_ch >= 2 else 1
        except Exception:
            self.channels = 1
            
        self.record_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)  # 데이터를 일정 부분 받을 때까지 잠금 후 해제 가능하나 편의상 즉시 켬
        self.stop_btn.setEnabled(True)
        self.settings_btn.setEnabled(False)
        self.open_folder_btn.setVisible(False)
        
        self.update_ui_language()
        self.timer.start(50) # 파형 업데이트 민감도를 위해 0.05초 단위 갱신
        
        self.record_thread = threading.Thread(target=self.record_loop)
        self.record_thread.start()

    def toggle_pause(self):
        if not self.is_recording:
            return
            
        if not self.is_paused:
            # 일시정지 상태 진입
            self.is_paused = True
            self.pause_start_time = time.time()
            self.visualizer.update_samples(np.zeros((0, 1)))
        else:
            # 녹음 재개
            self.is_paused = False
            self.elapsed_paused_time += (time.time() - self.pause_start_time)
            
        self.update_ui_language()

    def audio_callback(self, indata, frames, time_info, status):
        if status:
            print(status, file=sys.stderr)
        if self.is_recording and not self.is_paused:
            self.audio_queue.put(indata.copy())
            # 메인 스레드 비주얼라이저로 오디오 버퍼 전달
            self.visualizer.update_samples(indata)

    def record_loop(self):
        try:
            with sd.InputStream(samplerate=self.config["rate"], 
                                 channels=self.channels, 
                                 device=self.config["device_index"],
                                 callback=self.audio_callback):
                while self.is_recording:
                    sd.sleep(50)
        except Exception as e:
            print(f"Recording error: {e}")

    def stop_recording(self):
        self.is_recording = False
        self.is_paused = False
        self.timer.stop()
        
        if hasattr(self, 'record_thread'):
            self.record_thread.join()
            
        self.update_ui_language()
        self.visualizer.update_samples(np.zeros((0, 1)))
        
        # 데이터 큐 플러시
        while not self.audio_queue.empty():
            self.recorded_chunks.append(self.audio_queue.get())
            
        if self.recorded_chunks:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"rec_{timestamp}.wav"
            full_path = os.path.join(self.config["save_dir"], file_name)
            
            final_data = np.concatenate(self.recorded_chunks, axis=0)
            sf.write(full_path, final_data, self.config["rate"])
            
            lang_set = LANGUAGES[self.config["lang"]]
            self.status_label.setText(f"{lang_set['saved']} ({file_name})")
            self.open_folder_btn.setVisible(True) # 폴더 열기 바로가기 표출
            
        self.record_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.settings_btn.setEnabled(True)
        self.time_label.setText("00:00:00")
        self.refresh_history_list()

    def play_history_file(self, item):
        """기록 리스트에서 더블클릭된 wav 사운드 파일 재생"""
        file_path = os.path.join(self.config["save_dir"], item.text())
        if os.path.exists(file_path):
            lang_set = LANGUAGES[self.config["lang"]]
            self.status_label.setText(f"{lang_set['playing']} {item.text()}")
            self.status_label.setStyleSheet("color: #00ffcc;")
            
            self.player.setSource(QUrl.fromLocalFile(file_path))
            self.player.play()

    def update_timer_label(self):
        if self.is_recording:
            if self.is_paused:
                # 일시정지 상태에서는 시간이 누적 증가하지 않도록 고정 연산
                curr_elapsed = self.pause_start_time - self.start_time - self.elapsed_paused_time
            else:
                curr_elapsed = time.time() - self.start_time - self.elapsed_paused_time
                
            hours, rem = divmod(curr_elapsed, 3600)
            minutes, seconds = divmod(rem, 60)
            self.time_label.setText(f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}")

    def closeEvent(self, event):
        self.is_recording = False
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = AudioRecorder()
    ex.show()
    sys.exit(app.exec())