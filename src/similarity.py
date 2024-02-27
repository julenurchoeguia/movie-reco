import typing 
import torch
from pytorch_pretrained_bert import BertTokenizer, BertModel, BertForMaskedLM

def get_emdeddinga(list_of_words:typing.List):
    bert_embedding = BertEmbedding()
    result = bert_embedding(list_of_words)
    return result