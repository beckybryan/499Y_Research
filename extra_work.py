	"""
	#In main:
	#The following is for testing users based on one month intervals of data:

	#test_lacs holds a list of LAC lists, test_users holds a list of user_ids correlated to the LAC lists
	(test_lacs,test_users)=test_one_month(fd2)
	
	print("\n*******TEST 1********")

	(user, prob)=find_user(test_lacs[0],trained_users)
	
	print("\nNumber of LACs in transition list: %d" % len(test_lacs[0]))

	print("Correct: %s " % test_users[0])

	print("Guessed: %s with probability %s" % (user,str(prob)))


	print("\n*******TEST 2********")

	(user, prob)=find_user(test_lacs[1],trained_users)
	
	print("\nNumber of LACs in transition list: %d" % len(test_lacs[1]))

	print("Correct: %s " % test_users[1])

	print("Guessed: %s with probability %s" % (user,str(prob)))


	print("\n*******TEST 3********")

	(user, prob)=find_user(test_lacs[2],trained_users)
	
	print("\nNumber of LACs in transition list: %d" % len(test_lacs[2]))

	print("Correct: %s " % test_users[2])

	print("Guessed: %s with probability %s" % (user,str(prob)))


	print("\n*******TEST 4********")

	(user, prob)=find_user(test_lacs[3],trained_users)
	
	print("\nNumber of LACs in transition list: %d" % len(test_lacs[3]))

	print("Correct: %s " % test_users[3])

	print("Guessed: %s with probability %s" % (user,str(prob)))"""



	""" BAD METHOD: Calculates the classifier for each transition to find which user it is most likely (based on month).
Transitions is a list of lists of LACS. Returns a list of users that it most likely matches to. (can be
compared to test_users)"""
def find_user_bymonth(transitions,trained_users):

	month_id=0
	lac_index=0
	users=[]

	for u in trained_users:

		#need to check that the length of this list is >1
		if(len(transitions[month_id])>1):

			#loops through one month of ids
			for i in transitions[month_id]:
				lac1=transitions[month_id][i]
				lac2=transitions[month_id][i+1]

				#ignores self-transitions
				if(lac1!=lac2):
					trained_users[u].get_prob(lac1, lac2)

	
""" BAD METHOD: Reads in the file and reads in a list of LACS for the first user for the first month.
The list of LACs and users is returned (the list of users correlates to the LAC lists)."""
def test_one_month(fd):
	#taking away the first line (header line)
	fd.readline()

	#see: https://docs.python.org/2.3/whatsnew/node14.html
	#Separates each column of the data (user_id, user_date, user_lac)
	reader = csv.reader(fd, delimiter=',')

	curr_user_id="0"
	curr_month="0"
	lac_list=[]#list of lacs visited by one user for one month
	user_list=[]#list of users (index corresponds to the all_lac index)
	all_lac=[]#list of lists of lacs visited monthly by user

	index=0
	
	#Reading through the file line by line

	for line in reader:
		(user_id, date, lac)=line

		if(curr_user_id=="0"):
			curr_user_id=user_id
			curr_month=date[5:7]

		if(curr_user_id==user_id and curr_month==date[5:7]):
			lac_list.append(lac)
		else:
			user_list.append(curr_user_id)
			all_lac.append(list(lac_list))
			index+=1
			curr_user_id=user_id
			curr_month=date[5:7]
			lac_list=[]

			if(curr_user_id!="0"):
				lac_list.append(lac)

	return (all_lac,user_list)


	