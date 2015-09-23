"""
Becky Bryan
499Y Research
Prof. Brian Levine
Last updated: 4/12/15

This program currently reads in data in the form (ID, Date, LAC). LAC is the "location area code," or the
unique code for each location area. It counts the number of lacs and places these into a list (a map that maps 
the lacs to a unique number ranging from 0 to number of lacs-1). It also places each user ID into an array.
"""

""" For every user, a "user instance" is created through the User class. This allows each user to have their own
list of LACs that they visited, which is used to create a matrix. This matrix is a list of lists. It is only the size of 
the number of LACs that user visited (I am making the assumption that one user has not visited every LAC,
which is over 30,000 and would be too large to store as a matrix). 

"""

#!/usr/bin/env python3

import sys
import csv
import collections
import math
import random

class User:
	
	def __init__(self,id):
		self.user_id=id

	""" 
	train_data
	Input: a string in the format 'year-month'. For example, 2004-01. This is the month to train the data on
	
	Use: trains the data based on the given month. It creates a count matrix for every LAC visited within the month. 
	The count matrix has a smoothing factor of 1 added to each cell. Each cell represents the number of transitions from one LAC
	(row) to another (column).
	
	Output: N/A
	"""
	def train_data(self, train_year_month):
		#Retrieve a list of LACs visited in the given month
		date1 = train_year_month + "-00 00:00:00"
		date2 = train_year_month + "-99 99:99:99"

		lacs_trained = self.get_lac_by_date_range(date1, date2)

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

	""" 
	create_prob_matrix
	Input: num_lac, the number of lacs visited by the user

	Use: Creates a probability matrix from the transition count matrix by dividing each cell of the count matrix by
	the total number of possible transitions 

	Output: N/A
	"""
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


	#NOT USED: Creates a list of lists, or a matrix, that will store the counts of LAC transitions. It is initialized to zero
	def OLD_init_count_matrix(self):
		self.unique_lac=set(self.lacs_visited)
		#self.unique_lac=set(self.date_lac_dict.values())
		self.unique_lac=list(self.unique_lac) #The index of this list correllates to the row/column index of the count matrix and probability matrix
		self.num_lac=len(self.unique_lac)
		self.count_matrix=[[1 for x in range(self.num_lac)] for x in range(self.num_lac)]#adding 1 as smoothing factor

		#setting all self-transitions to zero
		for row in range(self.num_lac):
			for col in range(self.num_lac):
				if(row==col):
					self.count_matrix[row][col]=0


	def get_ID(self):
		return self.user_id

	#Creates an empty list to store a list holding all LACs visited by user (including duplicates)
	def create_lac_list(self):
		self.lacs_visited=[]

	#Adding a LAC to the list (including duplicates)
	def add_lac(self,lac):
		self.lacs_visited.append(lac)

	#NOT USED
	def fill_count_matrix(self):
		row=0
		col=0

		#lacs=list(self.date_lac_dict.values())

		#Filling in all transition cells for this user (ignoring self-transitions)
		for i in range(len(self.lacs_visited)-1):
			if(self.lacs_visited[i]!=self.lacs_visited[i+1]):
				row=self.unique_lac.index(self.lacs_visited[i])
				col=self.unique_lac.index(self.lacs_visited[i+1])
				self.count_matrix[row][col]+=1

		self.num_unvisited= self.total_lac-self.num_lac #finding the LACs that are unvisited, needed for smoothing factor

		self.row_sum=[] #Stores the sum of all the transitions in every row

		#Adding the sums of each row and storing them in a list
		for row in self.count_matrix:
			sum_row=0
			for val in row:
				sum_row+=val
			self.row_sum.append(sum_row)



	#NOTE USED: Checks to make sure each row in the probability matrix sums to 1
	def check_prob_matrix(self):
		row_index=0
		for row in self.prob_matrix:
			sum_row=0
			for val in row:
				sum_row+=val
			sum_row+=self.num_unvisited/(self.num_unvisited+self.row_sum[row_index])
			if(round(sum_row,10)!=1.0000000000):#Rounding
				print("ERROR: A row in probability matrix did not add up to zero")
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
		
		"""try:
			row=self.unique_lac.index(lac1)#has key; delete lac list
		except:
			return 1/self.total_lac #If row doesn't exist, return (1/total LACs)
		try:
			col=self.unique_lac.index(lac2)
		except:
			return 1/(self.num_unvisited + self.row_sum[row]) #If column doesn't exist, row does exist and need to calculate the row-count plus lacs_unvisited"""

		#Used if no probability matrix:
		#if(self.count_matrix[row][col]!=0):#ignoring self-transitions
		#	prob=self.count_matrix[row][col]/(self.row_sum[row]+self.num_unvisited)
		#return prob

		prob=self.prob_matrix[row][col]
		return prob


	""" A list of transitions is passed in. This method finds out the probability that this user made the 
	transitions. A positive probability is returned (although the original calculation is negative). When 
	this probability is used, the greater the value, the less likely it is this user."""
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
		#self.date_lac_dict[date]=lac

	""" Finds all the LACs visited by the user between a date range and returns the list (used for Testing). 
	Dates and Lacs Visited correlate to each other """
	def get_lac_by_date_range(self, date1, date2):
		lacs=[]

		for i in range(len(self.dates)):
			if(self.dates[i] >= date1 and self.dates[i] <= date2):
				lacs.append(self.lacs_visited[i])
		return lacs

	""" Print the date range of this user """
	def print_user_date_range(self):
		print("User ID: %s, " % self.user_id, end=" ")
		first=self.dates[0]
		last=self.dates[len(self.dates)-1]
		#first=list(self.date_lac_dict.keys())[0] #This works because it is an Ordered Dictionary
		#last=list(self.date_lac_dict.keys())[len(self.date_lac_dict)-1]
		print("%s - %s" % (first, last))


def main():
	#checking the number of arguments
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

	train_year_month = sys.argv[2]
	test_year_month = sys.argv[3]


	users_dict = read_data(fd)

	print_date_ranges(users_dict)

	train_data(users_dict, train_year_month)

	test_month(users_dict, test_year_month)



	#for testing, trained_users holds all of the created User instances that have been trained (probability matrices have been made for them)
	#trained_users = readData(fd)
	#print_date_ranges(trained_users)
	#test_data(trained_users)
"""
test_month
Input: users_dict, a dictionary of User instances; test_year_month, a string representing the year and month to test

Use: Test on the given month. Keep track of correctly guessed users.

Ouput: 
"""
def test_month(users_dict, test_year_month):
	correct=0
	#Retrieve a list of LACs visited in the given month
	date1 = test_year_month + "-00 00:00:00"		
	date2 = test_year_month + "-99 99:99:99"

	for user_id in users_dict:
		print("------------------------------")
		transitions=users_dict[user_id].get_lac_by_date_range(date1, date2)
		print("(For analysis: length of transitions tested= %d)" % len(transitions))
		(guessed_user, highest_prob)=find_user(transitions, users_dict)
		print("Correct: %s \nGuessed: %s (with highest probability of %f)" % (user_id, guessed_user, highest_prob))

		if(user_id == guessed_user):
			correct+=1

def print_date_ranges(trained_users):
	print("-------------------------------------")
	print("DATE RANGES:")
	for user_id in trained_users:
		trained_users[user_id].print_user_date_range()
	print("-------------------------------------")

""" A list of transitions is passed in. The method discovers which user most likely made these transitions.
 It does this by finding the log of each of the probabilities of the transition and summing them for each 
 trained user. Returns the guessed user and the highest probability found. """
def find_user(transitions,trained_users):

	highest_prob=0; 
	guessed_user="0"

	for u in trained_users:
		curr_prob=trained_users[u].calculate_probability(transitions)

		if(highest_prob==0): #this is only used in the first loop
			highest_prob=curr_prob;
			guessed_user=trained_users[u].get_ID()

		if(curr_prob>highest_prob):#note: the probabilities are negative, decimal numbers
			highest_prob=curr_prob
			guessed_user=trained_users[u].get_ID()

	return (guessed_user, highest_prob)

""" Asks for a date range input (note: date1 and date2 will be in the form '2004-07-26 00:00:00') and number of users to test.
The dictionary of stored trained_users is passed into the method. This method randomly chooses the given number of users and 
finds a list of transitions that occurred for those users within the specified date range. It prints the correct, guessed, and calculated
probability for the users. """
def test_data(trained_users):
	correct=0
	while(not correct):
		print("- - - - - - - - - - - - - - - - - - - - - - - - -")
		print("Please Input Range to Test Dataset: \nFrom (if entire range, input '0000-00-00')...")
		year1= input("Year (e.g. 2004): ")
		month1= input("Month (e.g. 07): ")
		day1= input("Day (e.g. 01): ")
		print("\nTo (if entire range, input '9999-99-99')...")
		year2= input("Year (e.g. 2005): ")
		month2= input("Month (e.g. 07): ")
		day2= input("Day (e.g. 01): ")
		print("- - - - - - - - - - - - - - - - - - - - - - - - -")
		print("Please Input Number of Users to Test (this dataset ranges from 1 to %d):" % len(trained_users))
		test_num=input("Number of Users to Test: ")

		date1="%s-%s-%s 00:00:00" % (year1, month1, day1)
		date2="%s-%s-%s 00:00:00" % (year2, month2, day2)

		if(len(date1)!=19 or len(date2)!=19):
			print("\n\nError: Dates were incorrectly inputted. Please input dates again\n\n")
		else:
			correct=1

		if(int(test_num)>len(trained_users)):
			print("\n\nError: Incorrect number of Users to Test. Please input a number in the correct range\n\n")
			correct=0
	
	random_list=random.sample(trained_users.keys(),int(test_num))

	print("------------------------------")
	print("Date Range: %s to %s" % (date1, date2))

	for user_id in random_list:
		print("------------------------------")
		transitions=trained_users[user_id].get_lac_by_date_range(date1, date2)
		print("(For analysis: length of transitions tested= %d)" % len(transitions))
		(guessed_user, highest_prob)=find_user(transitions, trained_users)
		print("Correct: %s \nGuessed: %s (with highest probability of %f)" % (user_id, guessed_user, highest_prob))

"""  """
def train_data(users_dict, train_year_month):

	for user_id in users_dict:
		users_dict[user_id].train_data(train_year_month)
		#user_instance_dict[user_id].set_total_lac(lac_count)
		#print("Initializing count transition matrix [%s]..." % user_id)
		#user_instance_dict[user_id].init_count_matrix()
		#print("Filling in count transition matrix [%s]..." % user_id)
		#user_instance_dict[user_id].fill_count_matrix()


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
				print("Creating a new user instance [%s]..." % user_id)
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


#OLD METHOD: for testing, returns the dictionary holding all of the User instances
def OLD_readData(fd):

	#taking away the first line (header line)
	fd.readline()

	lac_list=[]#list of all lacs in file
	#user_id_list=[]#list of all user ids in file... this currenty is not used, so commented out

	#see: https://docs.python.org/2.3/whatsnew/node14.html
	#Separates each column of the data (user_id, user_date, user_lac)
	reader = csv.reader(fd, delimiter=',')
	
	current_user_id="0"#keeping track of the current user (because the file is viewed one user at a time)
	user_instance_dict={}#stores all the User instances created; the key is the user_id
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
					user_instance_dict[current_user_id]=new_user

				current_user_id=user_id
				print("Creating a new user instance [%s]..." % user_id)
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
				user_instance_dict[current_user_id]=new_user

		#adding LAC to a list (except if last line in the file). This is used when finding the total number of LACs.
		if(lac!="-001-12-30 19:03:58"):
			lac_list.append(lac)

		#adding IDs to a list
		#if(user_id!="0"):
		#	user_id_list.append(user_id)

	lac_set=set(lac_list) #creating a set of LACS(unique numbers)
	lac_count=len(lac_set) #Finding cardinality of the set

	""" #Without the following, training on entire data set. Implement the following!!
	print("************************************************")
	print("Total Users in dataset: %d" % len(user_instance_dict))
	print("- - - - - - - - - - - - - - - - - - - - - - - - -")
	print("Please Input Range to Train Dataset (if entire range, input 'a'): \nFrom...")
	train_year_1= input("Year (e.g. 2007): ")
	train_month_1= input("Month (e.g. 07): ")
	train_day_1= input("Day (01): ")
	print("\nTo...")
	train_year_2= input("Year (e.g. 2007): ")
	train_month_2= input("Month (e.g. 07): ")
	train_day_2= input("Day (01): ")
	"""


	#Will need to change how it trains based on inputted date range. (use new dictionary made, date-lac, and when call ini_count_matrix, in that method, change so that it only creates a matrix with the correct LACs)

	for key_user_id in user_instance_dict:
		user_instance_dict[key_user_id].set_total_lac(lac_count)
		print("Initializing count transition matrix [%s]..." % key_user_id)
		user_instance_dict[key_user_id].init_count_matrix()
		print("Filling in count transition matrix [%s]..." % key_user_id)
		user_instance_dict[key_user_id].fill_count_matrix()
		#print("Creating a probability matrix [%s]..." % user_instance_dict[key_user_id].get_ID())
		#user_instance_dict[key_user_id].create_prob_matrix()

		#Checking the probability matrix, that each row sums to 1:
		#user_instance_dict[key_user_id].check_prob_matrix()

	#The following is for debugging:
	#using a set to create unique lists
	#lac_list=set(lac_list) #creating a set of LACS(unique numbers)
	#user_id_list=set(user_id_list) #creating a set of users (unique numbers)
	#lac_list=list(lac_list) #converting the LAC set into a list
	#user_id_list=list(user_id_list) #converting the user ID set into a list

	#Finding the number of users and the number of unique LACs in dataset
	#lac_count=len(lac_list)
	#user_id_count=len(user_id_list)

	return user_instance_dict#for Testing


"""This program accepts only one parameter, the filename of the file holding the data"""
def usage():
    print("USAGE:\n%s [filename] [train year-month] [test year-month]" % sys.argv[0])
    print("Example: python3.2 %s rm.csv 2004-01 2004-02" % sys.argv[0])
    exit()

if __name__ == '__main__':
	main()

