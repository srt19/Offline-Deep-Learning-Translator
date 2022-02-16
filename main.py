import sys
from PyQt6.QtCore import (
	Qt, QRect, QSize, QMetaObject, QCoreApplication, QObject, QThread, pyqtSignal
)
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import(
	QWidget, QGridLayout, QPushButton, QComboBox, QPlainTextEdit, QApplication, QMainWindow
)

class Worker(QObject):
	finished = pyqtSignal()
	progress = pyqtSignal(int)
	
	#Loading Model
	def load_job(self):
		global lang
		if lang == 8:
			from transformers import MBartForConditionalGeneration, MBartTokenizer
		else:
			from transformers import MarianTokenizer, AutoModelForSeq2SeqLM

		global mname
		global model
		global tokenizer
		
		if lang == 8:
			tokenizer = MBartTokenizer.from_pretrained("ken11/mbart-ja-en", local_files_only=True)
			model = MBartForConditionalGeneration.from_pretrained("ken11/mbart-ja-en", local_files_only=True)
			
		else:
			tokenizer = MarianTokenizer.from_pretrained(mname, local_files_only=True)
			model = AutoModelForSeq2SeqLM.from_pretrained(mname, local_files_only=True)
			
		print("Loading Finished")
		self.finished.emit()
		
	#Translating
	def tl_job(self):
		global tl_text
		global decoded
		print("Translating")
		if lang == 8:
			inputs = tokenizer(tl_text, return_tensors="pt")
			translated_tokens = model.generate(**inputs, decoder_start_token_id=tokenizer.lang_code_to_id["en_XX"], early_stopping=True, max_length=48)
			decoded = tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)[0]
			
		else:
			input_ids = tokenizer.encode(tl_text, return_tensors="pt")
			outputs = model.generate(input_ids)
			decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)

		#main = Ui_MainWindow()
		print("Completed")	
		self.finished.emit()

class Ui_MainWindow(object):
	def setupUi(self, MainWindow):
		MainWindow.setObjectName("MainWindow")
		MainWindow.resize(800, 600)
		self.centralwidget = QWidget(MainWindow)
		self.centralwidget.setObjectName("centralwidget")
		self.gridLayout = QGridLayout(self.centralwidget)
		self.gridLayout.setObjectName("gridLayout")
		self.loadmodel = QPushButton(self.centralwidget)
		font = QFont()
		font.setPointSize(9)
		self.loadmodel.setFont(font)
		self.loadmodel.setObjectName("loadmodel")
		self.gridLayout.addWidget(self.loadmodel, 0, 5, 1, 1)
		self.translate = QPushButton(self.centralwidget)
		font.setPointSize(12)
		self.translate.setFont(font)
		self.translate.setObjectName("translate")
		self.gridLayout.addWidget(self.translate, 1, 0, 1, 6)
		self.lang_list = QComboBox(self.centralwidget)
		self.lang_list.setObjectName("lang_list")
		self.gridLayout.addWidget(self.lang_list, 0, 0, 1, 5)
		self.inputs = QPlainTextEdit(self.centralwidget)
		self.inputs.setMinimumSize(QSize(380, 430))
		font.setPointSize(11)
		self.inputs.setFont(font)
		self.inputs.setObjectName("inputs")
		self.gridLayout.addWidget(self.inputs, 2, 0, 1, 1)
		self.outputs = QPlainTextEdit(self.centralwidget)
		self.outputs.setMinimumSize(QSize(380, 430))
		font.setPointSize(11)
		self.outputs.setFont(font)
		self.outputs.setObjectName("outputs")
		self.gridLayout.addWidget(self.outputs, 2, 5, 1, 1)
		MainWindow.setCentralWidget(self.centralwidget)
		#Event Stuff
		global lang
		lang = 0
		self.loadmodel.clicked.connect(self.load_run)
		self.translate.clicked.connect(self.tl_run)
		self.lang_list.currentIndexChanged.connect(self.lang_select)

		self.retranslateUi(MainWindow)
		QMetaObject.connectSlotsByName(MainWindow)
		
	#Get Language Number
	def lang_select(self, i):
		global lang
		lang = i
	
	#Loading Model Thread
	def load_run(self):
		global mname		
		if lang == 0:
			print("Japanese to English Selected")
			mname = ".models/Helsinki-NLP/opus-mt-ja-en"
		elif lang == 1:
			print("English to Japanese Selected")
			mname = ".models/Helsinki-NLP/opus-mt-en-ja"
		elif lang == 2:
			print("Chinese to English Selected")
			mname = ".models/Helsinki-NLP/opus-mt-zh-en"
		elif lang == 3:
			print("English to Chinese Selected")
			mname = ".models/Helsinki-NLP/opus-mt-en-zh"
		elif lang == 4:
			print("Indonesia to English Selected")
			mname = ".models/Helsinki-NLP/opus-mt-id-en"
		elif lang == 5:
			print("English to Indonesia Selected")
			mname = ".models/Helsinki-NLP/opus-mt-en-id"
		elif lang == 6:
			print("Vietnam to English Selected")
			mname = ".models/Helsinki-NLP/opus-mt-vi-en"
		elif lang == 7:
			print("English to Vietnam Selected")
			mname = ".models/Helsinki-NLP/opus-mt-en-vi"
		elif lang == 8:
			print("Japanese to English MBart Selected")
		print("Loading Model Files")
		
		self.thread = QThread()
		self.worker = Worker()
		self.worker.moveToThread(self.thread)
		
		self.thread.started.connect(self.worker.load_job)
		self.worker.finished.connect(self.thread.quit)
		self.worker.finished.connect(self.worker.deleteLater)
		self.thread.finished.connect(self.thread.deleteLater)
		
		self.thread.start()
		
		self.loadmodel.setEnabled(False)
		self.thread.finished.connect(
			lambda: self.loadmodel.setEnabled(True)
		)
	
	#Translate Thread
	def tl_run(self):
		global tl_text
		tl_text = self.inputs.toPlainText()
		self.thread = QThread()
		self.worker = Worker()
		self.worker.moveToThread(self.thread)
	
		self.thread.started.connect(self.worker.tl_job)
		self.worker.finished.connect(self.thread.quit)
		self.worker.finished.connect(self.worker.deleteLater)
		self.thread.finished.connect(self.thread.deleteLater)

		self.thread.start()

		self.translate.setEnabled(False)
		self.thread.finished.connect(
			lambda: self.outputs.setPlainText(decoded)
		)
		self.thread.finished.connect(
			lambda: self.translate.setEnabled(True)
		)

	def retranslateUi(self, MainWindow):
		_translate = QCoreApplication.translate
		MainWindow.setWindowTitle(_translate("MainWindow", "Offline Translator"))
		self.loadmodel.setToolTip(_translate("MainWindow", "<html><head/><body><p>Click to load model for translation</p></body></html>"))
		self.loadmodel.setText(_translate("MainWindow", "Load Model"))
		self.translate.setToolTip(_translate("MainWindow", "<html><head/><body><p>Click to start translating</p></body></html>"))
		self.translate.setText(_translate("MainWindow", "Translate"))
		self.inputs.setToolTip(_translate("MainWindow", "<html><head/><body><p>Input your text here</p></body></html>"))
		self.inputs.setPlaceholderText(_translate("MainWindow", "Input your text here"))
		self.outputs.setToolTip(_translate("MainWindow", "<html><head/><body><p>Your translated text goes here</p></body></html>"))
		self.outputs.setPlaceholderText(_translate("MainWindow", "Output text goes here"))
		#Language List
		self.lang_list.addItem("Japanese to English")
		self.lang_list.addItem("English to Japanese")
		self.lang_list.addItem("Chinese to English")
		self.lang_list.addItem("English to Chinese")
		self.lang_list.addItem("Indonesia to English")
		self.lang_list.addItem("English to Indonesia")
		self.lang_list.addItem("Vietnam to English")
		self.lang_list.addItem("English to Vietnam")
		self.lang_list.addItem("JA to EN MBart")

if __name__ == "__main__":
	import sys
	app = QApplication(sys.argv)
	MainWindow = QMainWindow()
	ui = Ui_MainWindow()
	ui.setupUi(MainWindow)
	MainWindow.show()
	sys.exit(app.exec())
