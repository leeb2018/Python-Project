from flask import Flask
from flask import render_template
from flask import request
from yelp_scrapper import *


app = Flask(__name__)


@app.route('/')
def home():
    return render_template("home.html")


@app.route('/result', methods=['POST'])
def process():
    scrapper = YelpScrapper(request.form["restaurant"])
    info = scrapper.processed_info
    return result(info["actual_rating"], info["expected_rating"], str(scrapper))


def result(a_rating, e_rating, rest_name):
    return render_template("result.html", actual_rating = a_rating,\
     	estimated_rating = e_rating, restaurant_name = rest_name)


def main():
    app.debug = True
    app.run()


if __name__ == "__main__":
    main()
