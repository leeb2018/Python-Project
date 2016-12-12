import requests                                                             
import lxml.html 
import nltk                                                           
from nltk.sentiment.vader import SentimentIntensityAnalyzer

class YelpScrapper:

	def __init__(self, restaurant_name):
		self.query = restaurant_name
		self.processed_info = self.process_query(restaurant_name)
		print(self.processed_info)


	def __str__(self):
		return self.query.title()

	def get_restaurant_url(self, restaurant):
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
		results = tree.xpath("//div[@data-key='1']")
		print(results)
		result = results[0]
		a_tag = lxml.html.fromstring(lxml.html.tostring(result)).xpath("//a[@class='biz-name js-analytics-click']")
		target = a_tag[0]

		href = target.attrib['href']
		return BASE_URL + href


	def get_reviews(self, rest_url):
		html = requests.get(rest_url).content                                          
		tree = lxml.html.fromstring(html)
		
		reviews = tree.xpath("//div[@class='review-content']/p[@lang='en']")
		return reviews


	def get_rating(self, rest_url):
		html = requests.get(rest_url).content                                          
		tree = lxml.html.fromstring(html)
		
		rating_elem = tree.xpath("//img[@class='offscreen']")
		rating = rating_elem[0].attrib['alt']
		return rating


	def sentiment_score(self, reviews):
		sid = SentimentIntensityAnalyzer()
		num_reviews = len(reviews)
		positive_score = 0
		negative_score = 0
		for review_html in reviews:
			review = review_html.text_content()
			positive_score += sid.polarity_scores(review)['pos']
			negative_score += sid.polarity_scores(review)['neg']

		postivity_ratio = positive_score / (positive_score + negative_score)
		postivity_score = postivity_ratio * 100
		# return str(round_rating(2.5 + (2.5 * total_score / num_reviews)))
		return '%.1f'%(postivity_score)

	def round_rating(self, number):
	    return round(number * 2) / 2


	def process_query(self, restaurant):
	    rest_url = self.get_restaurant_url(restaurant)
	    reviews = self.get_reviews(rest_url)
	    a_rating = self.get_rating(rest_url)
	    e_rating = self.sentiment_score(reviews)
	    return {"actual_rating" : a_rating, "expected_rating" : e_rating,\
	            "reviews": reviews}


if __name__ == "__main__":
    main()