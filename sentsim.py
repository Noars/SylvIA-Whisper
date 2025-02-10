from jiwer import wer
from Levenshtein import distance as lev

def wer_sentences_similarity(input_sentence,sentence_list,top = 0):
    """
    Compute the similarity between an input sentence and a list of sentences thanks to a WER evaluation.
    Arguments:
        input_sentence: string (input sentence)
        sentence_list: list of string (list of sentences)
        top (optional): integer (if 0 returns the best sentence, else if greater than 0, returns the k best sentences)
    Returns:
        sim_list: list of tuple (sentence,similarity)
    """

    sim_list = []

    for sentence in sentence_list:
        #Bijective function : 1 / (WER + 1) in case of comparison with similarity score.
        sim_list.append((sentence,1/(wer(input_sentence,sentence)+1)))
    
    sim_list.sort(key = lambda x: x[1])
    sim_list.reverse()

    if(top > 0):
        return sim_list[0:top]
    else:
        return sim_list[0]

def cer_sentences_similarity(input_sentence,sentence_list,top = 0):
    """
    Compute the similarity between an input sentence and a list of sentences thanks to a CER evaluation (Levenshtein Distance).
    Arguments:
        input_sentence: string (input sentence)
        sentence_list: list of string (list of sentences)
        top (optional): integer (if 0 returns the best sentence, else if greater than 0, returns the k best sentences)
    Returns:
        sim_list: list of tuple (sentence,similarity)
    """

    sim_list = []

    for sentence in sentence_list:
        #Bijective function : 1 / (CER + 1) in case of comparison with similarity score.
        sim_list.append((sentence,1/(lev(input_sentence,sentence)/len(sentence)+1)))
    
    sim_list.sort(key = lambda x: x[1])
    sim_list.reverse()

    if(top > 0):
        return sim_list[0:top]
    else:
        return sim_list[0]


def windowed_cer_sentences_similarity(input_sentence, sentence_list, top = 0):
    """
    Compute the similarity between an input sentence and a list of sentences thanks to a windowed CER evaluation (Levenshtein Distance).
    Arguments:
        input_sentence: string (input sentence)
        sentence_list: list of string (list of sentences)
        top (optional): integer (if 0 returns the best sentence, else if greater than 0, returns the k best sentences)
    Returns:
        sim_list: list of tuple (sentence,similarity)
    """

    sim_list = []

    for sentence in sentence_list:

        sentence_size = len(sentence)
        input_size = len(input_sentence)

        if(input_size <= sentence_size):
            #Bijective function : 1 / (CER + 1) in case of comparison with similarity score.
            sim_list.append((sentence,1/(lev(input_sentence,sentence)/len(sentence)+1)))
        
        else:
            j = sentence_size
            max_size = input_size

            for i in range(max_size):

                cut = input_sentence[i:j]

                if(j <= max_size):

                    #Bijective function : 1 / (CER + 1) in case of comparison with similarity score.
                    sim_list.append((sentence,1/(lev(cut,sentence)/len(cut)+1)))

                j = j + 1

    sim_list.sort(key = lambda x: x[1])
    sim_list.reverse()

    if(top > 0):
        return sim_list[0:top]
    else:
        return sim_list[0]
