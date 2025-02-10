import string
import random
from prepare_citations import *
from utils import *

class TextGenerator():

    def __init__(self,n = 3):

        self.n = n
        self.contexts = dict()
        self.ngrams = dict()
        self.corpus_vocab = {'<start>'}

    def tokenize(self,input_text):
        '''Method to tokenize a text given as input'''

        text = input_text.lower()

        for p in string.punctuation:

            #Separate each punctuation mark in the input text
            if(p == '>' or p == '<'):
                pass
            else:
                text = text.replace(p,' '+p+' ')

        return text.split()

    def random_selection(self,top_results):
        '''Method to select randomly among results'''

        #If bigram does not exist (probability is 0)
        if(top_results[0][1] == 0):
            return random.choice(top_results)[0]

        cumul_sum = 0
        for result in top_results:
            cumul_sum += result[1]

        #Start randomizer
        r = random.uniform(0,cumul_sum)

        cumul_sum = 0
        #Cumulative probability to get the token
        while True:
            for result in top_results:
                cumul_sum += result[1]
                if(cumul_sum > r):
                    return result[0]



    def update_corpus_vocabulary(self,text):
        '''Method to update the vocabulary of the corpus'''

        self.corpus_vocab.update(set(text))


    def count_ngram(self,input_text):
        '''Method to update the n-1 grams and ngrams counts'''

        text = (self.n-1)*['<start>']+input_text

        for i in range(len(text) - (self.n-1)):

            context = tuple(text[i+pos] for pos in range(self.n-1))
            ngram = tuple(text[i+pos] for pos in range(self.n))

            if context in self.contexts.keys():
                self.contexts[context] += 1
            else:
                self.contexts[context] = 1

            if ngram in self.ngrams.keys():
                self.ngrams[ngram] += 1
            else:
                self.ngrams[ngram] = 1

    def predict_next_word(self,input_context,top = 10):
        '''Method to predict the next word given a context as input'''

        context_lower = input_context.lower()

        #Get the last bigram of the input context
        index = self.n-1
        context = self.tokenize(context_lower)[-index:]

        #Initiate the table of probabilities
        probabilities = dict()

        for word in self.corpus_vocab:

            #Form the trigram with the word
            ngram = [context[0+pos] for pos in range(self.n-1)] + [word]
            ngram = tuple(e for e in ngram)
            #Form the bigram
            context = tuple(context[0+pos] for pos in range(self.n-1))

            #Get the count of the bigram and the trigram
            ngram_count = self.ngrams.get(ngram, 0)
            context_count = self.contexts.get(context, 0)

            #Compute the probability and store it
            probability = 0
            if(context_count > 0):
                probability = ngram_count / context_count
            probabilities[word] = probability

        return self.random_selection(sorted(probabilities.items(), key=lambda x: x[1], reverse=True)[:top])

    
    def predict_text(self,input_context,max_length = 100,length = 10):
        '''Method to predict an entire text from a given context as input'''

        output = input_context
        result = ""
        new_token = self.tokenize(input_context)[(-self.n-1):][1]
    
        i = 0
        size_reached = False
        condition = True

        #Generation loop
        while(condition):

            new_token = self.predict_next_word(output)
            output = output + ' ' + new_token
            
            if(new_token != "<start>"):

                if(result == ""):
                    result = new_token
                else:
                    result = result + ' ' + new_token
            i += 1

            #Reach the length condition
            if(i >= length):
                size_reached = True

            #Last condition to finish sentence
            if(new_token == '.'):
                condition = False
            
            if(i >= max_length):
                condition = False

        return result

    def train(self,sentences):
        '''Method to train and count ngrams from a given input text (list of sentences)'''

        for sentence in sentences:

            text = self.tokenize(sentence)

            self.update_corpus_vocabulary(text)

            self.count_ngram(text)


