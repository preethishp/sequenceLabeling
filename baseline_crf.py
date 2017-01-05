import os
import argparse
import pycrfsuite
import hw3_corpus_tool

def featureExtract(dialog, prevSpeakerChanged, isFirstUtterance):
    features = ['0', '0']
    if prevSpeakerChanged:
        features[0] = '1'

    if isFirstUtterance:
        features[1] = '1'

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
        for dialog in dialogUtter:
            currSpeaker = dialog.speaker

            if i != 0:
                if currSpeaker == prevSpeaker:
                    prevSpeakerChanged = False
                else:
                    prevSpeakerChanged = True
            if i == 1:
                isFirstUtterance = False

            listOfFeaturesForAllFilesX.append(featureExtract(dialog, prevSpeakerChanged, isFirstUtterance))
            listOfFeaturesForAllFilesY.append(dialog.act_tag)
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
        'feature.possible_states': True
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

                listOfFeaturesInAFile.append(featureExtract(dialog, prevSpeakerChanged, isFirstUtterance))
                prevSpeaker = currSpeaker
                i += 1
            listOfLabels = tagger.tag(listOfFeaturesInAFile)
            for label in listOfLabels:
                fileHandle.write(label + '\r\n')

            fileHandle.write('\r\n')
        j += 1
