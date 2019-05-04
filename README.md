# BoBo-C-C
Command and Control with Exfiltration


               *********               B B B            B B B
             *************             B    B           B    B
            *****     *****            B     B  O O O   B     B  O O O
           ***           ***           B B B   O     O  B B B   O     O
          ***             ***          B    B   O O O   B    B   O O O
          **    0     0    **          B     B          B     B
          **               **          B B B            B B B
          ***             ***             //////////
          ****           ****        ///////////////
          *****         *****    ///////////////////
          ******       ******/////////         |  |
        *********     ****//////               |  |
     *************   **/////*****              |  |
    *************** **///***********          *|  |*
   ************************************    ****| <=>*
  *********************************************|<===>*
  *********************************************| <==>*
  ***************************** ***************| <=>*
  ******************************* *************|  |*
  ********************************** **********|  |*

SMaster folder(Server):

To try out locally, go to BoBo.py and comment out the line with heroku_port and 
make the port equal the number you want and run it with this command:

python BoBo.py runserver

To access the server running on heroku cloud got shop-nike.com

The password is 'Bobo'

You can click on the bots connected and interact with the bot by running commands.
Runnable commands:

<any shell command>
Executes command in a shell and returns output.

upload <local_file>
Uploads file to server.

download <url> <destination>
Download file over HTTP

exit
Kill Agent
"""

Bots folder(Client):

run the client in linux with the command:

python client.py

You could change the SERVER to http://IP:PORT in config.py in bots

SERVER = "http://IP:PORT"
INTERVAL = int time in seconds between packets that are sent
IDLE = int time in seconds before it times out
MAX_FAILED = int times it will try to connect and fail before exitting the program
