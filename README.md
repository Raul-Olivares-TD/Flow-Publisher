# Flow-Publisher
- This tool is an HDA for upload assets from Houdini to Flow/Shotgun/ShotGrid.
- This tool exports an asset from Houdini and uploads it to Google Drive, publishes it to Flow, and notifies via Discord.
- This tool is complemented by the Scene Builder to continue with the small development of the pipeline.
	- Creates a scene with all configured for the artist. (Scene Builder)
	- Upload flipbooks to review at Flow. (Flipbook to Flow)
	- Upload assets to Flow. (Flow Publisher)

## HOW TO INSTALL.
##### DIRECTORY MANAGEMENT

- Put the directory visualnoobs inside the directory otls at the path at the directory *$HFS* it is the documents directory, something like this: *"C:/Users/User/Documents/houdini20.5/"*.
- The result should be something like: *"C:/Users/User/Documents/houdini20.5/otls/visualnoobs"*.
	- This directory contains inside him 5 scripts to use the tool correctly:
		- **discordNotifier.py** -> This scripts notify via discrod.
		- **driveConnections.py** ->  This scripts upload the assets from Houdini to Google Drive.
		- **flowConnections.py** -> Creates the connections with Flow and gets all the data from Flow to Houdini.
		- **houdiniParameters.py** -> This scripts control all the logic for the Houdini parameters at the HDA.
		- **houdiniPublisher.py** -> This scripts control all the logic for export the assets.
- Put the HDA inside the directory otls at the path at the directory *$HFS* it is the documents directory, something like this: *"C:/Users/User/Documents/houdini20.5/"*.
- The result should be something like: *"C:/Users/User/Documents/houdini20.5/otls/td_publisher.otlIc"*.

##### HOUDINI.ENV

- Houdini have a houdini.env file in that we need to add this lines.
- Python Path -> For use the scpripts properly at Houdini.
		PYTHONPATH = "C:\Users\User\Documents\houdini20.5\otls\visualnoobs;C:\Users\User\Python\Python311\Lib\site-packages;C:\Users\User\Documents\houdini20.5\otls"
- Flow user -> In that line we must write the user that we have in Flow/ShotGrid/ShotGun.
		FLOW_USER = "email register at flow of each user" # Ex: "jj2inline@gmail.com"
- Discord user -> In that line we must write the user that we have in Discord.
		DISCORD_USER = "raul"
- Discord channel ->  In that line we must write the Discrod channel id to notify.
		DISCORD_CHANNEL = "1231231231231231223123"