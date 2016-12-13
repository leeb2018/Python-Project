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
        ''' Returns the name of restaurant that scrapper is told to find.'''
        return self.query.title()

    def __len__(self):
        ''' Returns the number of reviews analyzed.'''
        return len(self.processed_info["reviews"])

    def get_reviews(func):
        ''' Retrieves reviews from the target restaurant page.
        Our implementation uses url to restaurant page obtained from
        get_restaurant_url() method and finds all the <div> tag with class
        "review-content" and its child <p> tag with attribute "lang" = "en"
        which contains all the reviews in English on that page.
        '''
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
        ''' Retrieves the Yelp rating from the target restaurant page.
        Our implementation uses url to restaurant page obtained from
        get_restaurant_url() method and finds all the <img> tag with class
        "offscreen" and find attribute "alt", which has value that corresponds
        to actual Yelp rating.
        '''
        html = requests.get(rest_url).content
        tree = lxml.html.fromstring(html)
        rating_elem = tree.xpath("//img[@class='offscreen']")
        rating = rating_elem[0].attrib['alt']
        return rating

    def sentiment_score(func):
        ''' Analyze reviews obtained from get_reviews() method.
        This method iterate through those reviews and analyze each review,
        using nltk sentiment analyzer. Sentiment analyzer give each review
        postive score and negative score. This method sums postive scores and
        negative scores and return ratio of positive score compared to negative
        score in percentage to represent our analyzed score.
        '''
        def reviews(self, restaurant):
            info_dict = func(restaurant)
            sid = SentimentIntensityAnalyzer()
            reviews = info_dict["reviews"]
            num_reviews = len(reviews)
            positive_score = 0
            negative_score = 0
            review_rating_list = []
            positivity_ratio = 0

            for review_html in reviews:
                review = review_html.text_content()
                cur_positive_score = sid.polarity_scores(review)['pos']
                cur_negative_score = sid.polarity_scores(review)['neg']
                positive_score += cur_positive_score
                negative_score += cur_negative_score

                if cur_positive_score + cur_negative_score != 0:
                    cur_positivity_ratio = (cur_positive_score /
                                            (cur_positive_score +
                                             cur_negative_score))
                    review_rating_list.append((cur_positivity_ratio, review))

                positivity_ratio = positive_score / (positive_score + negative_score)

            q = Q.PriorityQueue()
            for (x, y) in review_rating_list:
                q.put((abs(positivity_ratio - x), y))

            postivity_score = positivity_ratio * 100
            info_dict["expected_rating"] = '%.1f' % (postivity_score)
            info_dict["rating_pq"] = q
            return info_dict
        return reviews

    @sentiment_score
    @get_reviews
    def get_restaurant_url(restaurant):
        ''' Takes user's query as an argument and return url for the restaurant.
        Our implementation finds the first <div> tag with attribute "data-key",
        whose value is 1 - it is the first search result based on the query,
        which is usually the restaurant that the user is looking for. And,
        strips url from there by finding <a> tag with classname "biz-name
        js-analytics-click" and getting the value of its attribute "href"
        - equivalent to url.'''
        BASE_URL = "http://www.yelp.com"
        search = restaurant
        location = "Philadelphia, PA"
        term = search.replace(" ", "+")
        place = location.replace(",", "%2C").replace(" ", "+")
        query = BASE_URL + "/search?find_desc="+term+"&find_loc="+place+"&ns=1#start=0"
        html = requests.get(query).content
        tree = lxml.html.fromstring(html)

        # Yelp's class name and id name occasionally
        results = tree.xpath("//div[@data-key='1']")
        result = results[0]
        a_tag = lxml.html.fromstring(lxml.html.tostring(result)).xpath("//a[@class='biz-name js-analytics-click']")
        target = a_tag[0]

        href = target.attrib['href']
        return {"url": BASE_URL + href}

    def process_query(self, restaurant):
        ''' Brings all the methods together to create crucial dictionary
        containing necessary information such as actual_rating, our rating,
        url and all the obtained reviews
        '''
        info_dict = self.get_restaurant_url(restaurant)
        a_rating = self.get_rating(info_dict["url"])
        info_dict["actual_rating"] = a_rating
        return info_dict


if __name__ == "__main__":
    main()
