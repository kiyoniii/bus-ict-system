from flask_wtf import FlaskForm

from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Regexp


class NewUserForm(FlaskForm):
    username = StringField(
        "ユーザー名(半角英数字)",
        validators=[
            Regexp("^[0-9a-zA-Z]*$", message="半角英数字を入力してください"),
            DataRequired(message="ユーザー名を入力してください"),
        ],
    )
    password = PasswordField(
        "パスワード(半角英数字)",
        validators=[
            Regexp("^[0-9a-zA-Z]*$", message="半角英数字を入力してください"),
            DataRequired(message="パスワードを入力してください"),
        ],
    )
    submit = SubmitField("決定")
