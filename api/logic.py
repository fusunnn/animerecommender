import json
from logging import lastResort
import math
from datetime import datetime
from csv import writer

def getTitles():
	
	"""
	Get list of titles

	Returns:
		[list]: [list of titles] --> Used for auto complete
	"""
	
	with open("./data/anime_db.json", 'r') as fout:
		tits = json.load(fout)
	titles = [x for x in tits]
	return titles




def openAnimes():
	"""
	Opens Anime JSON and returns it

	Returns:
		[Dict]: [Animes Dict]
	"""
	with open("./data/anime_db.json", 'r') as fout:
		animes = json.load(fout)
	return dict(animes)


def search(animes, ask):
	
	"""
	function that gets title search and returns the propre anime dict

	Returns:
		string: proper title
	"""
	return animes[ask]




def dot(l1, l2):
    
	"""Dot product of two vectors

	Returns:
		int : result of dot prod
	"""
	prod = 0
	for x in range(len(l1)):
			prod += l1[x] * l2[x]
	return prod
	

			

def weighted_rating(v, m, R, C):

    return (v/(v+m) * R) + (m/(m+v) * C)



def stop_doubles(n1,n2):
	n1 = n1.split(" ")


	if n1[0] in n2:
		return False
	if len(n1) >= 2 and n1[1] in n2:
		return False

	return True




def get_degree_of_sim(v1, v2):
    
	a = (math.sqrt(sum([x**2 for x in v1]))*math.sqrt(sum([x**2 for x in v2])))
	if a == 0:
		return 0
	return dot(v1, v2)/ a
	



def inter(animes, choice, check, amnt):

	"""
	needs = ["Isekai", 'Bounty Hunter', 'Cooking', 'Cross Dressing', "Human Enhancement", "Super Deformed",
			'Ninja', 'Space Opera', "Anthropomorphism", 'Slow When It Comes To Love', 'Reverse Harem', 'Music',
			'Sports', 'Delinquent', 'time travel', 'vampire', romance]


	Function that finds matching anime, they need to pass the minimum amount of similarity

	Returns:
		list: list of animes that pass the minimum amount of similarity check
	"""


	choice_anime_vector = choice['tag_vec']
	choice_anime_vector_gen = choice['gen_vec']

	try:
		name = choice['title']["english"]
		if name == None:
			name = choice["title"]["userPreferred"]
	except:
		name = choice["title"]["userPreferred"]

	

	anime_type = choice["format"]
	final_recommendations = []
	simi = []

	for x in animes:
		anime_vec = animes[x]['tag_vec']
		anime_gen_vec = animes[x]["gen_vec"]

		if anime_vec != [0]*len(anime_vec) and anime_gen_vec != [0]*len(anime_gen_vec):
			degree_of_similarity = get_degree_of_sim(choice_anime_vector, anime_vec)
			degree_of_sim_gen = get_degree_of_sim(choice_anime_vector_gen, anime_gen_vec)
			if degree_of_similarity >= check and stop_doubles(name,x) and anime_type == animes[x]["format"]:
				animes[x]["simi"] = degree_of_similarity + degree_of_sim_gen/2
				final_recommendations.append(animes[x])
		
	return final_recommendations



def get_date_gap(d1, d2):

    #2021-07-07

    d1 = d1.split("-")
    d2 = d2.split("-")

    return 0.00001 + abs(int(d1[0])-int(d2[0]))




def stop_doubles_in_ranking(new_name, og):

	if og in new_name:
		return False
	
	bad = ["Season 2", "season 2", "season", "Season", "sequel", "other", "part", "Part", "Other"]
	new_name = new_name.split(" ")

	if new_name[0] in og:
		return False
	
	for x in bad:
		if x in new_name:
			return False
	
	if new_name[-1].isnumeric():
		return False

	return True

def ranking(recomendation_list, amount_to_recommend, choice, ):
	"""
	to use : averageRating, userCount, favoritesCount, popularityRank, ratingRank
	Function that sorts and ranks the proposed recommendations
	Uses a weighed coeficient formula -->( similiratiy(0-1)) * (rating(0-100) * 7/10) + (Amount of ppl that gave it a rating(0-alot)*3/10)

	Args:
		recomendation_list (List of recommendations proposed)
		amount_to_recommend (Int): the selected amount of recommendations

	Returns:
		list: ranked recommendations
	"""
	anime_rec_ranking = []
	anime_rec_inter = []
	anime_rec_names = []
	date_og = choice["seasonYear"]
	
	name_og = choice['title']["english"]
	if name_og is None:
		name_og = choice["title"]["userPreferred"]
		if name_og == None:
			name_og = choice["title"]["romanji"]
	if len(recomendation_list) < amount_to_recommend: #check to see if the amount proposed is less than the amount asked
		return []

	for anime in recomendation_list: #different attributes
		score = anime["averageScore"]
		date = anime["seasonYear"]
		
		name = anime['title']["english"]
		if name is None:
			name = anime["title"]["userPreferred"]
			if name == None:
				name = anime["title"]["romanji"]
		
	


		if score != None and name != None and stop_doubles_in_ranking(name, name_og): #check if empty variables
			anime["key"] = anime["simi"]  + score/200 #+ (0.2 - (0.01) * abs(date_og - date))
			anime_rec_inter.append(anime) 
			anime_rec_names.append(name) 
			#print(anime["simi"], score/200, (0.2 - (0.01)* abs(date_og - date)), name)

	anime_rec_ranking = sorted(anime_rec_inter, key = lambda k: k["key"], reverse=True) 


	if len(anime_rec_ranking) < amount_to_recommend:
		return []

	return anime_rec_ranking[0:amount_to_recommend]



# function to write the user's input into csv file to check what people are inputting on website
import time
def write_input(anime, number):
	time = datetime.now()
	dt_string = time.strftime("%d/%m/%Y %H:%M:%S")
	with open('/home/ivanadrd/api/data/inputs.csv', 'a', newline='') as f:
		writer_object = writer(f)
		writer_object.writerow([anime, number, dt_string])
		f.close()


def run(animes, choice, amnt):

	choice = search(animes, choice)
	amount = int(amnt) #int(input("How many would u want: "))
	check = 0.2
	trys = 0
	how = len([x for x in choice['tag_vec'] if x == 1])
	partial_recs = []
	found = False
	while not found:
		anime_recs = inter(animes, choice, check, how)
		if len(anime_recs) >= amount+3:
			partial_recs = anime_recs


		check -= 0.1
		trys += 1

		if trys == 9:
			found = True
			conc = ranking(partial_recs, amount, choice, )
			return conc
			
		conc = ranking(partial_recs, amount, choice, )
		if len(conc) >= amount:
			return conc

	return [animes[list(animes.keys())[x]] for x in range(amnt)]



"""make mini dict with name, score for each anime, ligher to process the data"""


"""start_time = time.time()
animes = openAnimes()
print(animes["Cowboy Bebop"])
our_vec = animes["Cowboy Bebop"]["tag_vec"]
print("--- %s seconds ---" % (time.time() - start_time))
for x in animes:
	vec = animes[x]["tag_vec"]
	if vec != [0 for x in range(len(vec))]:
		print(get_degree_of_sim(our_vec, vec))
	else:
		print(0)
print("--- %s seconds ---" % (time.time() - start_time))


"""

