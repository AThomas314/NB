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
        try:
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
        except:
            pass
    return dictionary

def Reconcile(  df:pd.DataFrame,
                AmtCol:str,
                VendorNumberCol:str):

    def Part1(df:pd.DataFrame,AmtCol:str,VendorNumberCol:str):
        vendors=df[VendorNumberCol].unique()
        VendorLedgers:dict[pd.DataFrame]={}
        for vendor in vendors:
            VendorLedgers[vendor] = df[df[VendorNumberCol]==vendor]
        easy=[]
        for key in VendorLedgers.keys():
            VendorLedgers[key] = VendorLedgers[key].reset_index(drop=True)
            VendorLedgers[key]['CumSum'] = VendorLedgers[key][AmtCol].cumsum()
            Outstandings = VendorLedgers[key][AmtCol].unique()
        try:
            if (np.max(Outstandings)<=0) or (np.min(Outstandings)>=0):
                easy.append(key)
        except:
            pass
        return easy,VendorLedgers

    def Part2(VendorLedgers:dict[pd.DataFrame],AmtCol:str,easy:list):
        for key in VendorLedgers.keys():
            if key not in easy:
                closing = np.sum(VendorLedgers[key][AmtCol].values).round(-1)
                if closing>0:
                    plus=True
                if closing<0:
                    plus=False
                if closing==0:
                    plus=None
                if plus==True:
                    for i in range((len(VendorLedgers[key])-1),0,-1):
                        try:
                            if VendorLedgers[key].iloc[i]['CumSum']<=0:
                                ToDrop = list(range(i))
                                VendorLedgers[key] = VendorLedgers[key].drop(ToDrop,axis=0)
                                VendorLedgers[key] = VendorLedgers[key].reset_index(drop=True)
                        except:
                            pass
                if plus==False:
                    for i in range((len(VendorLedgers[key])-1),0,-1):
                        try:
                            if VendorLedgers[key].iloc[i]['CumSum']>=0:
                                ToDrop=list(range(i))
                                VendorLedgers[key]=VendorLedgers[key].drop(ToDrop,axis=0)
                                VendorLedgers[key] = VendorLedgers[key].reset_index(drop=True)
                        except:
                            pass
                if plus==None:
                    ToDrop=list(VendorLedgers[key].index)
                    VendorLedgers[key] = VendorLedgers[key].drop(ToDrop,axis=0)
        return VendorLedgers

    def Part3(VendorLedgers:dict[pd.DataFrame],easy:list):
        for key in VendorLedgers.keys():
            if key not in easy:
                VendorLedgers[key].reset_index(inplace=True,drop=True)
                CumSums = VendorLedgers[key]['CumSum'].values                
                if 0 in CumSums: 
                    ToDrop=list(range(np.max(VendorLedgers[key]['CumSum'].index[VendorLedgers[key]['CumSum'].values==0])+1))
                    VendorLedgers[key] = VendorLedgers[key].drop(ToDrop,axis=0)
                else:
                    pass
        return VendorLedgers
    def Part4A(VendorLedgers:dict[pd.DataFrame],easy:list):
        def Part4(Acc:pd.DataFrame):
            MinIdx=None
            MaxIdx=None
            uniquecumsums = Acc['CumSum'].unique()
            cumsums = Acc['CumSum']
            while len(uniquecumsums)!=len(cumsums):
                for i in uniquecumsums:
                    if len(cumsums[cumsums==i].index)>=2 and (MinIdx == None) and (MaxIdx == None):
                        MinIdx , MaxIdx = np.min(cumsums[cumsums==i].index) , np.max(cumsums[cumsums==i].index)
                        ToDrop=list(range(MinIdx+1,MaxIdx+1,1))
                        Acc=Acc.drop(ToDrop,axis=0)
                        Acc=Acc.reset_index(drop=True)
                        uniquecumsums = Acc['CumSum'].unique()
                        cumsums = Acc['CumSum']
                        MinIdx=None
                        MaxIdx=None
            return Acc
        for key in VendorLedgers.keys():
            if key not in easy:
                df = VendorLedgers[key] 
                if isinstance(df,pd.DataFrame) :
                    df = df.reset_index(drop=True)
                    VendorLedgers[key] = Part4(df)
        return VendorLedgers

    try:
        df[AmtCol]=df[AmtCol].apply(lambda x : x.replace(',','')).astype(np.float64)
    except:
        pass

    easy,VendorLedgers = Part1(df,AmtCol,VendorNumberCol)
    VendorLedgers = Part2(VendorLedgers,AmtCol,easy)
    VendorLedgers = Part3(VendorLedgers,easy)
    VendorLedgers = Part4A(VendorLedgers,easy)

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