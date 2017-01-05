import argparse
import os
import extractData

if __name__ == '__main__':
    parserObj = argparse.ArgumentParser()
    parserObj.add_argument('DEVDIR',help='Specify the test directory')
    parserObj.add_argument('OPFILE',help='Specify the output file')

    argList = parserObj.parse_args()
    devDir = argList.DEVDIR
    opFile = argList.OPFILE
    labelDictForAllFiles = {}
    store = False
    i = 0
    with open(opFile,'r') as outputFileHandle:
        listOfLables = []
        currFileName = ''
        prevFileName = ''
        for line in outputFileHandle:
            if line != '\n':
                if line.find("Filename=") != -1:
                    if i!=0:
                        currFileName = line.split('\"')[1].strip('\n')
                        labelDictForAllFiles[prevFileName] = listOfLables
                        listOfLables = []
                    else:
                        currFileName = line.split('\"')[1].strip('\n')

                    #listOfLables.append(line.strip('\n'))
                else:

                    listOfLables.append(line.strip('\n'))
                prevFileName = currFileName
            i+=1
        labelDictForAllFiles[prevFileName] = listOfLables
    #print(labelDictForAllFiles['0808.csv'])
    correctlyClassified = 0
    noOfDialogues = 0
    for dialogUtter, dialogFileName in extractData.get_data(devDir):
            dialogNum = 0

            for dialog in dialogUtter:
                if dialog.act_tag == labelDictForAllFiles[dialogFileName][dialogNum]:
                    correctlyClassified += 1
                dialogNum+=1
            noOfDialogues += (dialogNum+1)
    print(correctlyClassified, noOfDialogues)
    accuracy = (correctlyClassified/noOfDialogues) * 100
    print(accuracy)