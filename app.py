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


@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                     endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)


def result(a_rating, e_rating):
    return render_template("result.html", actual_rating = a_rating,\
     	estimated_rating = e_rating)


def main():
    app.debug = True
    app.run()


if __name__ == "__main__":
    main()
