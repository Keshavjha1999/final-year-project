from re import L
from flask import Flask, render_template, redirect, request, flash, url_for, session, send_from_directory
from flask_cors import CORS
import os
import os.path
from werkzeug.security import generate_password_hash, check_password_hash
from newsapi import NewsApiClient
newsapi = NewsApiClient(api_key='4d05b1bf662540e38cdcb3f04920577f')
import sqlite3
import requests
from getRecipes import getSearchResults, getRecipeDetails
app = Flask(__name__, static_folder="./static/")
app.config["SECRET_KEY"] = "mysecretkey_is_safe"
BASE_DIR = os.getcwd()
db_path = f"{BASE_DIR}/static/user.db"
topics = ['World', 'Nation', 'Business', 'Technology', 'Entertainment', 'Sports', 'Science', 'Health']


def getTopNewsBBC(top):
    if(top=='World'):
        result = newsapi.get_top_headlines(language='en', page=1, page_size=6)
    elif(top=='Nation'):
        result = (requests.get('https://newsapi.org/v2/top-headlines?country=in&apiKey=4d05b1bf662540e38cdcb3f04920577f')).json()
    elif(top=='Business'):
        result = newsapi.get_top_headlines(language='en', category='business')
    elif(top=='Technology'):
        result = newsapi.get_top_headlines(language='en', category='technology')
    elif(top=='Entertainment'):
        result = newsapi.get_top_headlines(language='en', category='entertainment')
    elif(top=='Sports'):
        result = newsapi.get_top_headlines(language='en', category='sports')
    elif(top=='Science'):
        result = newsapi.get_top_headlines(language='en', category='science')
    elif(top=='Health'):
        result = newsapi.get_top_headlines(language='en', category='health')
    
    images = []
    headline = []
    summary = []
    strin = []

    for a in result['articles']:
        if(a['url'] != None and a['urlToImage'] != None and a['title'] != None and a['content'] != None):
            url = a['url']
            urlToImage = str(a['urlToImage'])
            headlin = str(a['title'])
            content = str(a['content'])
            if(len(content) > 140):
                content = str(content) + '...'
            strin.append(url + '||' + urlToImage + '||' + headlin + '||' + content + '\n')
    
    if os.path.exists("./static/myfile.txt"):
        os.remove("./static/myfile.txt")
    file1 = open("./static/myfile.txt","w")
    try:
        file1.writelines(strin)
    except UnicodeEncodeError:
        pass

@app.route("/")
def homeScreen():
    if "user" in session:
        return render_template("home.html", username=session["user"])
    else:
        return render_template("welcome_page.html")

@app.route("/home")
def home():
    if "user" in session:
        return render_template("home.html", username=session["user"])
    else:
        return redirect(url_for("login"))

# @ app.route("/welcome")
# def welcome():
#     return render_template("welcome_page.html")

# @app.route("/bhag")
# def log():
#     return render_template("login.html")


@ app.route("/news/<top>")
def news(top):
    getTopNewsBBC(top)
    newdict = {}
    file1 = open('./static/myfile.txt', "r")
    Lines = file1.readlines()
    url = []
    imgUrl = []
    heading = []
    content = []
    for line in Lines:
        lin = line.split('||')
        if(len(lin)!=4):
            continue
        url.append(lin[0])
        imgUrl.append(lin[1])
        heading.append(lin[2])
        content.append(lin[3])
    file1.close()
    # print(newdict)
    if "user" in session:
        # print(session["user"])
        return render_template(
            "dataNews.html",
            username=session["user"],
            # data=news_list,
            url = url,
            imgUrl = imgUrl,
            heading = heading,
            content = content,
            data2=topics,)
    else:
        return redirect(url_for("login"))
    # return render_template("news.html", data=news_list, data2=topics)

@ app.route("/Text-To-Speech")
def textToSpeech():
    if "user" in session:
        # print(session["user"])
        return render_template("TextToSpeech1.html", username=session["user"])
    else:
        return redirect(url_for("login"))
    # return render_template("TextToSpeech1.html")

@ app.route("/login", methods=["GET", "POST"])
def login():
    if "user" in session:
        session.pop("user", None)
    if request.method == "POST":
        if request.form["CheckLogReg"] == "register":
            RegisterUserName = request.form["RegisterUserName"]
            RegisterPassword = generate_password_hash(
                request.form["RegisterPassword"])
            conn = sqlite3.connect(db_path)
            db = conn.cursor()
            db.execute(f"INSERT INTO login ('username', 'password') values('{RegisterUserName}','{RegisterPassword}')")
            conn.commit()
            conn.close()
            # print(RegisterUserName)
            # print(RegisterPassword)
        elif request.form["CheckLogReg"] == "login":
            conn = sqlite3.connect(db_path)
            db = conn.cursor()
            LoginUserName = request.form["LoginUserName"]
            # LoginPassWord = request.form["LoginPassword"]
            password = db.execute(
                f"SELECT password from login WHERE username = '{LoginUserName}'"
            )
            hashPass = password.fetchone()[0]
            if check_password_hash(hashPass, request.form["LoginPassword"]):
                session["user"] = LoginUserName
                # return render_template("home.html")
                return redirect(url_for("home"))
            else:
                return render_template("login.html", data="fail")
            conn.close()
        else:
            return render_template("404.html")
    return render_template("login.html")


@app.route('/recipes', methods=["GET", "POST"])
def recipes():
    # dish_names = []
    if "user" in session:
        data = {'titles': [], 'prepTime': [],
                'cookTime': [], 'servings': [], 'links': []}
        if request.method == "POST" and request.form.get("searching") == "search":
            recipename = request.form.get("recipe_search")
            print(recipename)
            # module = RecipeModule(recipename)
            module = getSearchResults(recipename)
            dish_names = module.returnTitles()
            prepTime, cookTime, servings = module.returnTitleDetails()
            links = module.returnLinks()
            data = {'titles': dish_names, 'prepTime': prepTime,
                    'cookTime': cookTime, 'servings': servings, 'links': links}
            # for links in data['links']:
        else:
            print("didnt work")
        return render_template("recipes.html", username=session["user"], data=data)

    else:
        return redirect(url_for("login"))


@app.route("/recipes/<name>")
def displayRecipe(name):
    print("print link: ", name)
    data = {}
    module = getSearchResults(name)
    links = module.returnLinks()[:1]
    module2 = getRecipeDetails(links[0])
    data['title'] = name
    data['link'] = links[0]
    data['procedure'] = module2.returnProcedure()
    data['ingredients'] = module2.returnIngredients()
    data['chef'] = module2.returnChef()
    data['servings'] = module2.returnServings()
    data['preptime'] = module2.returnPrepTime()
    data['cooktime'] = module2.returnCookingTime()
    return render_template("displayrecipes.html", data=data, username=session["user"])

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                          'favicon.ico')
if __name__ == "__main__":
    app.run(debug=True, port=5000)
