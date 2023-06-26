<video src="https://github.com/sourav-kanta/csgodemo_to_video/blob/main/sample%20video/demo_sample.mp4"/>

**Functionalities**
  1. Converts a CS GO demo file into a video file
  2. Skips from player death to next round directly
  3. Create a demo review of your match

**First time setup :**
  1. Install python on your system and install the following package : <i>pip install obs-websocket-py</i> for obs websocket python wrapper
  2. Install OBS and enable Websocket (Tools -> Websocket Server Settings). Tutorial : https://fms-manual.readthedocs.io/en/latest/audience-display/obs-integration/obs-websockets.html
  3. Make sure to <b>Untick Enable Authentication</b>
  4. Open the recording.cfg file from the code folder and modify the 10th line (spec_player_by_name _buddha#skinsmonkey_) to change to your username
  5. Update the demo file paths in recording.cfg according to your setup (line 7 and 9)
  6. Next copy this file to C:\Program Files (x86)\Steam\steamapps\common\Counter-Strike Global Offensive\csgo\cfg folder
  7. Open Steam and add the following to CS GO Launch option : _-insecure -condebug +exec recording_
  8. Download awp_mirage map from Steam workshop (Check by manually opening CSGO and typing map awp_mirage in console)
  9. Open the recorder.py file and update the 5 global variables as per your setup : _logFile, steamPath, vdmFile, tickfile, playername_

**Steps to run**
  1. Copy the demo file you want to convert to video in the **demo folder** inside your repository and rename to demo.dem
  2. cd to your _repository directory_, **keep obs open** and now you can run the script as : _python recorder.py_
  3. Output video name _demo.mkv_ will be created in  _<repository_directory>\\demo_ folder 

 

**Future Plans**
  1. Improve usability by automating these steps to run
  2. Add GUI with configuration options for global variables and create an executable
  3. Upload these videos to Youtube
  4. Create a webserver where these youtube videos can be shared for other people to review and give their feedback
