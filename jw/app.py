# Dependencies
from flask import Flask, render_template
from flask_pymongo import PyMongo
# py file
import scrape_mars

# Initialize
app = Flask(__name__)

# Mongo connection
app.config["MONGO_URI"] = "mongodb://localhost:27017/mars_app"
mongo = PyMongo(app)

# Index.html
@app.route("/")
def index():
    mars = mongo.db.mars.find_one()
    return render_template("index.html", mars=mars)

# Page after scraped, static page
@app.route("/scrape")
def scrape():
    mars = mongo.db.mars
    mars_data = scrape_mars.scrape_all()
    # Upsert creates a new document when no document matches query criteria
    mars.update({}, mars_data, upsert=True)
    return "Scraping Successful!"

# Run
if __name__ == "__main__":
    app.run()
