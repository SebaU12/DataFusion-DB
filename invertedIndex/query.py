#! /usr/bin/env python3
# coding: utf-8

import abc
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer

class Query:
    def __init__(self, index):
        self.index = index
        self.original_terms = ""
        self.terms = []
        self.most_recent_results = []

    def get_postings_lists(self, terms):
        self.original_terms = terms
        tokens = word_tokenize(terms)

        stop_words = set(stopwords.words("english")) 
        filtered_terms = [term for term in tokens if term.lower() not in stop_words]

        stemmer = SnowballStemmer("english")  
        self.terms = [stemmer.stem(term) for term in filtered_terms]

        results = {}

        for term in self.terms:
            try:
                results[term] = self.index[term]
            except KeyError:
                results[term] = []

        return results

    @abc.abstractmethod
    def execute(self, terms):
        if self.__class__.__name__ == "Query":
            print("Usa AndQuery o OrQuery.\n")
        return

    def print_results(self):
        if self.most_recent_results:
            print("%s (original): %s" % (self.__class__.__name__, self.original_terms))
            print("%s (stemmed): %s" % (self.__class__.__name__, " ".join(self.terms)))
            print("%s result(s) found: %s\n" % ("{:,}".format(len(self.most_recent_results)), ", ".join(map(str, self.most_recent_results))))
        else:
            print("Your search didn't return any results.\n")


class AndQuery(Query):
    def __init__(self, index):
        Query.__init__(self, index)

    def execute(self, terms):
        postings_lists = self.get_postings_lists(terms)
        try:
            self.most_recent_results = sorted(set(postings_lists[0]).intersection(*[set(postings_list) for postings_list in postings_lists[1:]]))
        except IndexError:
            self.most_recent_results = []

        return self.most_recent_results


'''
class OrQuery(Query):

    def __init__(self, index):
        Query.__init__(self, index)

    def execute(self, terms):
        postings_lists = self.get_postings_lists(terms)
        postings_lists = [posting for postings_list in postings_lists for posting in postings_list]

        postings_lists = sorted(postings_lists, key=lambda x: (postings_lists.count(x), -x), reverse=True)

        postings_lists_set = set()
        postings_lists_set_add = postings_lists_set.add

        self.most_recent_results = [posting for posting in postings_lists if not (posting in postings_lists_set or postings_lists_set_add(posting))]

        return self.most_recent_results'''