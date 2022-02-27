import os
import sys
import gc
from PyQt6.QtCore import QSize, QObject, QThread, pyqtSignal
from PyQt6.QtGui import QAction, QFont
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
	QGridLayout, QLabel, QMessageBox, QPushButton, QPlainTextEdit, QTextBrowser, QComboBox, QWidget, QApplication, QMainWindow, QStatusBar, QFrame
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
			translated_tokens = model.generate(**inputs, decoder_start_token_id=tokenizer.lang_code_to_id["en_XX"], early_stopping=True, max_length=48)
			tl_output = tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)[0]
		else:
			input_ids = tokenizer.encode(tl_input, return_tensors="pt")
			outputs = model.generate(input_ids)
			tl_output = tokenizer.decode(outputs[0], skip_special_tokens=True)
		self.finished.emit()

class AboutWindow(QWidget):
	def __init__(self):
		super().__init__()
		self.setWindowTitle("About")
		self.layout = QGridLayout()
		self.aboutlabel = QLabel("About this program")
		self.abouttext = QTextBrowser()
		self.abouttext.setMinimumSize(QSize(378, 351))
		self.abouttext.setHtml(
			"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
			"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
			"p, li { white-space: pre-wrap; }\n"
			"</style></head><body style=\" font-family:\'Segoe UI\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
			"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:11pt;\">This program mainly to help user who doesn\'t have internet connection all of the time, so you only need to download certain language model for offline translation.</span></p>\n"
			"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:11pt;\"><br /></p>\n"
			"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:11pt;\">This Program was made using:</span></p>\n"
			"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:11pt;\">* PyQt6</span></p>\n"
			"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:11pt;\">* Transformers</span></p>\n"
			"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:11pt;\">* PyTorch</span></p>\n"
			"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:11pt;\"><br /></p>\n"
			"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><a href=\"https://github.com/srt19\"><span style=\" text-decoration: underline; color:#007af4;\">Link to the project</span></a></p></body></html>"
		)
		
		self.layout.addWidget(self.aboutlabel, 0, 0, 1, 1)
		self.layout.addWidget(self.abouttext, 1, 0, 1, 1)
		self.setLayout(self.layout)

class MainWindow(QMainWindow):
	def __init__(self):
		super(MainWindow, self).__init__()
		
		self.setWindowTitle("Offline Translator")
		
		self.about = None
		
		layout = QGridLayout()
		font = QFont()
		font.setPointSize(11)
		
		self.tl_button = QPushButton("Translate")
		self.tl_button.clicked.connect(self.tl_run)
		self.tl_button.setStatusTip("Click to start translation")
		self.load_button = QPushButton("Load Model")
		self.load_button.clicked.connect(self.load_run)
		self.load_button.setStatusTip("Click to load model files")
		self.unload_button = QPushButton("Unload Model")
		self.unload_button.clicked.connect(self.unload_run)
		self.unload_button.setStatusTip("Click to unload model files")
		self.in_text = QPlainTextEdit()
		self.in_text.setStatusTip("Type your text here")
		self.in_text.setMinimumSize(QSize(380, 430))
		self.out_text = QPlainTextEdit()
		self.out_text.setMinimumSize(QSize(380, 430))
		self.out_text.setStatusTip("Your text output goes here")
		#Languages List
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
		
		#Layout Settings
		layout.addWidget(self.lang_list, 0, 0, 1, 2)
		layout.addWidget(self.load_button, 2, 0, 1, 1)
		layout.addWidget(self.unload_button, 2, 1, 1, 1)
		layout.addWidget(self.tl_button, 3, 0, 1, 2)
		layout.addWidget(self.in_label, 4, 0, 1, 1)
		layout.addWidget(self.out_label,4, 1, 1, 1)
		layout.addWidget(self.in_text, 5, 0, 1, 1)
		layout.addWidget(self.out_text,5, 1, 1, 1)
		
		widget = QWidget()
		widget.setLayout(layout)
		widget.setFont(font)
		self.setCentralWidget(widget)
		
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
			mname = "./models/Helsinki-NLP/opus-mt-ja-en"
			self.modellabel.setText("Japanese to English")
		elif lang_id == 1:
			mname = "./models/Helsinki-NLP/opus-mt-en-ja"
			self.modellabel.setText("English to Japanese")
		elif lang_id == 2:
			mname = "./models/Helsinki-NLP/opus-mt-zh-en"
			self.modellabel.setText("Chinese to English")
		elif lang_id == 3:
			mname = "./models/Helsinki-NLP/opus-mt-en-zh"
			self.modellabel.setText("English to Chinese")
		elif lang_id == 4:
			mname = "./models/Helsinki-NLP/opus-mt-id-en"
			self.modellabel.setText("Indonesia to English")
		elif lang_id == 5:
			mname = "./models/Helsinki-NLP/opus-mt-en-id"
			self.modellabel.setText("English to Indonesia")
		elif lang_id == 6:
			mname = "./models/Helsinki-NLP/opus-mt-vi-en"
			self.modellabel.setText("Vietnam to English")
		elif lang_id == 7:
			mname = "./models/Helsinki-NLP/opus-mt-en-vi"
			self.modellabel.setText("English to Vietnam")
		elif lang_id == 8:
			mname = "./models/ken11/mbart-ja-en"
			self.modellabel.setText("Japanese to English MBart")
		isExist = os.path.exists(mname)
		if isExist == False:
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
		self.statuslabel.setText("Loading Model Files")
		self.thread.finished.connect(lambda: self.statuslabel.setText("Ready"))
		self.thread.finished.connect(lambda: self.load_button.setEnabled(True))
	
	def no_file(self):
		button = QMessageBox.warning(
			self,
			"Model Files Not Found",
			"Please make sure you have downloaded the model files and placed in the right models folder.",
			buttons=QMessageBox.StandardButton.Ok,
		)

	def unload_run(self):
		global mname
		global tokenizer
		global model
		mname = " "
		tokenizer = " "
		model = " "
		gc.collect(2)
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
		self.statuslabel.setText("Translating")
		self.thread.finished.connect(lambda: self.statuslabel.setText("Ready"))
		self.thread.finished.connect(lambda: self.tl_button.setEnabled(True))
		self.thread.finished.connect(lambda: self.out_text.setPlainText(tl_output))
		
if __name__ == '__main__' :
	app = QApplication(sys.argv)
	window = MainWindow()
	window.show()
	sys.exit(app.exec())
