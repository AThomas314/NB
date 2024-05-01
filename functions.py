import pandas as pd
import sys
import numpy as np
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from warnings import simplefilter
simplefilter(action='ignore')

def TrueOutStanding(dictionary:dict[pd.DataFrame],AmountColumn:str)->dict[pd.DataFrame]:
    for key in list(dictionary.keys()):
        dictionary[key].reset_index(inplace=True,drop=True)
        Outstandings = dictionary[key]['CumSum'].unique()
        if (np.max(Outstandings)<0) or (np.min(Outstandings)>0):
            dictionary[key]['True Outstanding']=dictionary[key][AmountColumn]
        else:
            dictionary[key]['True Outstanding'] = np.zeros(len(dictionary[key]))
            try:
                dictionary[key]['True Outstanding'][1] = dictionary[key]['CumSum'][0] + dictionary[key][AmountColumn][1]
                for i in range(2,len(dictionary[key]),1):
                    dictionary[key]['True Outstanding'][i] = dictionary[key][AmountColumn][i]
            except:
                pass
    return dictionary

def Reconcile(  df:pd.DataFrame,
                AmtCol:str,
                VendorNumberCol:str):
    def Part1(df,AmtCol,VendorNumberCol):
        vendors=df[VendorNumberCol].unique()
        VendorLedgers:dict[pd.DataFrame]={}
        for vendor in vendors:
            VendorLedgers[vendor] = df[df[VendorNumberCol]==vendor]
        easy=[]
        for key in VendorLedgers.keys():
            VendorLedgers[key].reset_index(inplace=True,drop=True)
            VendorLedgers[key]['CumSum'] = VendorLedgers[key][AmtCol].cumsum()
            Outstandings = VendorLedgers[key][AmtCol].unique()
        if (np.max(Outstandings)<=0) or (np.min(Outstandings)>=0):
            easy.append(key)
        print(15100032 in easy)
        print('15100032' in easy)
        return easy,VendorLedgers

    def Part2(VendorLedgers,AmtCol,easy):
        for key in VendorLedgers.keys():
            if key not in easy:
                closing = np.sum(VendorLedgers[key][AmtCol].values)
                if closing>=0:
                    plus=True
                else:
                    plus=False
                if plus:
                    for i in range((len(VendorLedgers[key])-1),0,-1):
                        try:
                            if VendorLedgers[key].iloc[i]['CumSum']<=0:
                                ToDrop=list(range(i))
                                VendorLedgers[key].drop(ToDrop,axis=0,inlace=True)
                        except:
                            pass
                if not plus:
                    for i in range((len(VendorLedgers[key])-1),0,-1):
                        try:
                            if VendorLedgers[key].iloc[i]['CumSum']>=0:
                                ToDrop=list(range(i))
                                VendorLedgers[key].drop(ToDrop,axis=0,inplace=True)
                        except:
                            pass
        return VendorLedgers

    try:
        df[AmtCol]=df[AmtCol].apply(lambda x : x.replace(',','')).astype(np.float64)
    except:
        pass

    easy,VendorLedgers = Part1(df,AmtCol,VendorNumberCol)
    VendorLedgers = Part2(VendorLedgers,AmtCol,easy)
    
    return VendorLedgers
    
def Concatenation(VendorLedgers:dict[pd.DataFrame]):
    output = pd.concat(VendorLedgers.values(),axis=0)
    return output

def ProcessFile(CodeColumn:QLineEdit,AmountColumn:QLineEdit,OutputPath:QLineEdit,app:QApplication):
    CodeColumn , AmountColumn,OutputPath = CodeColumn.text() , AmountColumn.text(),OutputPath.text()
    dlg = QFileDialog()
    dlg.setFileMode(QFileDialog.AnyFile)
    if dlg.exec_():
        filename = dlg.selectedFiles()[0]
    df = pd.read_csv(filename)
    dictionary = Reconcile(df,AmountColumn,CodeColumn)
    dictionary = TrueOutStanding(dictionary,AmountColumn)
    newdf = Concatenation(dictionary)
    newdf.to_csv(OutputPath)
    sys.exit(app)