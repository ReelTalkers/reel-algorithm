#Reel Algorithm

Source code for the Reel movie recommender algorithm and movie recommendation server are contained in this repository.

The movie recommender algorithm uses the MovieLens dataset as past data to derive new recommendations. This dataset is not included with this repository. Instructions on how to obtain this dataset are included in the [obtaining data subsection](#obtaining-data).

##Setup

* Install `Python 3.4.3` (and `pip`)
  * On Ubuntu: `sudo apt-get install python3`
* Install `virtualenv` and `virtualenvwrapper`
  * On Ubuntu: `sudo pip install virtualenv virtualenvwrapper`
* Add the following to your bashrc (accessed by typing `sudo nano ~/.bashrc`)
  * `export WORKON_HOME=~/Envs`
  * `source /usr/local/bin/virtualenvwrapper.sh`
* Recompile your bashrc
  * `source ~/.bashrc` or close and re-open terminal
* If this is the first time cloning the repository, create a new virtualenv
  * `mkvirtualenv venv`
* If you have previously cloned the repository, re-use the existing virtualenv from the previous step
  * `workon venv`
* Install the python dependencies
  * `pip install -r requirements.txt`
* To run the flask server
  * `python algorithm-server/app.py`
* When you are done, close the virtualenv
  * `deactivate`

If you run into any questions, consult [this article](http://timmyreilly.azurewebsites.net/python-with-ubuntu-on-windows/).

###Obtaining Data

The data we use to make movie recommendations is compiled by researchers in the University of Minnesota GroupLens Research group.

* We are using the [MoviesLens latest dataset](http://files.grouplens.org/datasets/movielens/ml-latest.zip).
* Other (smaller) datasets are available on [MovieLens datasets page](https://grouplens.org/datasets/movielens/).

####Data Setup

* Download the zip file into the main directory of the project.
* Decompress and rename the directory `data/`

##Development

* Do all development work inside of a virtualenv. Instructions for setup of virtualenv are descried above.
  * After installing new dependencies with `pip` on your local machine, update the requirements.txt file so that your environment will be reproducible.
    * `pip freeze > requirements.txt`

* This project mainly utilizes `flask` to create REST API endpoints, and `scipy` for recommending movies.