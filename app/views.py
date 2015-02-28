from app import app
from flask import render_template, flash, redirect
from .forms import RecipeInputForm


@app.route('/', methods=['GET','POST'])
def index():
	form = RecipeInputForm()
	if form.validate_on_submit():
		#get rID from recipes
		rID_1 = 'recipetest1'
		rID_2 = 'recipetest2'
		return redirect('/vertical_timeline/%s/%s' % (rID_1, rID_2))
	else:
		print "error"
	return render_template('index.html',
		form=form)

@app.route('/vertical_timeline/<rID_1>/<rID_2>')
def vertical_timeline(rID_1, rID_2):
	return (rID_1 + rID_2)