from app import app
from flask import render_template, request, url_for
import classes
import datetime, time, json

@app.route('/', methods=['GET','POST'])
def index():
    return render_template('index.html')

@app.route('/timeline', methods=['GET','POST'])
def timeline():
    print request.form
    stoves = int(request.form['stove_number'])
    ovens = int(request.form['oven_number'])
    recipes = request.form.getlist('recipe')
    for recipe in recipes:
    	recipe = recipe.encode('ascii')
    finish_time = datetime.datetime.strptime(str(request.form['finish_time']), '%Y-%m-%dT%H:%M')

    creator = classes.ScheduleCreator()
    print stoves
    print ovens
    print recipes
    print finish_time

    creator.create_schedule(stoves, ovens, *recipes)
    timeline = creator.S
    for recipe in timeline.recipes:
        for direction in recipe.directions:
            direction.start = time.mktime((finish_time + datetime.timedelta(minutes = direction.start)).timetuple()) * 1000
            direction.end = time.mktime((finish_time + datetime.timedelta(minutes = direction.end)).timetuple()) * 1000
            print direction.start
            print direction.end
    return render_template('vertical_timeline.html', timeline = timeline)