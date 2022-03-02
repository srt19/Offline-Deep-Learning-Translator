import os
import sys
import gc
from PyQt6.QtCore import QSize, QObject, QThread, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
	QGridLayout, QLabel, QMessageBox, QPushButton, QPlainTextEdit, QComboBox, QWidget, QApplication, QMainWindow,
	QStatusBar, QTabWidget
)


class Worker(QObject):
	finished = pyqtSignal()

	def load_job(self):
		global lang
		global mname
		global tokenizer
		global model
		if lang_id == 8:
			from transformers import MBartForConditionalGeneration, MBartTokenizer
			tokenizer = MBartTokenizer.from_pretrained(mname, local_files_only=True)
			model = MBartForConditionalGeneration.from_pretrained(mname, local_files_only=True)
		else:
			from transformers import MarianTokenizer, MarianMTModel
			tokenizer = MarianTokenizer.from_pretrained(mname, local_files_only=True)
			model = MarianMTModel.from_pretrained(mname, local_files_only=True)
		self.finished.emit()

	def tl_job(self):
		global tokenizer
		global model
		global tl_output
		if lang_id == 8:
			inputs = tokenizer(tl_input, return_tensors="pt")
			translated_tokens = model.generate(**inputs, decoder_start_token_id=tokenizer.lang_code_to_id["en_XX"],
												early_stopping=True, max_length=48)
			tl_output = tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)[0]
		else:
			input_ids = tokenizer.encode(tl_input, return_tensors="pt")
			outputs = model.generate(input_ids)
			tl_output = tokenizer.decode(outputs[0], skip_special_tokens=True)
		self.finished.emit()


class MainWindow(QMainWindow):
	def __init__(self):
		super(MainWindow, self).__init__()

		self.setWindowTitle("Offline Translator")

		font = QFont()
		font.setPointSize(11)
		layout = QGridLayout()

		# Tab Etc.
		self.tab_widget = QWidget()
		self.tab_widget.setFont(font)
		self.setCentralWidget(self.tab_widget)
		self.tabs = QTabWidget()
		self.main_tab = QWidget()
		self.main_tab_layout = QGridLayout()
		self.dl_tab = QWidget()
		self.dl_tab_layout = QGridLayout()

		# Adding Tabs
		self.tabs.addTab(self.main_tab, "Translate")
		self.tabs.addTab(self.dl_tab, "Download Model")

		# Main Tab
		self.tl_button = QPushButton("Translate")
		self.tl_button.clicked.connect(self.tl_run)
		self.tl_button.setStatusTip("Click to start translation")
		self.tl_button.setEnabled(False)
		self.load_button = QPushButton("Load Model")
		self.load_button.clicked.connect(self.load_run)
		self.load_button.setStatusTip("Click to load model files")
		self.unload_button = QPushButton("Unload Model")
		self.unload_button.clicked.connect(self.unload_run)
		self.unload_button.setStatusTip("Click to unload model files")
		self.unload_button.setEnabled(False)
		self.in_text = QPlainTextEdit()
		self.in_text.setStatusTip("Type your text here")
		self.in_text.setMinimumSize(QSize(380, 430))
		self.out_text = QPlainTextEdit()
		self.out_text.setMinimumSize(QSize(380, 430))
		self.out_text.setStatusTip("Your text output goes here")
		# Languages List
		self.lang_list = QComboBox()
		self.lang_list.setStatusTip("Select the language model")
		global lang_id
		lang_id = 0
		self.lang_list.addItem("Japanese to English")
		self.lang_list.addItem("English to Japanese")
		self.lang_list.addItem("Chinese to English")
		self.lang_list.addItem("English to Chinese")
		self.lang_list.addItem("Indonesia to English")
		self.lang_list.addItem("English to Indonesia")
		self.lang_list.addItem("Vietnam to English")
		self.lang_list.addItem("English to Vietnam")
		self.lang_list.addItem("Japanese to English MBart")
		self.lang_list.currentIndexChanged.connect(self.lang_sel)
		self.in_label = QLabel("<b>Input Text</b>")
		self.in_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
		self.out_label = QLabel("<b>Output Text</b>")
		self.out_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)

		# Layout Settings
		self.main_tab_layout.addWidget(self.lang_list, 0, 0, 1, 2)
		self.main_tab_layout.addWidget(self.load_button, 2, 0, 1, 1)
		self.main_tab_layout.addWidget(self.unload_button, 2, 1, 1, 1)
		self.main_tab_layout.addWidget(self.tl_button, 3, 0, 1, 2)
		self.main_tab_layout.addWidget(self.in_label, 4, 0, 1, 1)
		self.main_tab_layout.addWidget(self.out_label, 4, 1, 1, 1)
		self.main_tab_layout.addWidget(self.in_text, 5, 0, 1, 1)
		self.main_tab_layout.addWidget(self.out_text, 5, 1, 1, 1)
		self.main_tab.setLayout(self.main_tab_layout)
		
		# DL Tab
		global dl_id
		dl_id = 0
		self.dl_label = QLabel()
		self.dl_label.setText("Hello")
		self.dl_button = QPushButton("Download")
		self.dl_button.clicked.connect(self.dl_run)
		self.dl_combo = QComboBox()
		self.dl_combo.addItem("Japanese to English")
		self.dl_combo.addItem("English to Japanese")
		self.dl_combo.addItem("Chinese to English")
		self.dl_combo.addItem("English to Chinese")
		self.dl_combo.addItem("Indonesia to English")
		self.dl_combo.addItem("English to Indonesia")
		self.dl_combo.addItem("Vietnam to English")
		self.dl_combo.addItem("English to Vietnam")
		self.dl_combo.addItem("Japanese to English MBart")
		self.dl_combo.currentIndexChanged.connect(self.dl_num)
		
		self.dl_layout = QGridLayout()
		self.dl_layout.addWidget(self.dl_combo, 0, 0, 1, 1)
		self.dl_layout.addWidget(self.dl_button, 1, 0, 1, 1)
		self.dl_layout.addWidget(self.dl_label, 2, 0, 1, 1)
		self.dl_tab.setLayout(self.dl_layout)

		layout.addWidget(self.tabs)
		self.tab_widget.setLayout(layout)

		self.statusbar = QStatusBar()
		self.setStatusBar(self.statusbar)
		self.statuslabel = QLabel()
		self.modellabel = QLabel()
		self.statuslabel.setText("Ready")
		self.modellabel.setText("No model loaded")
		self.statusbar.addPermanentWidget(self.statuslabel)
		self.statusbar.addPermanentWidget(self.modellabel)

	def lang_sel(self, i):
		global lang_id
		lang_id = i

	def load_run(self):
		global mname
		if lang_id == 0:
			mname = "models/Helsinki-NLP/opus-mt-ja-en"
			self.modellabel.setText("Japanese to English")

		elif lang_id == 1:
			mname = "models/Helsinki-NLP/opus-mt-en-ja"
			self.modellabel.setText("English to Japanese")

		elif lang_id == 2:
			mname = "models/Helsinki-NLP/opus-mt-zh-en"
			self.modellabel.setText("Chinese to English")

		elif lang_id == 3:
			mname = "models/Helsinki-NLP/opus-mt-en-zh"
			self.modellabel.setText("English to Chinese")

		elif lang_id == 4:
			mname = "models/Helsinki-NLP/opus-mt-id-en"
			self.modellabel.setText("Indonesia to English")

		elif lang_id == 5:
			mname = "models/Helsinki-NLP/opus-mt-en-id"
			self.modellabel.setText("English to Indonesia")

		elif lang_id == 6:
			mname = "models/Helsinki-NLP/opus-mt-vi-en"
			self.modellabel.setText("Vietnam to English")

		elif lang_id == 7:
			mname = "models/Helsinki-NLP/opus-mt-en-vi"
			self.modellabel.setText("English to Vietnam")

		elif lang_id == 8:
			mname = "models/ken11/mbart-ja-en"
			self.modellabel.setText("Japanese to English MBart")

		mfound = os.path.exists(mname)

		if not mfound:
			self.modellabel.setText("Model Files Not Found")
			self.no_file()
			return

		self.thread = QThread()
		self.worker = Worker()
		self.worker.moveToThread(self.thread)
		self.thread.started.connect(self.worker.load_job)
		self.worker.finished.connect(self.thread.quit)
		self.worker.finished.connect(self.worker.deleteLater)
		self.thread.finished.connect(self.thread.deleteLater)

		self.thread.start()

		self.load_button.setEnabled(False)
		self.unload_button.setEnabled(False)
		self.statuslabel.setText("Loading Model Files")
		self.thread.finished.connect(lambda: self.unload_button.setEnabled(True))
		self.thread.finished.connect(lambda: self.tl_button.setEnabled(True))
		self.thread.finished.connect(lambda: self.statuslabel.setText("Ready"))

	def no_file(self):
		button = QMessageBox.warning(
			self,
			"Model Files Not Found",
			"Please make sure you have downloaded the model files and placed it in the right folder.",
			buttons=QMessageBox.StandardButton.Ok,
		)

	def unload_run(self):
		global mname
		global tokenizer
		global model
		mname = 0
		tokenizer = " "
		model = " "
		gc.collect(2)
		self.tl_button.setEnabled(False)
		self.unload_button.setEnabled(False)
		self.load_button.setEnabled(True)
		self.modellabel.setText("No model loaded")

	def tl_run(self):
		global tl_input
		tl_input = self.in_text.toPlainText()
		self.thread = QThread()
		self.worker = Worker()
		self.worker.moveToThread(self.thread)
		self.thread.started.connect(self.worker.tl_job)
		self.worker.finished.connect(self.thread.quit)
		self.worker.finished.connect(self.worker.deleteLater)
		self.thread.finished.connect(self.thread.deleteLater)

		self.thread.start()

		self.tl_button.setEnabled(False)
		self.load_button.setEnabled(False)
		self.unload_button.setEnabled(False)
		self.statuslabel.setText("Translating")
		self.thread.finished.connect(lambda: self.tl_button.setEnabled(True))
		self.thread.finished.connect(lambda: self.load_button.setEnabled(True))
		self.thread.finished.connect(lambda: self.unload_button.setEnabled(True))
		self.thread.finished.connect(lambda: self.statuslabel.setText("Ready"))
		self.thread.finished.connect(lambda: self.out_text.setPlainText(tl_output))
		
	def dl_num(self, i):
		global dl_id
		dl_id = i
	
	def dl_run(self):
		global dl_id
		


if __name__ == '__main__':
	app = QApplication(sys.argv)
	window = MainWindow()
	window.show()
	sys.exit(app.exec())
