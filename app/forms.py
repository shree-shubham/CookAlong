from flask.ext.wtf import Form
from wtforms import StringField, DateTimeField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Optional

class RecipeInputForm(Form):
	recipe_1 = StringField('recipe_1', validators=[DataRequired()])
	recipe_2 = StringField('recipe_2', validators=[Optional()])
	recipe_3 = StringField('recipe_3', validators=[Optional()])
	recipe_4 = StringField('recipe_3', validators=[Optional()])
	stoves = IntegerField('stoves', validators=[Optional()])
	ovens = IntegerField('ovens', validators=[Optional()])
	finish_time = DateTimeField('finish_time', validators=[Optional()])
