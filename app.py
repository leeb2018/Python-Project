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
    ratings = process_query(request.form["restaurant"])
    print(ratings)
    return result(ratings['actual_rating'], ratings['expected_rating'])


def result(a_rating, e_rating):
    return render_template("result.html", actual_rating = a_rating,\
     	estimated_rating = e_rating)


def main():

    app.debug = True
    app.run()


if __name__ == "__main__":
    main()
