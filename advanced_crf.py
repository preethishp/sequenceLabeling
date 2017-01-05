import os
import argparse
import pycrfsuite
import hw3_corpus_tool

def featureExtract(dialog, prevSpeakerChanged, isFirstUtterance, isExlamation, isAWhWord):
    features = ['0', '0','0','0']
    if prevSpeakerChanged:
        features[0] = '1'

    if isFirstUtterance:
        features[1] = '1'

   # if isAQuestion:
        #features[2] = '1'

    if isExlamation:
        features[2] = '1'

    if isAWhWord:
        features[3] = '1'

    #if isALaughter:
        #features[3] = '1'

    #if isAUh:
        #features[4] = '1'
    # features = [prevSpeakerChanged, isFirstUtterance]
    tokenList = []
    posList = []
    # print(len(dialog.pos))
    # for item in dialog.pos:
    # tokenList.append('TOKEN_'+item.token)
    if dialog.pos != None:
        tokenList = ['TOKEN_' + PosTagIns.token for PosTagIns in dialog.pos]
        posList = ['POS_' + PosTagIns.pos for PosTagIns in dialog.pos]
        features.extend(tokenList)
        features.extend(posList)

    return features

def isQuestion(text):
    if text == None:
        return False
    if text.find("?") != -1:
        return True
    else:
        return False

def isWhWord(text):
    if text==None:
        return False
    text = text.lower()
    if text.find("wh"):
        return True
    else:
        return False

def isLaughter(text):
    if text == None or text.find("Laughter") == -1:
        return False
    else:
        return True

def isUh(text):
    if text == None or (text.find("Uh,") == -1 and text.find("uh,") == -1):
        return False
    else:
        return True


def isAnExclamation(text):
    if text == None or (text.find("!") == -1):
        return False
    else:
        return True


if __name__ == '__main__':
    storePath = os.getcwd()

    parserObj = argparse.ArgumentParser()
    parserObj.add_argument("INPUTDIR", help="Specify the input directory")
    parserObj.add_argument("TESTDIR", help="Specify the test directory")
    parserObj.add_argument("OUTPUTFILE", help="Specify the output file")
    argList = parserObj.parse_args()
    inputdirecPath = argList.INPUTDIR
    testdirecPath = argList.TESTDIR
    outputFilePath = argList.OUTPUTFILE

    lenOfList = 0
    lenOfFirstDialogUtter = 0

    j = 0

    listOfFeaturesForAllFilesX = []
    listOfFeaturesForAllFilesY = []
    # tot = 0
    for dialogUtter, dialogFileName in hw3_corpus_tool.get_data(inputdirecPath):

        i = 0
        isFirstUtterance = True
        currSpeaker = ''
        prevSpeaker = ''
        prevSpeakerChanged = False
        isPrevSentQues = False
        isPrevExclamation = False
        isPrevWhWord = False
        for dialog in dialogUtter:
            currSpeaker = dialog.speaker

            if i != 0:
                if currSpeaker == prevSpeaker:
                    prevSpeakerChanged = False
                else:
                    prevSpeakerChanged = True
            if i == 1:
                isFirstUtterance = False

            listOfFeaturesForAllFilesX.append(featureExtract(dialog, prevSpeakerChanged, isFirstUtterance, isPrevExclamation, isPrevWhWord))
            #listOfFeaturesForAllFilesX.append(
                #featureExtract(dialog, prevSpeakerChanged, isFirstUtterance, isQuestion(dialog.text),isLaughter(dialog.text), isUh(dialog.text)))
            listOfFeaturesForAllFilesY.append(dialog.act_tag)
            isPrevSentQues = isQuestion(dialog.text)
            isPrevExclamation = isAnExclamation(dialog.text)
            isPrevWhWord = isWhWord(dialog.text)
            prevSpeaker = currSpeaker
            i += 1

        j += 1

    trainer = pycrfsuite.Trainer(verbose=False)

    trainer.append(listOfFeaturesForAllFilesX, listOfFeaturesForAllFilesY)

    trainer.set_params({
        'c1': 1.0,
        'c2': 0.5,
        'max_iterations': 75,  # stop earlier
        'feature.possible_transitions': True,
        'feature.possible_states' : True
    })
    trainer.train('conll2002-esp.crfsuite')

    tagger = pycrfsuite.Tagger()
    tagger.open('conll2002-esp.crfsuite')
    # lenOfListTest =0
    j = 0
    with open(outputFilePath, "w") as fileHandle:
        fileHandle.write("")

    for dialogUtterTest, dialogFileName in hw3_corpus_tool.get_data(testdirecPath):

        with open(outputFilePath, "a") as fileHandle:
            fileHandle.write('Filename="' + dialogFileName + '"\r\n')
            i = 0
            isFirstUtterance = True
            currSpeaker = ''
            prevSpeaker = ''
            prevSpeakerChanged = False
            isPrevSentQues = False
            isPrevExclamation = False
            isPrevWhWord = False
            listOfFeaturesInAFile = []
            for dialog in dialogUtterTest:
                currSpeaker = dialog.speaker

                if i != 0:
                    if currSpeaker == prevSpeaker:
                        prevSpeakerChanged = False
                    else:
                        prevSpeakerChanged = True
                if i == 1:
                    isFirstUtterance = False

                #listOfFeaturesInAFile.append(featureExtract(dialog, prevSpeakerChanged, isFirstUtterance, isQuestion(dialog.text)))
                listOfFeaturesInAFile.append(
                    featureExtract(dialog, prevSpeakerChanged, isFirstUtterance, isPrevExclamation, isPrevWhWord))
                isPrevSentQues = isQuestion(dialog.text)
                isPrevExclamation = isAnExclamation(dialog.text)
                isPrevWhWord = isWhWord(dialog.text)
                #listOfFeaturesInAFile.append(
                    #featureExtract(dialog, prevSpeakerChanged, isFirstUtterance, isQuestion(dialog.text), isLaughter(dialog.text), isUh(dialog.text)))
                prevSpeaker = currSpeaker
                i += 1
            listOfLabels = tagger.tag(listOfFeaturesInAFile)
            for label in listOfLabels:
                fileHandle.write(label + '\r\n')

            fileHandle.write('\r\n')
        j += 1
