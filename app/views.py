from app import app
from flask import render_template, flash, redirect
from .forms import RecipeInputForm
import classes

@app.route('/', methods=['GET','POST'])
def index():
    form = RecipeInputForm()
    if form.validate_on_submit():
        if (form.recipe_1.data and form.recipe_2.data and form.ovens_numb.data and form.stoves_numb.data):
            creator = classes.ScheduleCreator()
            #timeline = creator.create_schedule(form.stoves_numb.data, form.ovens_numb.data, form.recipe_1.data, form.recipe_2.data) #this does nothing, timeline is none
            creator.create_schedule(form.stoves_numb.data, form.ovens_numb.data, form.recipe_1.data, form.recipe_2.data) #this does nothing, timeline is none
            return render_template('vertical_timeline.html', diction = Schedule(creator.S.export()))
        else:
            flash('Sorry, there seems to be a problem with the form')
    return render_template('index.html',form=form)
#    
#@app.route('/vertical_timeline/