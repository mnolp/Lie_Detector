# Small_Project
# INFO
A program to detect deception using balance data and audio features.
The data gathering tool only works on linux. 

# INSTALLATION
To run this program you need to install the sequent cpp libraries
- WiiC, installation guide at https://github.com/grandelli/WiiC
- SFML 2.4.2, sudo apt-get install libsfml-dev=2.4.2
- PostgreSQL, create a database from the .psql file in the root folder. Name it 'lie_detector'
- Create a python 3.6.9 virtual environment in the root folder with virtualenv. Install with pip the libraries in requirements.txt
- Put an existing "output" folder in the root directory or create an empty one.
