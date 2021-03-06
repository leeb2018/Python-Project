from flask import Flask, jsonify, json, request
from flask import render_template
from yelp_scrapper import *
import copy


app = Flask(__name__)
global generator
global pq


@app.route('/')
def home():
    ''' render the main page with search box for users to input restaurant name
    of her/his interest.
    '''
    return render_template("home.html")


@app.route('/result', methods=['POST'])
def process():
    ''' create YelpScrapper instance with user's input (hopefully proper
    retaurant name). Then, access information of the scrapper instance.
    Pass those info to result() method that renders the result.html page
    using provided info and Jinja2
    '''
    global generator
    global pq
    scrapper = YelpScrapper(request.form["restaurant"])
    info = scrapper.processed_info
    pq = info["rating_pq"]
    q = Q.PriorityQueue()
    q.queue = copy.deepcopy(pq.queue)

    ''' generator created '''
    generator = get_review(q)
    a = next(generator)
    ''' print all reviews sorted by closeness to averate nlp rating'''

    return result(info["actual_rating"],
                  info["expected_rating"], str(scrapper), a[1])


def get_review(q):
    global pq
    while not q.empty():
        yield q.get()
    q.queue = copy.deepcopy(pq.queue) 
    yield q.get()


@app.route('/getReview', methods=['POST'])
def get_next_review():
    global generator
    global pq

    review = "No review found :("

    try:
        review = next(generator)
    except StopIteration:
        q = Q.PriorityQueue()
        q.queue = copy.deepcopy(pq.queue)
        generator = get_review(q) 

    return jsonify({"review": next(generator)})


def result(a_rating, e_rating, rest_name, rest_review):
    ''' render the result page with actual Yelp rating, our estimated rating,
    retaurant's name with "go back" button to allow users to return to the main
    page.
    '''
    return render_template("result.html", actual_rating=a_rating,
                           estimated_rating=e_rating,
                           restaurant_name=rest_name,
                           restaurant_review=rest_review)


def main():
    app.debug = True
    app.run()


if __name__ == "__main__":
    main()
