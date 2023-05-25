from flask import Flask, Response, request, session, render_template, redirect, make_response # import Flask library
import requests
import random
from datetime import timedelta

app = Flask(__name__,static_folder="static") # __name__ is defined

# Session Handling
app.secret_key = "_#Programming 4$%" # set "common key" to encrypt
app.session_cookie_name = "PG4_session"
# app.config("SESSION_COOKIE_NAME","PG4_session")
app.permanent_session_lifetime = timedelta(minutes=30) # set session lifetime to 10mins 

def import_word():
    try:
        with open("static/wordsGuesser.txt","r") as file:
            content=file.read()
        dict_array=content.splitlines()
        return dict_array
    except:
        print("Unable to read word file")


def import_dict():
    try:
        with open("static/wordsGuesser.txt","r") as file:
            content=file.read()
        dict_array=content.splitlines()
        return dict_array
    except:
        with open("static/words.txt","r") as file:
            content=file.read()
        dict_array2=content.splitlines()
        return dict_array2

@app.route("/logout", methods=["GET"])
def clear():
    session.clear()
    return redirect("/")

@app.route("/resetscore")
def resetcookie():
    resp=make_response(redirect("/logout"))
    resp.set_cookie("score_cookie","0")
    return resp

@app.route("/reset-highscore")
def resethighscore():
    resp=make_response(redirect("/"))
    resp.set_cookie("highscore_cookie","0")
    return resp

@app.route("/", methods=["GET"]) # map the URL "/" for a function below
def begin():
    # read dict 
    try:
        if session.get("word", None) == None:
            dict_array=import_word()
            dict_array2=import_dict()
            session["word"] = dict_array[random.randint(0, len(dict_array) - 1)]
            session["history"] = list()

    except requests.exceptions.RequestException: # just handle exceptions regarding HTTP
        return Response("Something went wrong to retrieve data", mimetype='text/plain')

    lenWord=str(len(session["word"]))
    print("------------------------------\nWord is :",session["word"])
    # print(lenWord,"letters (begin1)")
    score=request.cookies.get("score_cookie")
    highscore=request.cookies.get("highscore_cookie")

    if score==None and highscore==None:
        score="0"
        highscore="0" 
    elif score==None:
        score="0"
    elif highscore==None:
        highscore="0"

    resp=make_response(render_template("wordle.html", current="", word=session["word"], history=session["history"], lenWord=lenWord,warn="",wordleft="6",score=score,highscore=highscore))
    resp.set_cookie("score_cookie",score)
    resp.set_cookie("highscore_cookie",highscore)
    return resp

@app.route("/", methods=["POST"]) # map the URL "/" for a function below
def ontheway():
    wordleftIn=6
    query = request.form["query"]
    score=request.cookies.get("score_cookie")
    highscore=request.cookies.get("highscore_cookie")
    score=int(score)
    highscore=int(highscore)

    try:
        dict_array=import_word()
        dict_array2=import_dict()
        word = session["word"]
        history = session["history"]
        lenWord = len(word)
        # lenWord = str(lenWordInt)
        # print(lenWord,"letters (begin2)")

        if len(query)>lenWord:
            # print("cut")
            query=query[:lenWord]
        elif len(query)<lenWord:
            warn=f"Your guess word is shorter than {lenWord} letters, try again."
            print("len",len(history),history)
            wordleftIn=6-len(history)
            return render_template("wordle.html", current=query, word=word, history=history, lenWord=lenWord, warn=warn, wordleft=wordleftIn, score=score, highscore=highscore)
        
        if query not in dict_array2:
            warn="Your guess words is not allowed!! Try again."
            wordleftIn=6-len(history)
            return render_template("wordle.html", current=query, word=word, history=history, lenWord=lenWord, warn=warn, wordleft=wordleftIn, score=score, highscore=highscore)
        history.append(query) # can't append directly like session["history"].append(query)
        historyLen=len(history)
        session["history"] = history
        wordleftIn-=historyLen
        # print(query)
        # print(lenWord)
        if wordleftIn<=0 and query!=word:
            resp=make_response(render_template("wordle.html", current=query, word=word, history=history, lenWord=lenWord, warn="Game over, try again!", wordleft=f"{wordleftIn} -- Answer is {word} --", score=0, highscore=highscore, reset=1))
            resp.set_cookie("score_cookie","0")
            return resp

        if query == word:
            score+=1
            if score>highscore:
                highscore=score
            resp=make_response(render_template("wordle.html", current=query, word=word, history=history, lenWord=lenWord, warn="",wordleft=wordleftIn,score=score,highscore=highscore))
            # score=request.cookies.get("score_cookie")
            resp.set_cookie("score_cookie",str(score))
            resp.set_cookie("highscore_cookie",str(highscore))
            session.clear()
            # print("correct")
            return resp
        else:
            # print("Incorrect")
            # return render_template("contact.html")
            return render_template("wordle.html", current=query, word=word, history=history, lenWord=lenWord, warn="", wordleft=wordleftIn, score=score, highscore=highscore)
    except Exception as e:
        print(e)
        return Response("Something went wrong to retrieve data: " + str(e), mimetype='text/plain')


if __name__=="__main__":
    app.run()