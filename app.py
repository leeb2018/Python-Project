from flask import Flask
from flask import render_template
from flask import request
from yelp_scrapper import *


app = Flask(__name__)


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
    scrapper = YelpScrapper(request.form["restaurant"])
    info = scrapper.processed_info
    return result(info["actual_rating"],
                  info["expected_rating"], str(scrapper))


def result(a_rating, e_rating, rest_name):
    ''' render the result page with actual Yelp rating, our estimated rating,
    retaurant's name with "go back" button to allow users to return to the main
    page.
    '''
    return render_template("result.html", actual_rating=a_rating,
                           estimated_rating=e_rating,
                           restaurant_name=rest_name)


def main():
    app.debug = True
    app.run()


if __name__ == "__main__":
    main()
