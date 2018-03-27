__author__ = 'tli56'
import sys,re
import os
import shutil
class CopyPat:
    def __init__(self):
        self.PatfulPathDictStag ={}
        self.PatDictStag ={}
        self.PatfulPathCopy ={}
        self.PatDictProd ={}
        self.PatNameList = []

    def collectPatFromRelease(self,RootDir,postfix="pat",srcOrDes ="Stag"):
        for root, subdirs, files in os.walk(RootDir):
            for special_file in files:
                print("detect new file " +  special_file + "\n")
                if postfix:
                    if special_file.endswith(postfix):
                        patID = special_file[-15:-12]
                        patName = special_file[:-16]
                        print("Pat ID " +  patID)
                        print("Pat name " +  patName)
                        if srcOrDes == "Stag":
                            if patName in self.PatDictStag.keys():
                                if int(patID) > int(self.PatDictStag[patName]):
                                    self.PatDictStag[patName] = int(patID)
                                    self.PatfulPathDictStag.pop(patName)
                                    self.PatfulPathDictStag[patName] = os.path.join(root,patName)
                            else:
                                self.PatDictStag[patName] = patID
                                self.PatfulPathDictStag[patName]=os.path.join(root,patName)
                        else:
                            if patName in self.PatDictProd.keys():
                                if int(patID) > int(self.PatDictProd[patName]):
                                    self.PatDictProd[patName] = int(patID)
                            else:
                                self.PatDictProd[patName] = int(patID)


    # def readAlgorithm(self,logfile):
    #      logfilehandle= open(logfile,"r")
    #      fileLines = logfilehandle.readlines()
    #      for fileLine in fileLines:
    #          self.PatNameList.append(fileLine)
    #      logfilehandle.close()
    #
    # def PrintPlist(self,logfile):
    #      logfilehandle= open(logfile,"w")
    #      logfilehandle.write("print plist\n")
    #      for elm in self.PatNameList:
    #          plistname = "mbist_KS_atspeed_" + elm.rstrip()
    #          logfilehandle.write(",,,"+plistname+",PatternListRef,SOC_RESET_38_FUSEOVR_wsg_tm_slowtap\n")
    #          logfilehandle.write(",,,,,mbist_atspeed_cfg\n")
    #          logfilehandle.write(",,,,,mtt_setting_inject\n")
    #          logfilehandle.write(",,,,,HDC_" + elm.rstrip() +"\n")
    #          logfilehandle.write(",,,,,UHDC_" + elm.rstrip() +"\n")
    #          logfilehandle.write(",,,,,TP_RF_" + elm.rstrip() +"\n")
    #          logfilehandle.write(",,,,,URF_" + elm.rstrip() +"\n")
    #      plistname = "mbist_KS_atspeed_all_algos"
    #      logfilehandle.write(",,,"+plistname+",PatternListRef,SOC_RESET_38_FUSEOVR_wsg_tm_slowtap\n")
    #      logfilehandle.write(",,,,,mbist_atspeed_cfg\n")
    #      logfilehandle.write(",,,,,mtt_setting_inject\n")
    #      logfilehandle.write(",,,,,mbist_EI_RedMem_stream_in\n")
    #      logfilehandle.write(",,,,,mbist_bisr_all_pwrup\n")
    #      for elm in self.PatNameList:
    #          logfilehandle.write(",,,,,HDC_" + elm.rstrip() +"\n")
    #          logfilehandle.write(",,,,,UHDC_" + elm.rstrip() +"\n")
    #          logfilehandle.write(",,,,,TP_RF_" + elm.rstrip() +"\n")
    #          logfilehandle.write(",,,,,URF_" + elm.rstrip() +"\n")
    #      logfilehandle.close()

    def CheckNewPat(self):
        for elm in self.PatDictStag:
            if elm in self.PatDictProd:
                if int(self.PatDictStag[elm]) > int(self.PatDictProd[elm]):
                    self.PatfulPathCopy[elm] = self.PatfulPathDictStag[elm]
            else:
                self.PatfulPathCopy[elm] = self.PatfulPathDictStag[elm]

    def PrntCopyFile(self,logfile,target):
        logfilehandle= open(logfile,"w")
        for elm in self.PatfulPathCopy:
            logfilehandle.write("del/f/s/q " +  target + "\\" + elm + "*"+ "\n" )
            logfilehandle.write("COPY " +  self.PatfulPathCopy[elm] + "*.*  " + target + "\n")
        logfilehandle.close()

class genMTTConf:
    def __init__(self):
        self.hpcDict = {}
        self.uhpcDict = {}
        self.tprfDict = {}
        self.utprfDict = {}
        self.romDict = {}

    def readMTTList(self,mttList):
        MTThandle= open(mttList,"r")
        fileLines = MTThandle.readlines()
        for fileLine in fileLines:
            hdcFound = re.search(r'^HDC_HPSPSRAM_MTT(\d*)',fileLine)
            uhdcFound = re.search(r'^HDC_UHPSPSRAM_MTT(\d*)',fileLine)
            tprfFound = re.search(r'^TP_HSxRF_MTT(\d*)\_(\d*)',fileLine)
            utprfFound = re.search(r'^TP_UHSRF_MTT(\d*)\_(\d*)',fileLine)
            romFound = re.search(r'^HD_ROM_MTT(\d*)',fileLine)
            if hdcFound:
                self.hpcDict[fileLine.rstrip()] = hdcFound.group(1)
            if uhdcFound:
                self.uhpcDict[fileLine.rstrip()] = uhdcFound.group(1)
            if tprfFound:
                self.tprfDict[fileLine.rstrip()] = tprfFound.group(1) + "_" + tprfFound.group(2)
            if utprfFound:
                self.utprfDict[fileLine.rstrip()] = utprfFound.group(1) + "_" + utprfFound.group(2)
            if romFound:
                self.romDict[fileLine.rstrip()] = romFound.group(1)
    def PrntMTTConf(self,mttConf):
        logfilehandle= open(mttConf,"w")
        #print hdc MTT setting
        logfilehandle.write("#hdc mtt list\n")
        for elm in self.hpcDict:
            #convert decimal to binary
            decimalValue = self.hpcDict[elm]
            binaryValue = bin(int(decimalValue))[2:]
            binaryReverseValue = binaryValue[::-1].ljust(16).replace(" ","0")
            binaryReverseValueWSpace = ""
            for indx in range(len(binaryReverseValue)):
                binaryReverseValueWSpace = binaryReverseValueWSpace + binaryReverseValue[indx] + " "
            logfilehandle.write("+    " + elm + "   MAIN         PAT               mtt_setting_inject_0* 35              0            DATA             TDI      " +  binaryReverseValueWSpace + "\n")

        logfilehandle.write("#uhdc mtt list\n")
        for elm in self.uhpcDict:
            #convert decimal to binary
            decimalValue = self.uhpcDict[elm]
            binaryValue = bin(int(decimalValue))[2:]
            binaryReverseValue = binaryValue[::-1].ljust(16).replace(" ","0")
            binaryReverseValueWSpace = ""
            for indx in range(len(binaryReverseValue)):
                binaryReverseValueWSpace = binaryReverseValueWSpace + binaryReverseValue[indx] + " "
            logfilehandle.write("+    " + elm + "   MAIN         PAT               mtt_setting_inject_0* 35              0            DATA             TDI      " +  binaryReverseValueWSpace  + "\n" )

        logfilehandle.write("#tprf mtt list\n")
        for elm in self.tprfDict:
            #convert decimal to binary
            decimalValue = self.tprfDict[elm].split("_")[0]
            slowbitValue = self.tprfDict[elm].split("_")[1]
            binaryValue = bin(int(decimalValue))[2:]
            binaryReverseValue = binaryValue[::-1].ljust(18).replace(" ","0")
            binaryReverseValueWSpace = ""
            for indx in range(len(binaryReverseValue)):
                binaryReverseValueWSpace = binaryReverseValueWSpace + binaryReverseValue[indx] + " "
            slowbitValueReverse = slowbitValue[::-1]
            slowbitValueReverseWSpace = ""
            for indx in range(len(slowbitValueReverse)):
                slowbitValueReverseWSpace = slowbitValueReverseWSpace + slowbitValueReverse[indx] + " "
            binaryReverseValueWSpace =  binaryReverseValueWSpace +  slowbitValueReverseWSpace
            logfilehandle.write("+    " + elm + "   MAIN         PAT               mtt_setting_inject_0* 35              0            DATA             TDI      " +  binaryReverseValueWSpace + "\n" )

        logfilehandle.write("#utprf mtt list\n")
        for elm in self.utprfDict:
            #convert decimal to binary
            decimalValue = self.utprfDict[elm].split("_")[0]
            slowbitValue = self.utprfDict[elm].split("_")[1]
            binaryValue = bin(int(decimalValue))[2:]
            binaryReverseValue = binaryValue[::-1].ljust(18).replace(" ","0")
            binaryReverseValueWSpace = ""
            for indx in range(len(binaryReverseValue)):
                binaryReverseValueWSpace = binaryReverseValueWSpace + binaryReverseValue[indx] + " "
            slowbitValueReverse = slowbitValue[::-1]
            slowbitValueReverseWSpace = ""
            for indx in range(len(slowbitValueReverse)):
                slowbitValueReverseWSpace = slowbitValueReverseWSpace + slowbitValueReverse[indx] + " "
            binaryReverseValueWSpace =  binaryReverseValueWSpace +  slowbitValueReverseWSpace
            logfilehandle.write("+    " + elm + "   MAIN         PAT               mtt_setting_inject_0* 35              0            DATA             TDI      " +  binaryReverseValueWSpace  + "\n")

        logfilehandle.write("#hdrom mtt list\n")
        for elm in self.romDict:
            #convert decimal to binary
            decimalValue = self.romDict[elm]
            binaryValue = bin(int(decimalValue))[2:]
            binaryReverseValue = binaryValue[::-1].ljust(16).replace(" ","0")
            binaryReverseValueWSpace = ""
            for indx in range(len(binaryReverseValue)):
                binaryReverseValueWSpace = binaryReverseValueWSpace + binaryReverseValue[indx] + " "
            logfilehandle.write("+    " + elm + "   MAIN         PAT               mtt_setting_inject_0* 35              0            DATA             TDI      " +  binaryReverseValueWSpace  + "\n" )


if ( __name__ == "__main__"):
#    PatCopyInst = CopyPat()
#    PatCopyInst.collectPatFromRelease("I:\\hdmxpats\\x76\\staging\\Msoc_array\\A0","pat","Stag")
#    PatCopyInst.collectPatFromRelease("I:\\hdmxpats\\x76\\Msoc_array\\A0","pat","Prod")
#    PatCopyInst.CheckNewPat()
#    PatCopyInst.PrntCopyFile("patCpy.bat","I:\\hdmxpats\\x76\\Msoc_array\\A0\\p01\\pat")
    MTTInst = genMTTConf()
    MTTInst.readMTTList("C:\\Users\\tli56\\PycharmProjects\\github\\inputs\\MTT_Patmod_Config_File.input")
    MTTInst.PrntMTTConf("C:\\Users\\tli56\\PycharmProjects\\github\\outputs\\MTT_Patmod_Config_File.txt")





