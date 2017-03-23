# Reel Algorithm

Source code for the Reel movie recommender algorithm and movie recommendation server are contained in this repository.

The movie recommender algorithm uses the MovieLens dataset as past data to derive new recommendations. This dataset is not included with this repository. Instructions on how to obtain this dataset are included in the [obtaining data subsection](#obtaining-data).

## Setup

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

### Obtaining Data

The data we use to make movie recommendations is compiled by researchers in the University of Minnesota GroupLens Research group.

* We are using the [MoviesLens latest dataset](http://files.grouplens.org/datasets/movielens/ml-latest.zip).
* Other (smaller) datasets are available on [MovieLens datasets page](https://grouplens.org/datasets/movielens/).
* Download the appropriate dataset into the `data/movielens/` directory and decompress

Alternatively, download all the datasets at once by typing `bash data-download.sh` from the root of this repository.

## API

Send all queries to localhost port 5000 as POST requests with a corresponding JSON file in the data section.

### Single User Recommendations
URL: http://localhost:5000/recommendations

JSON:

```
{
	"user": string,
	"num_recs": int (optional, defaults to 100)
	"ratings": [
		{
			"rating": string (must be to star rating between 0.5 and 5.0)
			"imdb": string (must be valid IMDB identifier)

		},

		...

	]
}
```

### Group Recommendations
URL: http://localhost:5000/group_recommendations

JSON:

```
{
	"group": string
	"num_recs": int (optional, defaults to 100)
	"users": list of single user recommendations JSON (without "num_recs" field)
}

```




## Data Description

The MovieLens datasets contains 3 csv files that we are using data from.

* movies.csv (3 fields)
  * `movieId`: unique integer identifer for each movie
  * `title`: the title of the movie (with release year in parenthesis)
  * `genres`: a pipe separated list of genres
* ratings.csv (4 fields)
  * `userId`: unique integer identifier for each user
  * `movieId`: cross-references the movie ids in movies.csv
  * `rating`: star rating (in half-star increments from .5 to 5.0)
  * `timestamps`: when the user made the rating (in seconds since 1970)
* links.csv (3 fields)
  * `movieId`: cross-references the movie ids in movies.csv
  * `imdbId`: imdb identifier for given movie
  * `tmdbId`: tmdb identifier for given movie


## Development

* Do all development work inside of a virtualenv. Instructions for setup of virtualenv are descried above.
  * After installing new dependencies with `pip` on your local machine, update the requirements.txt file so that your environment will be reproducible.
    * `pip freeze > requirements.txt`

* This project mainly utilizes `flask` to create REST API endpoints, and `scipy` for recommending movies.
