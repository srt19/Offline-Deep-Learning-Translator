import sys
import gc
from PyQt6.QtCore import QSize, QObject, QThread, pyqtSignal
from PyQt6.QtWidgets import (
	QGridLayout, QPushButton, QPlainTextEdit, QComboBox, QWidget, QApplication, QMainWindow
)

class Worker(QObject):
	finished = pyqtSignal()
	
	def load_job(self):
		global lang
		global mname
		global tokenizer
		global model
		print("Loading Model Files")
		if lang_id == 8:
			from transformers import MBartForConditionalGeneration, MBartTokenizer
			tokenizer = MBartTokenizer.from_pretrained("mname", local_files_only=True)
			model = MBartForConditionalGeneration.from_pretrained("mname", local_files_only=True)
		else:
			from transformers import MarianTokenizer, MarianMTModel
			tokenizer = MarianTokenizer.from_pretrained(mname, local_files_only=True)
			model = MarianMTModel.from_pretrained(mname, local_files_only=True)
		print("Loading Model Completed")
		self.finished.emit()
		
	def tl_job(self):
		global tokenizer
		global model
		global tl_output
		if lang_id == 8:
			inputs = tokenizer(tl_input, return_tensors="pt")
			translated_tokens = model.generate(**inputs, decoder_start_token_id=tokenizer.lang_code_to_id["en_XX"], early_stopping=True, max_length=48)
			tl_output = tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)[0]
		else:
			input_ids = tokenizer.encode(tl_input, return_tensors="pt")
			outputs = model.generate(input_ids)
			tl_output = tokenizer.decode(outputs[0], skip_special_tokens=True)
		print("Completed")
		self.finished.emit()

class MainWindow(QMainWindow):
	def __init__(self):
		super(MainWindow, self).__init__()
		
		self.setWindowTitle("Offline Translator")
		
		layout = QGridLayout()
		
		self.tl_button = QPushButton("Translate")
		self.tl_button.clicked.connect(self.tl_run)
		self.load_button = QPushButton("Load Model")
		self.load_button.clicked.connect(self.load_run)
		self.unload_button = QPushButton("Unload Model")
		self.unload_button.clicked.connect(self.unload_run)
		self.in_text = QPlainTextEdit()
		self.in_text.setMinimumSize(QSize(380, 430))
		self.in_text.setPlainText("Input your text here")
		self.out_text = QPlainTextEdit()
		self.out_text.setMinimumSize(QSize(380, 430))
		self.out_text.setPlainText("Your translated text goes here")
		#Languages List
		self.lang_list = QComboBox()
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
		
		#Layout Settings
		layout.addWidget(self.lang_list, 0, 0, 1, 2)
		layout.addWidget(self.load_button, 2, 0, 1, 1)
		layout.addWidget(self.unload_button, 2, 1, 1, 1)
		layout.addWidget(self.tl_button, 3, 0, 1, 2)
		layout.addWidget(self.in_text, 4, 0, 1, 1)
		layout.addWidget(self.out_text,4, 1, 1, 1)
		
		widget = QWidget()
		widget.setLayout(layout)
		self.setCentralWidget(widget)
	
	def lang_sel(self, i):
		global lang_id
		lang_id = i
		
	def load_run(self):
		global mname
		if lang_id == 0:
			mname = "Helsinki-NLP/opus-mt-ja-en"
			print("Japanese to English Selected")
		elif lang_id == 1:
			mname = "models/Helsinki-NLP/opus-mt-en-ja"
			print ("English to Japanese Selected")
		elif lang_id == 2:
			mname = "models/Helsinki-NLP/opus-mt-zh-en"
			print("Chinese to English Selected")
		elif lang_id == 3:
			mname = "models/Helsinki-NLP/opus-mt-en-zh"
			print("English to Chinese Selected")
		elif lang_id == 4:
			mname = "models/Helsinki-NLP/opus-mt-id-en"
			print("Indonesia to English Selected")
		elif lang_id == 5:
			mname = "models/Helsinki-NLP/opus-mt-en-id"
			print("English to Indonesia Selected")
		elif lang_id == 6:
			mname = "models/Helsinki-NLP/opus-mt-vi-en"
			print("Vietnam to English Selected")
		elif lang_id == 7:
			mname = "models/Helsinki-NLP/opus-mt-en-vi"
			print("English to Vietnam Selected")
		elif lang_id == 8:
			mname = "models/ken11/mbart-ja-en"
			print("Japanese to English MBart Selected")
		self.thread = QThread()
		self.worker = Worker()
		self.worker.moveToThread(self.thread)
		self.thread.started.connect(self.worker.load_job)
		self.worker.finished.connect(self.thread.quit)
		self.worker.finished.connect(self.worker.deleteLater)
		self.thread.finished.connect(self.thread.deleteLater)
		
		self.thread.start()

		self.load_button.setEnabled(False)
		self.worker.finished.connect(lambda: self.load_button.setEnabled(True))

	def unload_run(self):
		global mname
		global tokenizer
		global model
		mname = " "
		tokenizer = " "
		model = " "
		gc.collect(2)
		print("Model Unloaded")
		
	def tl_run(self):
		global tl_input
		tl_input = self.in_text.toPlainText()
		print("Translating")
		
		self.thread = QThread()
		self.worker = Worker()
		self.worker.moveToThread(self.thread)
		self.thread.started.connect(self.worker.tl_job)
		self.worker.finished.connect(self.thread.quit)
		self.worker.finished.connect(self.worker.deleteLater)
		self.thread.finished.connect(self.thread.deleteLater)
		
		self.thread.start()
		
		self.tl_button.setEnabled(False)
		self.thread.finished.connect(lambda: self.tl_button.setEnabled(True))
		self.thread.finished.connect(lambda: self.out_text.setPlainText(tl_output))
		
if __name__ == '__main__' :
	app = QApplication(sys.argv)
	window = MainWindow()
	window.show()
	sys.exit(app.exec())
