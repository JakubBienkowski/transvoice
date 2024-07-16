import sys
import json
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QProgressBar, QVBoxLayout, QWidget
from PyQt5.QtCore import QTimer, Qt
import speech_recognition as sr

class SignLanguageRecorder(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sign Language Recorder")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.sentence_label = QLabel("Ready to start", self)
        self.sentence_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.sentence_label)

        self.timer_label = QLabel("", self)
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.timer_label)

        self.progress_bar = QProgressBar(self)
        self.layout.addWidget(self.progress_bar)

        self.sentences = []
        self.current_sentence_index = 0
        self.repetitions = 3
        self.current_repetition = 0

        self.countdown_timer = QTimer(self)
        self.countdown_timer.timeout.connect(self.update_countdown)

        self.recording_timer = QTimer(self)
        self.recording_timer.timeout.connect(self.stop_recording)

        self.countdown_value = 5

        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

    def load_sentences(self, filename):
        with open(filename, 'r') as f:
            self.sentences = f.read().splitlines()
        self.progress_bar.setMaximum(len(self.sentences) * self.repetitions)

    def start_session(self):
        self.current_sentence_index = 0
        self.current_repetition = 0
        self.next_sentence()

    def next_sentence(self):
        if self.current_sentence_index < len(self.sentences):
            self.sentence_label.setText(self.sentences[self.current_sentence_index])
            self.start_countdown()
        else:
            self.sentence_label.setText("Session completed!")

    def start_countdown(self):
        self.countdown_value = 5
        self.update_countdown()
        self.countdown_timer.start(1000)

    def update_countdown(self):
        if self.countdown_value > 0:
            self.timer_label.setText(f"Recording in: {self.countdown_value}")
            self.countdown_value -= 1
        else:
            self.countdown_timer.stop()
            self.start_recording()

    def start_recording(self):
        self.timer_label.setText("Recording...")
        # Start capturing motion data here
        self.recording_timer.start(3000)  # Record for 3 seconds

    def stop_recording(self):
        self.recording_timer.stop()
        # Stop capturing motion data and save it
        self.save_recording()
        self.current_repetition += 1
        self.progress_bar.setValue(self.current_sentence_index * self.repetitions + self.current_repetition)

        if self.current_repetition < self.repetitions:
            self.start_countdown()
        else:
            self.current_sentence_index += 1
            self.current_repetition = 0
            self.next_sentence()

    def save_recording(self):
        # Placeholder for saving the recording
        filename = f"recording_{self.current_sentence_index}_{self.current_repetition}.json"
        data = {
            "sentence": self.sentences[self.current_sentence_index],
            "repetition": self.current_repetition,
            "motion_data": {}  # Add actual motion data here
        }
        with open(filename, 'w') as f:
            json.dump(data, f)

    def listen_for_commands(self):
        with self.microphone as source:
            audio = self.recognizer.listen(source)
        try:
            command = self.recognizer.recognize_google(audio).lower()
            if "start" in command:
                self.start_session()
            elif "pause" in command:
                # Implement pause functionality
                pass
            elif "resume" in command:
                # Implement resume functionality
                pass
            elif "stop" in command:
                # Implement stop functionality
                pass
        except sr.UnknownValueError:
            print("Could not understand audio")
        except sr.RequestError as e:
            print(f"Could not request results; {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    recorder = SignLanguageRecorder()
    recorder.show()
    sys.exit(app.exec_())