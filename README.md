**Functionalities**
  1. Converts a CS GO demo file into a video file
  2. Skips from player death to next round directly
  3. Create a demo review of your match

**Steps to run :**
  1. Install python 3 on your system and install the following package : <i>pip3 install obs-websocket-py</i> for obs websocket wrapper
  2. Install OBS and enable Websocket. Tutorial : https://fms-manual.readthedocs.io/en/latest/audience-display/obs-integration/obs-websockets.html
  3. Make sure to <b>Untick Enable Authentication</b>
  4. Keep CS open and alt tab to OBS. Create a new scene and add source as **Window Capture with window as the CS GO application**
  5. Open the recording.cfg file from the code folder and modify the 10th line (spec_player_by_name _buddha#skinsmonkey_) to change to your username
  6. Next copy this file to C:\Program Files (x86)\Steam\steamapps\common\Counter-Strike Global Offensive\csgo\cfg
  7. Open Steam and add the following to CS GO Launch option : _-insecure -condebug +exec recording_
  8. Download awp_mirage map from Steam workshop (Check by manually opening CSGO and typing map awp_mirage in console)
  9. Copy the demo file you want to convert to video in the **demo folder** 
  10. Open the recording.py file and update the following global variables as per your setup :
      _<br/>logFile = "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Counter-Strike Global Offensive\\csgo\\console.log"<br/>
      steamPath = "C:\\Program Files (x86)\\Steam\\"<br/>
      playername = 'buddha#skinsmonkey'_
  11. Close any open instances of csgo
  12. cd to your code directory, keep obs open and now you can run the script as : _python recording.py_

**Future Plans**
  1. Improve usability by automating these steps to run
  2. Add GUI with configuration options for global variables and create an executable
  3. Upload these videos to Youtube
  4. Create a webserver where these youtube videos can be shared for other people to review and give their feedback
