from flask.ext.wtf import Form
from wtforms import StringField, DateTimeField, IntegerField, SubmitField
from wtforms.validators import DataRequired

class RecipeInputForm(Form):
	recipe_1 = StringField('recipe_1', validators=[DataRequired()])
	recipe_2 = StringField('recipe_2')
	stoves = IntegerField('stoves', validators=[DataRequired()])
	ovens = IntegerField('ovens', validators=[DataRequired()])
	finish_time = DateTimeField('finish_time', validators=[DataRequired()])
