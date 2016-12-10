import requests                                                             
import lxml.html 
import nltk                                                           
from nltk.sentiment.vader import SentimentIntensityAnalyzer

def get_restaurant_url(restaurant):
	BASE_URL = "http://www.yelp.com"                                            
	search = restaurant                                                    
	location ="Philadelphia, PA"

	term = search.replace(" ","+")                                              
	place = location.replace(",","%2C").replace(" ","+")                        
	query = BASE_URL + "/search?find_desc="+term+"&find_loc="+place+"&ns=1#start=0"

	html = requests.get(query).content
	print(html)                                         
	tree = lxml.html.fromstring(html)
	# Yelp's class name and id name occasionally
	results = tree.xpath("//div[@class='search-result natural-search-result hero-search-result' and @data-key='1']")
	print(results)
	result = results[0]
	a_tag = lxml.html.fromstring(lxml.html.tostring(result)).xpath("//a[@class='biz-name js-analytics-click']")
	target = a_tag[0]

	href = target.attrib['href']
	return BASE_URL + href


def get_reviews(rest_url):
	html = requests.get(rest_url).content                                          
	tree = lxml.html.fromstring(html)
	
	reviews = tree.xpath("//div[@class='review-content']/p[@lang='en']")
	return reviews


def get_rating(rest_url):
	html = requests.get(rest_url).content                                          
	tree = lxml.html.fromstring(html)
	
	rating_elem = tree.xpath("//img[@class='offscreen']")
	rating = rating_elem[0].attrib['alt']
	return rating


def sentiment_score(reviews):
	sid = SentimentIntensityAnalyzer()
	num_reviews = len(reviews)
	total_score = 0
	for review_html in reviews:
		review = review_html.text_content()
		print("\n------------------------------------------------------")
		print(review)
		print(sid.polarity_scores(review))
		total_score += sid.polarity_scores(review)['pos'] - sid.polarity_scores(review)['neg']
		print("------------------------------------------------------\n")
	# return str(round_rating(2.5 + (2.5 * total_score / num_reviews)))
	return str(2.5 + (2.5 * total_score / num_reviews)) + " star rating"

def round_rating(number):
    return round(number * 2) / 2


def process_query(restaurant):
    rest_url = get_restaurant_url(restaurant)
    reviews = get_reviews(rest_url)
    a_rating = get_rating(rest_url)
    e_rating = sentiment_score(reviews)
    return {"actual_rating" : a_rating, "expected_rating" : e_rating}


if __name__ == "__main__":
    main()