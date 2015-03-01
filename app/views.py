from app import app
from flask import render_template, flash, redirect
from .forms import RecipeInputForm
import classes
import datetime, time

@app.route('/', methods=['GET','POST'])
def index():
    form = RecipeInputForm()
    if form.validate_on_submit():
        if (form.recipe_1.data and form.ovens_numb.data and form.stoves_numb.data and form.finish_time):
            recipes_array = []
            if form.recipe_1.data:
                recipes_array.append(form.recipe_1.data)
            if form.recipe_2.data:
                recipes_array.append(form.recipe_2.data)
            if form.recipe_3.data:
                recipes_array.append(form.recipe_3.data)
            if form.recipe_4.data:
                recipes_array.append(form.recipe_4.data)
            creator = classes.ScheduleCreator()
            creator.create_schedule(form.stoves_numb.data, form.ovens_numb.data, *recipes_array)
            timeline = creator.S
            for recipe in timeline.recipes:
            	for direction in recipe.directions:
            		direction.start = time.mktime((form.finish_time.data + datetime.timedelta(minutes = direction.start)).timetuple()) * 1000
            		direction.end = time.mktime((form.finish_time.data + datetime.timedelta(minutes = direction.end)).timetuple()) * 1000
            return render_template('vertical_timeline.html', timeline = timeline)
        else:
            flash('Sorry, there seems to be a problem with the form')
    return render_template('index.html', form = form)