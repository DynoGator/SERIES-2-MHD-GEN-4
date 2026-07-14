from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTextBrowser

class GateRunner(QWidget):
    def __init__(self, worker):
        super().__init__()
        self.worker = worker
        
        layout = QVBoxLayout(self)
        
        self.btn_run = QPushButton("Run Selected Gates")
        self.btn_run.clicked.connect(self.run_gates)
        layout.addWidget(self.btn_run)
        
        self.text_browser = QTextBrowser()
        layout.addWidget(self.text_browser)
        
    def run_gates(self):
        self.text_browser.setText("Running gates...")
        self.worker.run_gate("G0")
        
    def set_report(self, md_text: str):
        # Extremely basic markdown to html
        html = md_text.replace('\n', '<br/>')
        self.text_browser.setHtml(html)
