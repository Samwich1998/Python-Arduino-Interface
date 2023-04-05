"""
    Written by Samuel Solomon
    
    --------------------------------------------------------------------------
    Data Aquisition:
        
    Plotting:
        If Plotting, You Need an GUI Backend -> In Spyder IDE Use: %matplotlib qt5
        Some IDEs (Spyder Included) may Naturally Plot in GUI.
    --------------------------------------------------------------------------
    
    Modules to Import Before Running the Program (Some May be Missing):
        pip install -U numpy scikit-learn matplotlib openpyxl pyserial joblib pandas
        pip install -U natsort pyexcel eeglib pyfirmata2 shap ipywidgets seaborn pyqt6
        pip install -U ipython qdarkstyle
        pip install --upgrade tensorflow
    
    Programs to Install:
        Vizard (If using Virtual Reality): https://www.worldviz.com/virtual-reality-software-downloads
        
    --------------------------------------------------------------------------
"""

# -------------------------------------------------------------------------- #
# ---------------------------- Imported Modules ---------------------------- #

# Basic Modules
import os
import sys
import numpy as np

sys.path.append('./Helper Files/')
# Import Data Aquisition and Analysis Files
import excelProcessing as excelDataProtocol       # Functions to Save/Read in Data from Excel
import streamData as streamDataProtocol      # Functions to Handle Data from Arduino

if __name__ == "__main__":
    # ---------------------------------------------------------------------- #
    #    User Parameters to Edit (More Complex Edits are Inside the Files)   #
    # ---------------------------------------------------------------------- #
    
    # Protocol Switches: Only the First True Variable Excecutes
    readDataFromExcel = False      # Analyze Data from Excel File called 'testDataExcelFile' on Sheet Number 'testSheetNum'
    streamData = True              # Stream in Data from the Board and Analyze;
    
    # User Options During the Run: Any Number Can be True
    plotStreamedData = True        # Graph the Data to Show Incoming Signals + Analysis
    
    # ---------------------------------------------------------------------- #
    
    # Analyze the Data in Batches
    numPointsPerBatch = 2000        # The Number of Data Points to Display to the User at a Time;
    moveDataFinger = 200            # The Minimum Number of NEW Data Points to Plot/Analyze in Each Batch;
    
    # Spec
    streamingOrder = ["ecg"]  # A List Representing the Order of the Sensors being Streamed in.

    # Save the Data as an Excel File (For Later Use)
    if streamData:
        # Arduino Streaming Parameters
        boardSerialNum = '85735313333351E040A0'   # Board's Serial Number (port.serial_number)
        stopTimeStreaming = 60*180   # If Float/Int: The Number of Seconds to Stream Data; If String, it is the TimeStamp to Stop (Military Time) as "Hours:Minutes:Seconds:MicroSeconds"
        
        saveRawSignals = True        # Saves the Data in 'readData.data' in an Excel Named 'saveExcelName'
        saveExcelName = "Data.xlsx"  # The Name of the Saved File
        saveDataFolder = "./Data/2022-11-17 First Trial/"   # Data Folder to Save the Excel Data; MUST END IN '/'
    else:
        boardSerialNum = None
        saveRawSignals = False
        
    # Instead of Arduino Data, Use Test Data from Excel File
    if readDataFromExcel:
        if not plotStreamedData:
            # If not displaying, read in all the excel data (max per sheet) at once
            numPointsPerBatch = 2048576
            moveDataFinger = 1048100 
        
        testSheetNum = 0   # The Sheet/Tab Order (Zeroth/First/Second/Third) on the Bottom of the Excel Document
        # testDataExcelFile = "./Test.xlsx" # Path to the Test Data
        testDataExcelFile = "./Data/ECG/2022-11-09 GSR.xlsx"   # Data Folder to Save the Excel Data; MUST END IN '/'

    # ---------------------------------------------------------------------- #
    # ---------------------------------------------------------------------- #
    #           Data Collection Program (Should Not Have to Edit)            #
    # ---------------------------------------------------------------------- #
    # ---------------------------------------------------------------------- #
    # Initialize instance to analyze the data
    readData = streamDataProtocol.mainArduinoRead(boardSerialNum, numPointsPerBatch, moveDataFinger, streamingOrder, [], plotStreamedData)

    # Stream in the data from the circuit board
    if streamData:
        readData.streamArduinoData(stopTimeStreaming, predictionModel = None, actionControl = None)
    
    # Take Data from Excel Sheet
    elif readDataFromExcel:
        # Collect the Data from Excel
        compiledRawData, experimentTimes, experimentNames, surveyAnswerTimes, surveyAnswersList, surveyQuestions, subjectInformationAnswers, subjectInformationQuestions = excelDataProtocol.getExcelData().getData(testDataExcelFile, numberOfChannels = len(streamingOrder), testSheetNum = testSheetNum)
        # Analyze the Data using the Correct Protocol
        readData.streamExcelData(compiledRawData, experimentTimes, experimentNames, surveyAnswerTimes, surveyAnswersList, 
                                 surveyQuestions, subjectInformationAnswers, subjectInformationQuestions, predictionModel = None, actionControl = None)
    
    # ---------------------------------------------------------------------- #
    # ------------------ Extract Data into this Namespace ------------------ #

    # Extract the data
    timePoints = np.array(readData.analysisList[0].data[0])
    ecgReadings = np.array(readData.analysisProtocol.data[1][0])
        
    # ---------------------------------------------------------------------- #
    # -------------------------- Save Input data --------------------------- #
    # Save the Data in Excel
    if saveRawSignals:
        # Double Check to See if User Wants to Save the Data
        verifiedSave = input("Are you Sure you Want to Save the Data (Y/N): ")
        if verifiedSave.upper() == "Y":
            # Get the streaming data
            streamingData = []
            for analysis in readData.analysisList:
                for analysisChannelInd in range(len(analysis.data[1])):
                    streamingData.append(np.array(analysis.data[1][analysisChannelInd]))
            # Initialize Class to Save the Data and Save
            saveInputs = excelDataProtocol.saveExcelData()
            saveInputs.saveData(timePoints, streamingData, [], [], [], [], [],
                                [], [], streamingOrder, saveDataFolder, saveExcelName)
        else:
            print("User Chose Not to Save the Data")
