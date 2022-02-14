import sys
from PyQt6.QtCore import (
	Qt, QRect, QSize, QMetaObject, QCoreApplication, QObject, QThread, pyqtSignal
)
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
	QWidget, QPushButton, QComboBox, QPlainTextEdit, QFrame, QMenuBar, QStatusBar, QApplication, QMainWindow
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
			tokenizer = MBartTokenizer.from_pretrained("models/ken11/mbart-ja-en", local_files_only=True)
			model = MBartForConditionalGeneration.from_pretrained("models/ken11/mbart-ja-en", local_files_only=True)
			
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
		MainWindow.setEnabled(True)
		MainWindow.resize(800, 600)
		self.centralwidget = QWidget(MainWindow)
		self.centralwidget.setObjectName("centralwidget")
		self.LoadModel = QPushButton(self.centralwidget)
		self.LoadModel.setGeometry(QRect(340, 40, 120, 30))
		font = QFont()
		font.setFamily("Arial")
		font.setPointSize(10)
		self.LoadModel.setFont(font)
		self.LoadModel.setIconSize(QSize(16, 16))
		self.LoadModel.setAutoDefault(False)
		self.LoadModel.setDefault(False)
		self.LoadModel.setFlat(False)
		self.LoadModel.setObjectName("LoadModel")
		self.Translate = QPushButton(self.centralwidget)
		self.Translate.setGeometry(QRect(350, 100, 100, 30))
		font.setFamily("Arial")
		font.setPointSize(12)
		self.Translate.setFont(font)
		self.Translate.setObjectName("Translate")
		self.lang_list = QComboBox(self.centralwidget)
		self.lang_list.setGeometry(QRect(330, 10, 80, 25))
		font.setFamily("Arial")
		font.setPointSize(10)
		self.lang_list.setFont(font)
		self.lang_list.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
		self.lang_list.setObjectName("lang_list")
		self.output = QPlainTextEdit(self.centralwidget)
		self.output.setGeometry(QRect(410, 150, 380, 400))
		font.setFamily("Arial")
		font.setPointSize(11)
		self.output.setFont(font)
		self.output.setFrameShadow(QFrame.Shadow.Plain)
		self.output.setObjectName("output")
		self.input = QPlainTextEdit(self.centralwidget)
		self.input.setGeometry(QRect(10, 150, 380, 400))
		font.setFamily("Arial")
		font.setPointSize(11)
		self.input.setFont(font)
		self.input.setFrameShadow(QFrame.Shadow.Plain)
		self.input.setObjectName("input")
		MainWindow.setCentralWidget(self.centralwidget)
		self.menubar = QMenuBar(MainWindow)
		self.menubar.setGeometry(QRect(0, 0, 800, 26))
		self.menubar.setObjectName("menubar")
		MainWindow.setMenuBar(self.menubar)
		self.statusbar = QStatusBar(MainWindow)
		self.statusbar.setObjectName("statusbar")
		MainWindow.setStatusBar(self.statusbar)

		#Event Stuff
		global lang
		lang = 0
		self.LoadModel.clicked.connect(self.load_run)
		self.Translate.clicked.connect(self.tl_run)
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
			mname = "models/Helsinki-NLP/opus-mt-ja-en"
		elif lang == 1:
			print("English to Japanese Selected")
			mname = "models/Helsinki-NLP/opus-mt-en-ja"
		elif lang == 2:
			print("Chinese to English Selected")
			mname = "models/Helsinki-NLP/opus-mt-zh-en"
		elif lang == 3:
			print("English to Chinese Selected")
			mname = "models/Helsinki-NLP/opus-mt-en-zh"
		elif lang == 4:
			print("Indonesia to English Selected")
			mname = "models/Helsinki-NLP/opus-mt-id-en"
		elif lang == 5:
			print("English to Indonesia Selected")
			mname = "models/Helsinki-NLP/opus-mt-en-id"
		elif lang == 6:
			print("Vietnam to English Selected")
			mname = "models/Helsinki-NLP/opus-mt-vi-en"
		elif lang == 7:
			print("English to Vietnam Selected")
			mname = "models/Helsinki-NLP/opus-mt-en-vi"
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
		
		self.LoadModel.setEnabled(False)
		self.thread.finished.connect(
			lambda: self.LoadModel.setEnabled(True)
		)
	
	#Translate Thread
	def tl_run(self):
		global tl_text
		tl_text = self.input.toPlainText()
		self.thread = QThread()
		self.worker = Worker()
		self.worker.moveToThread(self.thread)
	
		self.thread.started.connect(self.worker.tl_job)
		self.worker.finished.connect(self.thread.quit)
		self.worker.finished.connect(self.worker.deleteLater)
		self.thread.finished.connect(self.thread.deleteLater)

		self.thread.start()

		self.Translate.setEnabled(False)
		self.thread.finished.connect(
			lambda: self.output.setPlainText(decoded)
		)
		self.thread.finished.connect(
			lambda: self.Translate.setEnabled(True)
		)

	def retranslateUi(self, MainWindow):
		_translate = QCoreApplication.translate
		MainWindow.setWindowTitle(_translate("MainWindow", "Offline Translator"))
		self.LoadModel.setText(_translate("MainWindow", "Load Model"))
		self.Translate.setText(_translate("MainWindow", "Translate"))
		self.output.setToolTip(_translate("MainWindow", "Translated Text Goes Here"))
		self.output.setPlaceholderText(_translate("MainWindow", "Output Text Here"))
		self.input.setToolTip(_translate("MainWindow", "Your Text Goes Here"))
		self.input.setPlaceholderText(_translate("MainWindow", "Input Your Text Here"))
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
	app = QApplication(sys.argv)
	MainWindow = QMainWindow()
	ui = Ui_MainWindow()
	ui.setupUi(MainWindow)
	MainWindow.show()
	sys.exit(app.exec())
