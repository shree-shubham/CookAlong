from app import app
from flask import render_template, flash, redirect
from .forms import RecipeInputForm
import logic

@app.route('/', methods=['GET','POST'])
def index():
	form = RecipeInputForm()
	if form.validate_on_submit():
		if form.recipe_1.data:
			rID_1 = logic.get_rID(form.recipe_1.data)
		if form.recipe_2.data:
			rID_2 = logic.get_rID(form.recipe_2.data)
		# if form.recipe_3:
		# 	rID_3 = logic.get_rID(form.recipe_3)
		# if form.recipe_4:
		# 	rID_4 = logic.get_rID(form.recipe_4)
		schedule = logic.Schedule(form.recipe_1.data, form.recipe_2.data)
		# get directions
		return render_template('vertical_timeline.html', schedule = schedule)
	else:
		flash('Sorry, there seems to be a problem with the form')
	return render_template('index.html',
		form=form)