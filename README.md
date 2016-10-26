## Predicting movie genres with PyMongo and Doc2Vec. 

* Movies data taken from : [MovieLens Latest Datasets](http://grouplens.org/datasets/movielens/latest/)
* Utilising [GenSim models.doc2vec](https://radimrehurek.com/gensim/models/doc2vec.html)
* [PyMongo](https://api.mongodb.com/python/current/)

Prediction utilises movie's Title, Plot and Actors. 
[MongoDB](https://www.mongodb.com/download-center) document example: 

```
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

Create the doc2vec model file (use `--help` for more information): 

```
./modeller.py --db topics --coll movies --model example.model
```

Using the doc2vec model file (use `--help` for more information): 

```
./analyser.py --db topics --coll excluded_movies --model example.model

```

Output prediction example: 

```
INFO : Title: Terminator Genisys
INFO : Plots: When John Connor (Jason Clarke), leader of the human resistance, sends Sgt. Kyle Reese (Jai Courtney) back to 1984 to protect Sarah Connor (Emilia Clarke) and safeguard the future, an unexpected turn of events creates a fractured timeline. Now, Sgt. Reese finds himself in a new and unfamiliar version of the past, where he is faced with unlikely allies, including the Guardian (Arnold Schwarzenegger), dangerous new enemies, and an unexpected new mission: To reset the future...
INFO : Actual Genres: [u'Action', u'Adventure', u'Sci-Fi']
INFO : precomputing L2-norms of doc weight vectors
INFO : Most similar:  [(u'Adventure', 0.5624773502349854), (u'Action', 0.5235205292701721), (u'Animation', 0.5159382820129395)]
INFO :   

```