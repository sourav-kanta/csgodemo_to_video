**Functionalities**
  1. Converts a CS GO demo file into a POV video file
  2. Skips from player death to next round directly
  3. Create a demo review of your match

**Sample Video**
  <br/> <br/>[![IMAGE ALT TEXT HERE](https://img.youtube.com/vi/Et5iVpf-zuY/0.jpg)](https://www.youtube.com/watch?v=Et5iVpf-zuY) <br/> <br/>
  
**Steps to run**
  1. Start application by :
     1. Download and run the application from the Release tab
     <br/><br/>![image](https://github.com/sourav-kanta/csgodemo_to_video/assets/15877038/d219878a-bbeb-42a0-8518-4a147e2af624) <br/> <br/>
  2. Click on Change Setup button and select the neccessary files and folders. Input the name you played in the demo with and click OK.
     <br/> <br/>![image](https://github.com/sourav-kanta/csgodemo_to_video/assets/15877038/1096f7cb-da95-4b5a-93b6-ffd196137845)<br/> <br/>
  3. Click on Start Gnerating Video to start the recording process
     <br/> <br/>![image](https://github.com/sourav-kanta/csgodemo_to_video/assets/15877038/2e57033c-4488-4fa5-8634-814718f65d8d)<br/> <br/>
  4. Output video name _demo.mkv_ will be created in the demo_ folder 

**Executable Build Steps**
  1. Create a virtual environment and activate it
  2. Install dependencies with pip install -r requirements.txt
  3. Run the following command inside virtual environment : _pyinstaller --onefile --name "Demo To Video Convertor" --icon .\loop-arrow.ico --add-data "recording.cfg;." .\MainMenu.py --windowed_
  
**Future Plans**
  1. Create a youtube upload feature to upload these videos on youtube
  2. Create a website where these videos can be viewed and other users can then demo review through comments
