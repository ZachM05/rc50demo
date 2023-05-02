# RC50 Monitoring Application

The main branch of this repo will allow a user to run a monitoring application for a Loctite Pulse RC50 Integrated Dispenser off their local device.

This demo is best when paired with a Robotic dispense, as the application can periodically poll the RC50 every few seconds as defined while the dispense is inactive, and then continuously poll the reservoir when dispensing for best results.

This demo utilizes Docker which allows light-weight containers to run code with specific purposes. The 4 containers running for this application are:
- Python container used to continuously monitor the RC50 and send data points when necessary
- Python container which receives messages from monitoring app and then stores them in a data base, as well as sends them to any clients connected through a webpage
- MongoDB container which hosts a database for files to be stored
- NextJS container which serves a website locally on the host device

To install Docker Desktop, follow the [instructions shown here](https://docs.docker.com/desktop/). If running on Windows, make sure to install Windows Subsystem for Linux (WSL2).

The files can be downloaded from the repository by clicking the "Code" dropdown in the top right, and clicking "Download ZIP".

After this, unzip the archive and double click on the start.cmd file. This will open the Docker containers in the background, and successfully host the website on your local machine.

You can then access the site at [http://localhost:3000](http://localhost:3000)