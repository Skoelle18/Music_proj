# Music_proj
1) Installing Correct Python Version
   You need to install python 3.10.11 for this project

once you're done installing, go to the vs code terminal of the project folder and type: `python --version` and press enter. It should display `Python 3.10.11`

2) Installing the Libraries for this project

  once this step is done, type `pip install mido python-rtmidi` in the vs code terminal and press enter.

3) Installing/Configuring VLC media player to play .midi files
   Go to your browser and install VLC media player. open VLC media player and then click on tools. A drop down menu will pop up, select         preferences in the drop down menu.
   A settings GUI will now be seen on your screen. Go to the bottom left of this gui, where you see the options for `show settings`. Select     ALL.
  You will see a new gui, with `Search` on the top left corner. Click on the search bar and enter `midi`. You will see an option on the        left called `audio codecs`. Click on `audio codecs`, you will see the option for `Soundfont file` on the right. Click on browse, navigate     to your project folder and select the file named `FluidR3_GM.sf2` which you get after extracting from the zip file `FluidR3_GM` located      in this repository.Click on `Save` button on the bottom right.

  You are done with the setup. Run the python script in vs code. It should generate a .midi file in the project folder

  Test the .midi file generated in VLC media player.
