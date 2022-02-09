/**
 *@file abstractor.c
 *@author Ozan Kılıç 
 *
 *@brief The Abstractor is a multithread-powered research tool for scientific literature. It focuses on
 *delivering fast and accurate results for given queries. The program takes a query as an input,
 *scans its file collection, finds the most relevant abstracts by measuring the Jaccard similarities between
 *abstracts and the given query, then retrieves convenient sentences from the selected abstracts.
 */

#include <stdio.h>
#include <pthread.h>
#include <iostream>
#include <fstream>
#include <set>
#include <vector>
#include <cmath>
#include <iomanip> 
#include <algorithm>
#include <map>
using namespace std;

// mutex initializer is called to use mutex in the project
pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;

// alphabet to give thread names
char alphabet[26] = {'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'};

// text iterator intiger to hold last calculated text
int textIterator = 0;

// abstractNames vector to save paths of abstacts
vector<string> abstractNames;

// set query holds the words for the text which is compared with all other texts
set<string> query;

// below two vector of pairs are for holding a text's name, score, and abstract
vector< pair <string, double> > fileAndScore;
vector< pair <string, string> > fileAndAbstract;

// to hold output file name that is given as argument
string outputFileName;

// ofStream is for writing down to the output
ofstream myfile;

// Sortbysec function is to compare vector of pairs according to second elements. Returns true if first vector's second elm is greater than the first vector's second elm
bool sortbysec(const pair<string,double> &a,
              const pair<string,double> &b)
{
    return (a.second > b.second);
}


// calculateSimilarity function is used by threads to calculate Jaccard Similarities of texts and the query
void* calculateSimilarity(void *param) {

	// thread name is taking from method argument
	char threadName = *(char *) param;
	string textName;

	// threads run until all the given abstracts' Jaccard Similarities calculated.
	while(textIterator < abstractNames.size()){

		// mutex is used because text iterator is the critical section
		pthread_mutex_lock(&mutex);
		textName = abstractNames[textIterator];
		textIterator += 1;
		pthread_mutex_unlock(&mutex);

		// mutex is used because outputfile is the critical section
		pthread_mutex_lock(&mutex);
		// Opens the file and writes the result to the file given as argument
		myfile << "Thread " << threadName << " is calculating " << textName << endl;
		pthread_mutex_unlock(&mutex);
		
		// below section is to calculate Jaccard Similarity and summary sentence
		set<string> allWords;
		set<int> commonSentenceNumber;
		int commonWordCounter = 0;
		string currentSentence = "";
		string abstractSentence = "";
		bool isAbstractSentence = false;
		string fullPath = "../abstracts/" + textName;
		ifstream theText (fullPath);

		// this if opens the abstract file and traverse the words. If a word is common between the query and 
		// the abstract, the sentence the word is been is added to the abstractSentence(Summary sentence)
		// and the common word counter is incremented by one with every common word between the query and the abstract
		// allWords set is for holding unique elements. At the end common word counter and size of allWords is used
		// to calculate Jaccard Similarity.
		if ( theText.is_open() ) {
			while ( theText.good() ) {
				string theStr;
				theText >> theStr;
				currentSentence += " " + theStr;
				if(theStr == "."){
					if(isAbstractSentence){
						abstractSentence += " " + currentSentence;
						isAbstractSentence = false;
					}
					currentSentence = "";
					
				}
				if(query.find(theStr) != query.end()){
					isAbstractSentence = true;
					if(allWords.find(theStr) == allWords.end()){
						allWords.insert(string(theStr));
						commonWordCounter += 1;
					}
				}
				else{
					allWords.insert(string(theStr));
				}
			}          
		}
		
		// all elements of the query is added to the allWords set.
		allWords.insert(query.begin(), query.end());

		// Jaccard similarity is calculated.
		double score = (double)commonWordCounter / (double)(allWords.size());
		
		// mutex is used because the below two vectors are open to common use of the threads.
		pthread_mutex_lock(&mutex);
		fileAndScore.push_back(pair<string, double>(textName, score));
		fileAndAbstract.push_back(pair<string, string>(textName, abstractSentence));
		pthread_mutex_unlock(&mutex);

	}
    pthread_exit(NULL);
}


int main(int argc, char *argv[]) {

	// below three parts are for taking argument variables.
	string inputFileName;
	inputFileName = argv[1];
	outputFileName = argv[2];

	// below four parts are for opening reading and writing files.
	fstream file;
	string inputLine;
	file.open(inputFileName.c_str());
	myfile.open (outputFileName);

	// below four parts are for taking program's parameters given in the input file.
	int numOfThreads, numOfAbstracts, numOfResults;
	file >> numOfThreads;
	file >> numOfAbstracts;
	file >> numOfResults;
	getline(file,inputLine);
	getline(file,inputLine);
	int abstractCounter = 0;
	for(int a = 0; a < numOfAbstracts; a++){
		string abstractName;
		getline(file,abstractName);
		abstractNames.push_back(abstractName);
	}

	// for loop is for taking words given as query in the input file.
	string word = "";
	for(auto x : inputLine){
		if ( x == ' '){
			query.insert(word);
			word= "";
		}
		else{
			word =word+x;
		}
	}
	query.insert(word);

	// threads are declared and created in the for loop. They start to run calculateSimilarity method when they are created.
	pthread_t threadIDs[numOfThreads];
	for(int i=0; i<numOfThreads; i++){
		pthread_create(&threadIDs[i], NULL, calculateSimilarity, &alphabet[i]);
	}

	// Wait for all the threads to be finished.
	int control = 0;
	while(control != numOfThreads){
		control = 0;
		for(int i=0; i<numOfThreads; i++){
			if (pthread_join(threadIDs[i], NULL) == 0){
				control +=1;
			}
		}
	}


	// Using sort() function to sort file vector by 2nd element(score)
    sort(fileAndScore.begin(), fileAndScore.end(), sortbysec);
	myfile << "###" << endl;
	for(int i=0; i<numOfResults; i++){
		myfile << "Result " << i+1 << ":" << endl;
		myfile << "File: " << fileAndScore[i].first << endl;
		myfile << "Score: " << fixed << setprecision(4) << fileAndScore[i].second << endl;
		for(int a=0; a<numOfAbstracts; a++){
			if(fileAndAbstract[a].first == fileAndScore[i].first){
				myfile << "Summary: " << fileAndAbstract[a].second << endl;
				break;
			}
		}
		myfile << "###" << endl;
	}

	myfile.close();
    return 0;
}
