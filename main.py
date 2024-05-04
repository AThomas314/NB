
from functions import *

def main():
    app = QApplication(sys.argv)
    w = QWidget()
    w.setGeometry(0,0,250,200)
    AmountColumn=QLineEdit(w)
    AmountColumn.setGeometry(20,30,180,30)
    AmountColumn.setText('Amount Column')
    CodeColumn=QLineEdit(w)
    CodeColumn.setGeometry(20,60,180,30)
    CodeColumn.setText('Code Column')
    OutputPath=QLineEdit(w)
    OutputPath.setGeometry(20,90,180,30)
    OutputPath.setText('Output Path')
    SelectFileButton=QPushButton('Select Input File ( .csv )',w) 
    SelectFileButton.setGeometry(20,120,180,30)
    SelectFileButton.clicked.connect(lambda : ProcessFile(CodeColumn,AmountColumn,OutputPath,app))
    w.show()
    app.exec_()

main()
