from bs4 import BeautifulSoup
import argparse
import re
 

parser = argparse.ArgumentParser(description="Script for modifying Keyword Tests in bulk to disable Browser operations, so that they can be used with environments specified in the Execution Plan",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-v", "--verbose", action="store_true", help="increase verbosity")
parser.add_argument("-o", "--overwrite",  action="store_true", help="replace the source file with the altered version")
parser.add_argument("filename", help="Keyword Test input filename")
args = parser.parse_args()
config = vars(args)
# Reading the data from an XML Keyword Test
KDT=config["filename"]
VERBOSE=config["verbose"]
OVERWRITE=config["overwrite"]

# Print messages to console iff Verbose is set to True
def logger(message):
    if VERBOSE: 
        print(message)
    

# Function to loop through the XML identifying all instances of a given type of Operation 
# There are two types of browser operation, and we want to disable both types
# We disable by inserting the tag <CommonData Disabled='True'> before the Parameters tag
# Then we return the altered XML
def disableBrowser(OpType, searchData):
    
    for operation in searchData.find_all('Operation', {'Type': OpType}):
        data_element = operation.Data
        if not data_element.find('CommonData', {'Disabled':'True'}):
            logger("==== Found Enabled Browser Instance =====\n" + OpType)
            data_element.Parameters.insert_before(disableTag)
    return searchData

# Show the input options 
logger(config)

with open(KDT, 'r') as file:
    # Loading the XML
    data = file.read()
    # Create a DOM object
    ordered_data = BeautifulSoup(data, 'xml')
    # Use the DOM to compose our disable Tag element
    disableTag = ordered_data.new_tag('CommonData')
    disableTag['Disabled'] = 'True'
    # identify and update the first of our Browser Operation Types ( {1B5F17B2-4691-45F4-A91F-F5CFF1E09C4E} )
    # we then feed that output back into a new, altered DOM so we can run it again for the second Browser Operation Type
    modified_data = BeautifulSoup(disableBrowser('{1B5F17B2-4691-45F4-A91F-F5CFF1E09C4E}', ordered_data).prettify(), 'xml')
    # identify and update the second of our Brwser Operation Types ( {98EACF50-FA7B-4595-8EDC-4C0B21157A52} )
    final_data = disableBrowser('{98EACF50-FA7B-4595-8EDC-4C0B21157A52}', modified_data)

    logger(final_data.prettify())
# Output our modified XML
# Temporary Output File if we haven't selected to Overwrite the source file 
outfileName = "outputfile.xml"
if OVERWRITE: outfileName = KDT
logger(outfileName)
output_file = open(outfileName, "w")
# inject out prettified XML into the file 
output_file.write(final_data.prettify())
output_file.close()