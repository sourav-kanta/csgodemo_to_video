**Functionalities**
  1. Converts a CS GO demo file into a POV video file
  2. Skips from player death to next round directly
  3. Create a demo review of your match

**First time setup :**
  1. Install python on your system and install the required package : <i>pip install -r requirements.txt</i> for obs websocket python wrapper
  2. Install OBS and enable Websocket (Tools -> Websocket Server Settings). Tutorial : https://fms-manual.readthedocs.io/en/latest/audience-display/obs-integration/obs-websockets.html
  3. Make sure to <b>Untick Enable Authentication</b>
  4. Open Steam and add the following to CS GO Launch option : _-insecure -condebug +exec recording_
  5. Download awp_mirage map from Steam workshop (Check by manually opening CSGO and typing map awp_mirage in console)

**Steps to run**
  1. Start application by :
     1. cd to your _repository directory_
     2. python MainMenu.py
     ![image](https://github.com/sourav-kanta/csgodemo_to_video/assets/15877038/d219878a-bbeb-42a0-8518-4a147e2af624)
  2. Click on Change Setup button and select the neccessary files and folders. Input the name you played in the demo with and click OK.
     ![image](https://github.com/sourav-kanta/csgodemo_to_video/assets/15877038/1096f7cb-da95-4b5a-93b6-ffd196137845)
  3. Click on Start Gnerating Video to start the recording process
     ![image](https://github.com/sourav-kanta/csgodemo_to_video/assets/15877038/2e57033c-4488-4fa5-8634-814718f65d8d)
  4. Output video name _demo.mkv_ will be created in the demo_ folder 

**Future Plans**
  1. Package application to an executable
