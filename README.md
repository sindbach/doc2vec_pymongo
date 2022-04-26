## Predicting movie genres with PyMongo and Doc2Vec. 

Utilising:

* [GenSim models.doc2vec](https://radimrehurek.com/gensim/models/doc2vec.html)
* [PyMongo](https://api.mongodb.com/python/current/)

Tested with : 

* Python v3.9
* PyMongo v4.1.1
* MongoDB v5.0
* GenSim v4.1

### Data

A very small set of data is provided with this repository for example purposes. There are two `json` files that are ready to import into a [MongoDB]([MongoDB](https://www.mongodb.com)) deployment. 

* Small set of data for training the model: [data/training.json](./data/training.json) 
* Small set of data for testing the output model: [data/test.json](./data/test.json)

To import the files into MongoDB you can use `mongoimport`: 

```sh
mongoimport --db topics --collection movies --file ./data/training.json
mongoimport --db topics --collection test --file ./data/test.json 
```

#### Custom Data

Essentially you need a MongoDB collection with document structure as below example: 

```json
{
  "_id": ObjectId("57ff3452b62f007fe3d033b9"),
  "Title": "Circle",
  "Plot": "In a massive, mysterious chamber, fifty strangers awaken to find themselves ...",
  "Actors": "Michael Nardelli, Allegra Masters, Molly Jackson, Jordi Vilasuso",
  "Year": "2015",
  "Genre": "Drama, Horror, Mystery",  
  "Language": "English",
  ...
}
```

You can either construct the document yourself, or fetch existing information from movies' sites. 

The example data was collected by fetching movies data from : [MovieLens Latest Datasets](http://grouplens.org/datasets/movielens/latest/). There's a file called `./ml-latest-small/links.csv` that contains `movieId`. This ID can be used to fetch the related movie information from [omdbapi.com](www.omdbapi.com). You would need to register and activate an API key. The site provides 1000 API calls per day for free. 

Use [build_dataset.py](./utils/build_dataset.py) script as an example to fetch more movies data from `omdbapi.com`. The script will output a `json` file that could be imported to MongoDB using `mongoimport`.

### Building a Model 

The prediction model utilises movie's `Title`, `Plot` and `Actors` fields. 
You can create a `doc2vec` model file using `modeller.py` command line. See `modeller.py --help` for more information. Below is an example command to read from database `topics` and collection `movies` to create a model file called `example.model`: 

```sh
./modeller.py --db topics --coll movies --model example.model
```

### Use the Model

Provide the generated `doc2vec` model file as input to `analyser.py` to predict the genres of movie(s). See `analyser.py --help` for more information. Below is an example command to read documents from database `topics` and collection `test` and predict the genres using `example.model`: 

```sh
./analyser.py --db topics --coll test --limit 3 --model example.model
```

Output example: 

```sh
INFO : Title: Terminator Genisys
INFO : Plots: When John Connor (Jason Clarke), leader of the human resistance, sends Sgt. Kyle Reese (Jai Courtney) back to 1984 to protect Sarah Connor (Emilia Clarke) and safeguard the future, an unexpected turn of events creates a fractured timeline. Now, Sgt. Reese finds himself in a new and unfamiliar version of the past, where he is faced with unlikely allies, including the Guardian (Arnold Schwarzenegger), dangerous new enemies, and an unexpected new mission: To reset the future...
INFO : Actual Genres: [u'Action', u'Adventure', u'Sci-Fi']
INFO : precomputing L2-norms of doc weight vectors
INFO : Most similar:  [(u'Adventure', 0.5624773502349854), (u'Action', 0.5235205292701721), (u'Animation', 0.5159382820129395)]
INFO :   
```
