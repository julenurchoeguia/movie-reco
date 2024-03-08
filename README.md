
# Movie Recomendation System

## Presentation

This repository contains a movie reconmendation streamlit app based on Wikidata Knowledge Graph.
Follow the link to open the app on streamlit cloud:

[![Streamlit App](https://img.shields.io/badge/movie_reco-streamlit_app-red)](https://movie-reco.streamlit.app/)

## How does it works?

The user uses the search bar to find movies he likes. Once he has add all the movies he likes to his list. He exeute the search.

The search engine will first gather all the movies linked to the users list ( 1-Hop Ripple Set). Then it will compute the cosine similarity between the set of topics of the listed movies and the set of topics of each candidate from the 1-Hop Ripple Set.

Finally, it will return the top N closest movies, where N is a parameter passed by the user.

## Technical specifications

We use Wikidata Knowledge Graph and we compute the 1-Hop Ripple Set of a movie as the union of the following sets :
- The movies that have the same `genre` released within ± 10 years from the original movie release date
- The movies with the same `directors` than the original movie
- The movies with common `mainSubjects` released within ± 10 years from the original movie release date


We tested multiple embedding models and we finally went with `text-embedding-3-small` from OpenIA

