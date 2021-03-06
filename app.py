# doing necessary imports

from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import pymongo
import re
import nltk
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import pymongo
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)  # initialising the flask app with the name 'app'




@app.route('/',methods=['POST','GET']) # route with allowed methods as POST and GET
def index():
    if request.method == 'POST':
        searchString = request.form['content'].replace(" ","")  # obtaining the search string entered in the form
        try:
            DB_NAME = "flipKart_Scrapping_DB"  # Specifiy a Database Name
            # Connection URL
            CONNECTION_URL = f"mongodb+srv://harish:haresh2019@cluster0.4ouqh.mongodb.net/DB_NAME?retryWrites=true&w=majority"
            # Establish a connection with mongoDB
            client = pymongo.MongoClient(CONNECTION_URL)
            # Create a DB
            dataBase = client[DB_NAME]  # connecting to the database called flipKart_Scrapping_DB
            COLLECTION_NAME = searchString  # Create a Collection Name
            collection = dataBase[COLLECTION_NAME]
            reviews = collection.find({})  # searching the collection with the name same as the keyword
            if reviews.count() > 500:  # if there is a collection with searched keyword and it has records in it
                return render_template('results.html',reviews=reviews)  # show the results to user
            else:
                flipkart_url = "https://www.flipkart.com/search?q=" + searchString  # preparing the URL to search the product on flipkart
                uClient = uReq(flipkart_url) # requesting the webpage from the internet
                flipkartPage = uClient.read() # reading the webpage
                uClient.close() # closing the connection to the web server
                flipkart_html = bs(flipkartPage, "html.parser")  # parsing the webpage as HTML
                bigboxes = flipkart_html.findAll("div", {"class": "_1AtVbE col-12-12"})
                # searching for appropriate tag to redirect to the product link
                reviews = []  # initializing an empty list for reviews
                #  iterating over the comment section to get the details of customer and their comments
                del bigboxes[0:3]
                # the first 3 members of the list do not contain relevant information, hence deleting them. #

                for i in range(12):  # for establishing 50 different Product links.
                    box = bigboxes[i]
                    productLink = "https://www.flipkart.com" + box.div.div.div.a['href']
                    # extracting the actual product link

                    uClient1 = uReq(productLink)  # requesting the webpage from the internet
                    productPage = uClient1.read()  # reading the webpage
                    uClient1.close()  # closing the connection to the web server

                    # productPage
                    productPagehtml = bs(productPage, "html.parser")

                    links = []
                    for link in productPagehtml.find('div', {"class": "col JOpGWq"}):  # finding link to review page
                        links.append(link.get('href'))

                    # finding links to 50 review pages
                    for i in range(1, 50):
                        url = "https://www.flipkart.com" + str(links[-1]) + '&page=' + str(i)
                        # print(url)
                        prodRes = uReq(url)
                        prodreviewpage = prodRes.read()
                        prodRes.close()
                        prod_html = bs(prodreviewpage, "html.parser")

                        # to retrive product name
                        for i in prod_html.find_all('a', {'class': "_2rpwqI"}):
                            product_name = i.get('title')

                        # to retrive  product overall rating #
                        for i in prod_html.find_all('div', {'class': "_3LWZlK"}):
                            overall_rating = i.text
                            # print(overall_rating)

                        # to find particular product Price#
                        for i in prod_html.find_all('div', {'class': "_30jeq3"}):
                            price = i.text
                            # print(price)

                        # to find particular Product Discount#
                        for i in prod_html.find_all('div', {'class': "_3Ay6Sb"}):
                            discount = i.text
                            # print(discount)

                        commentboxes = prod_html.find_all('div', {'class': "_1AtVbE col-12-12"})

                        # del bigboxes[0:3] # the first 3 members of the list do not contain relevant information, hence deleting them.
                        del commentboxes[0:4]
                        # print(commentboxes)

                        for commentbox in commentboxes:
                            try:
                                name = commentbox.div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text
                                # print(name)
                            except:
                                name = 'No Name'
                            try:
                                rating = commentbox.div.div.div.div.text[0]
                                # print(rating)
                            except:
                                rating = 'No Rating'
                            try:
                                commentHead = commentbox.div.div.div.p.text
                            except:
                                commentHead = 'No Comment Heading'
                            try:
                                comtag = commentbox.div.div.find_all('div', {'class': ''})
                                custComment = comtag[0].div.text
                            except:
                                custComment = 'No Customer Comment'

                            mydict = {"Product": searchString, "Product_name": product_name,
                                      "Overall_Rating": overall_rating, "Price": price, "Discount": discount,
                                      "Name": name, "Customer_Rating": rating,
                                      "CommentHead": commentHead, "Comment": custComment} # saving that detail to a dictionary
                            rec = collection.insert_one(mydict) #insertig the dictionary containing the rview comments to the collection

                            reviews.append(mydict)  #  appending the comments to the review list




                return render_template('results.html', reviews=reviews) # showing the review to the user
        except:
            return 'something is wrong'
            #return render_template('results.html')
    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
    #app.run(port=8000, debug=True)  # running the app on the local machine on port 8000
