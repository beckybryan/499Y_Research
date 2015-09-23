"""
Becky Bryan
499Y Research
Prof. Brian Levine

Phone Data Anaylsis

This program reads in data from a csv file of the form ID, Date, LAC. LAC is the "location area code," or the
unique code for each location area the user has visited. For every unique user in the file, a user object is 
created that stores the user's ID, Dates, and LACs stored in the file. The list of LACs are used to create a
count-transition matrix, a matrix that holds the counts of all transitions the user made between LACs. This count-transition
matrix is then used to create a probability-transition matrix, a matrix that holds the probability that the user
will make a certain transition.

Given a list of transitions, the probability-transition matrices can be used to guess which user made those transitions.

"""

#!/usr/bin/env python3

import sys
import csv
import collections
import math
import random
from decimal import *

class User:
	
	def __init__(self,id):
		self.user_id=id

	""" train_data
	Input: a string in the format 'year-month'. For example, 2004-01. This is the month to train the data on
	Use: trains the data based on the given month. It creates a count matrix for every LAC visited within the month. 
	The count matrix has a smoothing factor of 1 added to each cell. Each cell represents the number of transitions from one LAC
	(row) to another (column).
	Output: 0 if the date range does not apply to this user"""
	def train_data(self, train_year_month):
		#Retrieve a list of LACs visited in the given month

		date1 = train_year_month + "-00 00:00:00"
		date2 = train_year_month + "-99 99:99:99"

		lacs_trained = self.get_lac_by_date_range(date1, date2)

		#If the date range does not exist for this user, exit
		if(len(lacs_trained)==0):
			return 0

		self.unique_lac = set(lacs_trained)
		self.unique_lac = list(self.unique_lac)
		num_lac = len(self.unique_lac)

		#Initialize Count Matrix
		self.count_matrix = [[1 for x in range(num_lac)] for x in range(num_lac)]

		for row in range(num_lac):
			for col in range(num_lac):
				if(row==col):
					self.count_matrix[row][col]=0

		#Fill Count Matrix (ignoring self-transitions)
		row=0
		col=0

		for i in range(len(lacs_trained)-1):
			if(lacs_trained[i]!=lacs_trained[i+1]):
				row=self.unique_lac.index(lacs_trained[i])
				col=self.unique_lac.index(lacs_trained[i+1])
				self.count_matrix[row][col]+=1

		self.create_prob_matrix(num_lac)

		return 1


	""" create_prob_matrix
	Input: num_lac, the number of lacs visited by the user
	Use: Creates a probability matrix from the transition count matrix by dividing each cell of the count matrix by
	the total number of possible transitions 
	Output: N/A """
	def create_prob_matrix(self, num_lac):
		#Calculating number of unvisited LACs and the sum of each row
		self.num_unvisited = self.total_lac-num_lac 
		self.row_sum=[]

		for row in self.count_matrix:
			sum_row=0
			for val in row:
				sum_row+=val
			self.row_sum.append(sum_row)

		#Creating Probability Matrix (ignoring self-transitions)
		self.prob_matrix=[[0 for x in range(num_lac)] for x in range(num_lac)]

		for row in range(num_lac):
			for col in range(num_lac):
				if(self.count_matrix[row][col]!=0):
					self.prob_matrix[row][col]=self.count_matrix[row][col]/(self.row_sum[row]+self.num_unvisited)

		#Checks that each row of matrix adds to 1
		self.check_prob_matrix()

		del self.count_matrix #deallocates the memory storing count_matrices

	def get_ID(self):
		return self.user_id

	#Creates an empty list to store a list holding all LACs visited by user (including duplicates)
	def create_lac_list(self):
		self.lacs_visited=[]

	#Adding a LAC to the list (including duplicates)
	def add_lac(self,lac):
		self.lacs_visited.append(lac)

	#Checks to make sure each row in the probability matrix sums to 1
	def check_prob_matrix(self):
		row_index=0
		for row in self.prob_matrix:
			sum_row=Decimal(0)
			for val in row:
				sum_row+=Decimal(val)
			sum_row+=Decimal(self.num_unvisited)/Decimal(self.num_unvisited+self.row_sum[row_index]) #Accounts for all the LACs the user did not visit

			if(abs(Decimal(1) - sum_row) > 0.00000000001):
				print("ERROR: A row in probability matrix did not add up to one [user: %s] [sum: %d] [calc: %d]" % (self.user_id, sum_row, abs(1-sum_row)))
				print(row)
				exit()
			row_index+=1

	""" This method assumes that self transitions are ignored. Two locations (LACs) are passed in and 
	the probability of this user performing that transition is found calculated."""
	def get_prob(self, lac1, lac2):

		row=0
		col=0
		
		#Getting the indexes of the LACs to find row and column in the probability matrix
		#If the index does not exist, then the user did not use that LAC and the probability is returned (1/smoothing factor)

		if(lac1 in self.unique_lac):
			row = self.unique_lac.index(lac1)
		else:
			return 1/self.total_lac
			
		if(lac2 in self.unique_lac):
			col = self.unique_lac.index(lac2)
		else:
			return 1/(self.num_unvisited + self.row_sum[row])

		prob=self.prob_matrix[row][col]
		return prob


	""" A list of transitions is passed in. This method finds out the probability that this user made the 
	transitions. It returns the probability. """
	def calculate_probability(self, transitions):
		prob=0

		for i in range(len(transitions)-1):
			lac1=transitions[i]
			lac2=transitions[i+1]

			if(lac1!=lac2):
				prob+=math.log10(self.get_prob(lac1,lac2))
				
		return prob


	""" Sets the total number of LACS (used for smoothing factor) """
	def set_total_lac(self, num_lac):
		self.total_lac=num_lac

	""" Creates an empty dictionary that will hold the date as the key and LAC as the value. This will be used for Testing. """
	def create_date_list(self):
		self.dates=[]

	""" Adding dates visited to a list. This dictionary will be used for Testing. """
	def add_date(self, date):
		self.dates.append(date)

	""" Finds all the LACs visited by the user between a date range and returns the list (used for Testing). 
	Dates and Lacs Visited correlate to each other """
	def get_lac_by_date_range(self, date1, date2):
		lacs=[]

		for i in range(len(self.dates)):
			if(self.dates[i] >= date1 and self.dates[i] <= date2):
				lacs.append(self.lacs_visited[i])
		return lacs

	""" Print the date range of this user. Returns these values """
	def print_user_date_range(self):
		print("User ID: %s, " % self.user_id, end=" ")
		first=self.dates[0]
		last=self.dates[len(self.dates)-1]
		print("%s - %s" % (first, last))
		return(first, last)


def main():
	#Checking the number of arguments
	if(len(sys.argv)!=4):
		print("ERROR: Incorrect number of arguments")
		usage()

	#Catch exception on reading file
	try:
		filename=sys.argv[1]
		fd=open(filename)
	except:
		print("Error opening file:".sys.exc_info()[0])
		sys.exit()

	#Optional printing date ranges of all users
	if(sys.argv[2] == 'd'):
		users_dict = read_data(fd)
		print_date_ranges(users_dict)
		sys.exit()

	#If user manually enters a certain date range to test and train
	if(len(sys.argv[2]) == 7 and len(sys.argv[3]) == 7):
		train_year_month = sys.argv[2]
		test_year_month = sys.argv[3]
		users_dict = read_data(fd)
		users_dict = train_all_data(users_dict, train_year_month)
		write_to_file(users_dict, train_year_month, test_year_month)
		sys.exit()
	elif(sys.argv[2] == "a" and sys.argv[3]== "a"):	#Tests and trains on all data
		users_dict = read_data(fd)
		train_test_dates = [
			"2003-12",
			"2004-01",
			"2004-02",
			"2004-03",
			"2004-04",
			"2004-05",
			"2004-06",
			"2004-07",
			"2004-08",
			"2004-09",
			"2004-10",
			"2004-11",
			"2004-12",
			"2005-01",
			"2005-02",
			"2005-03",
			"2005-04",
			"2005-05",
			"2005-06",
			"2005-07",
		]
		for i in range(len(train_test_dates)-1):
			temp_users_dict = users_dict.copy()
			train_year_month = train_test_dates[i]
			test_year_month = train_test_dates[i+1]
			temp_users_dict = train_all_data(temp_users_dict, train_year_month)
			if(len(temp_users_dict) > 0):
				write_to_file(temp_users_dict, train_year_month, test_year_month)
		sys.exit()
	else:
		print("Error: Incorrect date ranges")
		usage()


""" write_to_file
Input: users_dict, dictionary of all users trained_users
Purpose: Opens and names a csv file. Tests all of the users based on the 'test_year_month' input. 
It tests the month, each week, each day, and each hour for all users (by calling other methods). 
Ouput: N/A (other than a CSV file saved)"""
def write_to_file(users_dict, train_year_month, test_year_month):

	output_file = open("%s - %s.csv" % (train_year_month, test_year_month), "wt")
	writer = csv.writer(output_file)
	writer.writerow(("Trace Duration", "Total Tested", "Correct", "Incorrect", "Accuracy"))

	test_month(users_dict, test_year_month, writer)
	test_week(users_dict, test_year_month, writer)
	test_day(users_dict, test_year_month, writer)
	test_hour(users_dict, test_year_month, writer)

	output_file.close()


""" test_hour
Input: users_dict, a dictionary of all users (already trained); test_year_month, year and month to test on (in form yyyy-mm)
Purpose: tests on every hour of the day in a month 
Output: N/A"""
def test_hour(users_dict, test_year_month, write_file):
	correct = 0
	incorrect = 0
	day_count = 1
	date1 = test_year_month + "-00 00:00:00"
	date2 = test_year_month + "-00 00:99:00"

	while(day_count < 31):
		for hour in range(1, 61):
			date1 = date1[:8] + ("%02d" % day_count) + date1[10] + ("%02d" % hour) + date1[13:]
			date2 = date2[:8] + ("%02d" % day_count) + date2[10] + ("%02d" % hour) + date2[13:]
			(c, i) = test_data(users_dict, date1, date2)
			correct += c
			incorrect += i
		day_count += 1

	total = correct + incorrect

	if(total > 0):
		accuracy = round(correct/total,5)
	else:
		accuracy = 0
	
	write_file.writerow(("hour",total,correct,incorrect,accuracy))


""" test_day
Input: users_dict, a dictionary of all users (already trained); test_year_month, year and month to test on (in form yyyy-mm)
Purpose: tests based on every day in a month
Output: N/A """
def test_day(users_dict, test_year_month, write_file):
	correct = 0
	incorrect = 0
	count = 1
	date1 = test_year_month + "-00 00:00:00"
	date2 = test_year_month + "-99 99:99:99"

	#refactor to use a for loop (for day in range(1,31):)?
	while(count < 31):
		date1 = date1[:8] + ("%02d" % count) + date1[10:]
		date2 = date2[:8] + ("%02d" % count) + date2[10:]
		(c, i) = test_data(users_dict, date1, date2)
		correct += c
		incorrect += i
		count += 1

	total = correct + incorrect

	if(total > 0):
		accuracy = round(correct/total, 5)
	else:
		accuracy = 0

	write_file.writerow(("day",total,correct,incorrect,accuracy))

""" test_week
Input: users_dict, dictionary of all users (already trained); test_year_month, year and month to test_year_month
Purpose: Tests based on each week of the month. The month is broken up into 4 weeks. Each week is 7 days long.
Output: N/A """
def test_week(users_dict, test_year_month, write_file):
	
	(correct1, incorrect1) = test_data(users_dict, test_year_month + "-00 00:00:00", test_year_month + "-07 99:99:99")
	(correct2, incorrect2) = test_data(users_dict, test_year_month + "-08 00:00:00", test_year_month + "-14 99:99:99")
	(correct3, incorrect3) = test_data(users_dict, test_year_month + "-15 00:00:00", test_year_month + "-21 99:99:99")
	(correct4, incorrect4) = test_data(users_dict, test_year_month + "-22 00:00:00", test_year_month + "-28 99:99:99")

	correct = correct1 + correct2 + correct3 + correct4
	incorrect = incorrect1 + incorrect2 + incorrect3 + incorrect4
	total = correct + incorrect

	if(total > 0):
		accuracy = round(correct/total,5)
	else:
		accuracy = 0

	write_file.writerow(("week",total,correct,incorrect,accuracy))


""" test_month
Input: users_dict, a dictionary of User instances; test_year_month, a string representing the year and month to test
Use: Test on the given month. Keep track of correctly guessed users. [IMPLEMENT: WRITE TO A FILE!]
Ouput: N/A """
def test_month(users_dict, test_year_month, write_file):
	date1 = test_year_month + "-00 00:00:00"		
	date2 = test_year_month + "-99 99:99:99"
	
	(correct, incorrect) = test_data(users_dict, date1, date2)
	total = correct + incorrect

	if(total > 0):
		accuracy = round(correct/total,5)
	else:
		accuracy = 0
		
	write_file.writerow(("month",total,correct,incorrect,accuracy))


""" test_data
Input: users_dict, diciontary of users (already trained); date1 and date2, the date range to test on (in the form 'yyyy-mm-dd hh-mm-ss')
Purpose: Tests based on a general date range
Output: Number of correctly guessed and number of incorrectly guessed users"""
def test_data(users_dict, date1, date2):
	correct = 0
	incorrect = 0
	for user_id in users_dict:
		transitions = users_dict[user_id].get_lac_by_date_range(date1, date2)
		if(len(transitions) > 0):
			(guessed_user, highest_prob) = find_user(transitions, users_dict)
			if(user_id == guessed_user):
				correct += 1
			else:
				incorrect += 1
	return (correct, incorrect)


"""print_date_ranges
Input: trained_users, dictionary of all users from file trained
Purpose: prints the date ranges of all users
Output: N/A"""
def print_date_ranges(trained_users):
	print("-------------------------------------")
	print("DATE RANGES:")
	min_date="9999"
	max_date="0000"
	for user_id in trained_users:
		(first, last) = trained_users[user_id].print_user_date_range()
		if(first < min_date):
			min_date = first
		if(last > max_date):
			max_date = last
	print("MINIMUM: %s" % min_date)
	print("MAXIMUM: %s" % max_date)
	print("-------------------------------------")


""" A list of transitions is passed in. The method discovers which user most likely made these transitions.
 It does this by finding the log of each of the probabilities of the transition and summing them for each 
 trained user. Returns the guessed user and the highest probability found. """
def find_user(transitions,trained_users):

	highest_prob=0; 
	guessed_user="0"

	for user_id in trained_users:
		curr_prob = trained_users[user_id].calculate_probability(transitions)

		if(highest_prob == 0): #this is only used in the first loop
			highest_prob = curr_prob;
			guessed_user = user_id

		if(curr_prob > highest_prob):#note: the probabilities are negative, decimal numbers
			highest_prob = curr_prob
			guessed_user = user_id

	return (guessed_user, highest_prob)


""" train_all_data
Input: users_dict, dictionary holding all User instances; train_year_month, the month and year to train on; test_year_month, the month and year to test on
Purpose: Trains all the data within the User dictionary based on the inputted "train_year_month" value. If the user does not have
information of that month, it is deleted from the dictionary.
Output: Returns modified users_dict"""
def train_all_data(users_dict, train_year_month):
	to_remove = []
	for user_id in users_dict:
		in_range = users_dict[user_id].train_data(train_year_month)
		if(not in_range):
			to_remove.append(user_id)

	for user_id in to_remove:
		del users_dict[user_id]

	return users_dict


""" Reads through the entire data set. For each user, a User object is created, which includes its ID, a list of dates, and a 
list of LACs visited. """
def read_data(fd):

	#taking away the first line (header line)
	fd.readline()

	lac_list=[]#list of all lacs in file

	#see: https://docs.python.org/2.3/whatsnew/node14.html
	#Separates each column of the data (user_id, user_date, user_lac)
	reader = csv.reader(fd, delimiter=',')
	
	current_user_id="0"#keeping track of the current user (because the file is viewed one user at a time)
	users_dict={}#stores all the User instances created; the key is the user_id
	new_user=None#stores the current user intance 

	#Reading through the file line by line
	for line in reader:
		(user_id, date, lac)=line

		#If user_id=0, then it is not a valid user (end of file)
		if(user_id!="0"):
			#if a new user id is seen or it is the last valid line of the file
			if(current_user_id!=user_id):
				
				#if this is not the first iteration through the file (when current_user_id=0)
				if(current_user_id!="0"):
					users_dict[current_user_id]=new_user

				current_user_id=user_id
				#print("Creating a new user instance [%s]..." % user_id)
				new_user=User(user_id)
				new_user.create_lac_list()
				new_user.add_lac(lac)
				new_user.create_date_list()
				new_user.add_date(date)
			else:
				new_user.add_lac(lac)
				new_user.add_date(date)
		else:#then this is the last line of the file, need to add last user instance to the dictionary
			if(current_user_id!="0"):
				users_dict[current_user_id]=new_user

		#adding LAC to a list (except if last line in the file). This is used when finding the total number of LACs.
		if(lac!="-001-12-30 19:03:58"):
			lac_list.append(lac)

	lac_set=set(lac_list) #creating a set of LACS(unique numbers)
	lac_count=len(lac_set) #Finding cardinality of the set

	for user_id in users_dict:
		users_dict[user_id].set_total_lac(lac_count)

	return users_dict#for Training & Testing


"""This program accepts only one parameter, the filename of the file holding the data"""
def usage():
    print("USAGE:\n%s [filename] [train-year-month] [test-year-month]" % sys.argv[0])
    print("Example: python3.2 %s rm.csv 2007-01 2007-02" % sys.argv[0])
    print("\nTo train and test on all possible month pairs, please input:\npython3.2 %s [filename] a a" % sys.argv[0])
    exit()

if __name__ == '__main__':
	main()

