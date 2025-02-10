import csv
import random

def get_sentence_by_id_from_csv(input_file):
    '''Function to get a dictionary with triggers id as key and triggers as values.'''

    with open(input_file, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile,delimiter=',')
        result = dict()

        next_row = next(reader)
        next_row = next(reader)

        for row in reader:
            result.update({row[0]:row[1]})
        
    return result

def get_association_by_id(input_file,triggers):
    '''Function to get a dictionary with triggers id as key and answers id as values.'''

    with open(input_file, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile,delimiter=',')

        #Building the dictionary with triggers as key
        result = dict()

        for keyid in triggers:
            result.update({keyid:[]})


        next_row = next(reader)
        next_row = next(reader)

        for row in reader:
            result[row[0]].append(row[1])

    return result



def get_sentence_from_dict(d):
    '''Function to get the list of the sentence from a dictionary'''

    l = []

    for i in dict.values(d):
        l.append(i)
    
    return l

def get_random_answer_from_trigger(d,trigger):
    '''Function that returns a random citation of a particular trigger'''

    return random.choice(d[trigger])


#Build the trigger dictionary
triggers = get_sentence_by_id_from_csv("res/citations/declencheuse.csv")

#Build the answer dictionary
answers = get_sentence_by_id_from_csv("res/citations/declencheuse.csv")

#Build the association dictionary
associations = get_association_by_id("res/citations/association.csv",triggers)

#Get a random answer from a trigger
r = get_random_answer_from_trigger(associations,"1")

#Get the list of triggers
l = get_sentence_from_dict(triggers)