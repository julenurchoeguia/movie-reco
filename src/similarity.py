
from openai import OpenAI
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import load_dotenv
import warnings
import typing
import json

load_dotenv.load_dotenv()
client = OpenAI()

def get_embedding(list_words:typing.List, model="text-embedding-3-small"):
    """
    This function returns the embeddings of a list of words.
    """
    for word in list_words:
        if not isinstance(word, str):
            raise ValueError("All the elements in the list must be strings.")
        if word == "":
            raise ValueError("The list must not contain empty strings.")
    response = client.embeddings.create(input = list_words, model=model)
    embeddings = []
    for word_embedding in response.data:
        embeddings.append(list(word_embedding.embedding))
    return embeddings

def max_similarity(embeddings1:typing.List, embeddings2:typing.List, nb_words:int=5):
    """
    This function returns the maximum similarity between two list of embeddings.
    """
    similarities = cosine_similarity(embeddings1, embeddings2).flatten()
    top_similarities = np.sort(similarities)[-nb_words:]
    return top_similarities.mean()

def average_vector_similarity(embeddings1:typing.List, embeddings2:typing.List):
    """
    This function returns the average similarity between two list of embeddings.
    """
    embeddings1_mean = np.mean(embeddings1, axis=0)
    embeddings2_mean = np.mean(embeddings2, axis=0)
    return cosine_similarity([embeddings1_mean], [embeddings2_mean])[0][0]


if __name__ == "__main__":
    embeddings1 = get_embedding(["Startup", "World"])
    embeddings2 = get_embedding(["Artificial Intelligence", "Machine Learning", "Netflix"])
    print(max_similarity(embeddings1, embeddings2))
    print(average_vector_similarity(embeddings1, embeddings2))
