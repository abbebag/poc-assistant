# poc-assistant
Proof of concept virtual assistant in python using Tesseract (https://github.com/tesseract-ocr/tesseract) and PyAutoGUI (https://github.com/asweigart/pyautogui). Whisper (https://github.com/openai/whisper) support coming soon 

## Installation and Usage
NOTE: The code currently works on MacOS only and installation is quite complicated

### With UTM
The current development workflow uses UTM (https://github.com/utmapp/UTM) to virtualize the "assistant"  

#### Setup virtual instance  
1. Download UTM (https://github.com/utmapp/UTM)
2. Create and open a virtual MacOS instance with default settings
3. Install Python
4. Follow installation requirements for Tesseract (https://tesseract-ocr.github.io/tessdoc/Installation.html#macos)
5. Clone or download this repository
6. Create and activate a virtual environment (optional)
7. `pip install -r requirements.txt`

#### Setup and run the command server locally  
1. Clone the repository
2. Create and activate a virtual environment (optional)
3. run `serv.py` (using Python 3, eg `python3 serv.py`

A server will start running locally on your IP address (found with eg `ipconfig getifaddr en0`). note it down

#### Open the client on the virtual instance
1. Set PORT in `main.py` to be the IP address above
2. run `main.py` (using Python 3)

Now you should be able to send commands from your local terminal window to the virtual instance.  
Try it with eg. `open TextEdit type Hello World! click File click Save type test press enter`

### Without UTM
coming soon

### Using Whisper (https://github.com/openai/whisper)
coming soon
