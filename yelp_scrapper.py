import requests                                                             
import lxml.html 
import nltk

try:
    import Queue as Q  # ver. < 3.0
except ImportError:
    import queue as Q


from nltk.sentiment.vader import SentimentIntensityAnalyzer

class YelpScrapper(object):


	def __init__(self, restaurant_name):
		self.query = restaurant_name
		self.processed_info = self.process_query(restaurant_name)


	def __str__(self):
		return self.query.title()


	def get_reviews(func):
		def get_url(restaurant):
			info_dict = func(restaurant)
			url = info_dict["url"]
			html = requests.get(url).content                                          
			tree = lxml.html.fromstring(html)
		
			reviews = tree.xpath("//div[@class='review-content']/p[@lang='en']")
			info_dict["reviews"] = reviews
			return info_dict
		return get_url


	def get_rating(self, rest_url):
		html = requests.get(rest_url).content                                          
		tree = lxml.html.fromstring(html)
		
		rating_elem = tree.xpath("//img[@class='offscreen']")
		rating = rating_elem[0].attrib['alt']
		return rating


	def sentiment_score(func):
		def reviews(self, restaurant):
			info_dict = func(restaurant)
			sid = SentimentIntensityAnalyzer()
			reviews = info_dict["reviews"]
			num_reviews = len(reviews)
			positive_score = 0
			negative_score = 0
			review_rating_list = []
			for review_html in reviews:
				review = review_html.text_content()
				cur_positive_score = sid.polarity_scores(review)['pos']
				cur_negative_score = sid.polarity_scores(review)['neg']
				positive_score += cur_positive_score
				negative_score += cur_negative_score
				if cur_positive_score + cur_negative_score != 0:
					cur_positivity_ratio = (cur_positive_score /
					(cur_positive_score + cur_negative_score))
					review_rating_list.append((cur_positivity_ratio, review))

			positivity_ratio = positive_score / (positive_score + negative_score)

			q = Q.PriorityQueue()
			for (x, y) in review_rating_list:
				q.put((abs(positivity_ratio - x), y))

			postivity_score = positivity_ratio * 100
			info_dict["expected_rating"] = '%.1f'%(postivity_score)
			info_dict["rating_pq"] = q
			return info_dict
		return reviews


	@sentiment_score
	@get_reviews
	def get_restaurant_url(restaurant):
		BASE_URL = "http://www.yelp.com"                                            
		search = restaurant                                                    
		location ="Philadelphia, PA"

		term = search.replace(" ","+")                                              
		place = location.replace(",","%2C").replace(" ","+")                        
		query = BASE_URL + "/search?find_desc="+term+"&find_loc="+place+"&ns=1#start=0"

		html = requests.get(query).content             
		tree = lxml.html.fromstring(html)
		# Yelp's class name and id name occasionally
		results = tree.xpath("//div[@data-key='1']")
		result = results[0]
		a_tag = lxml.html.fromstring(lxml.html.tostring(result)).xpath("//a[@class='biz-name js-analytics-click']")
		target = a_tag[0]

		href = target.attrib['href']
		return {"url" : BASE_URL + href}


	def process_query(self, restaurant):
	    info_dict = self.get_restaurant_url(restaurant)
	    a_rating = self.get_rating(info_dict["url"])
	    info_dict["actual_rating"] = a_rating
	    return info_dict


if __name__ == "__main__":
    main()