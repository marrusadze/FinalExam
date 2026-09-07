from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import (
    DateTimeField,
    FloatField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    NumberRange,
    Optional,
)

from app.models import CATEGORIES, CATEGORY_LABELS

_REQUIRED = "ეს ველი სავალდებულოა."


class RegisterForm(FlaskForm):
    name = StringField(
        "სახელი და გვარი", validators=[DataRequired(message=_REQUIRED), Length(max=100)]
    )
    email = StringField(
        "ელფოსტა",
        validators=[
            DataRequired(message=_REQUIRED),
            Email(message="ელფოსტის ფორმატი არასწორია."),
            Length(max=150),
        ],
    )
    password = PasswordField(
        "პაროლი",
        validators=[
            DataRequired(message=_REQUIRED),
            Length(min=6, message="მინიმუმ 6 სიმბოლო."),
        ],
    )
    confirm_password = PasswordField(
        "გაიმეორეთ პაროლი",
        validators=[
            DataRequired(message=_REQUIRED),
            EqualTo("password", message="პაროლები არ ემთხვევა."),
        ],
    )
    submit = SubmitField("რეგისტრაცია")


class LoginForm(FlaskForm):
    email = StringField(
        "ელფოსტა",
        validators=[DataRequired(message=_REQUIRED), Email(message="ელფოსტის ფორმატი არასწორია.")],
    )
    password = PasswordField("პაროლი", validators=[DataRequired(message=_REQUIRED)])
    submit = SubmitField("შესვლა")


class EventForm(FlaskForm):
    title = StringField(
        "სათაური", validators=[DataRequired(message=_REQUIRED), Length(max=150)]
    )
    short_description = StringField(
        "მოკლე აღწერა", validators=[DataRequired(message=_REQUIRED), Length(max=300)]
    )
    full_description = TextAreaField(
        "სრული აღწერა", validators=[DataRequired(message=_REQUIRED)]
    )
    location = StringField(
        "ადგილი (ქალაქი)",
        validators=[DataRequired(message=_REQUIRED), Length(max=150)],
        description="გამოიყენება ამინდის ვიჯეტისთვის, მაგ. „თბილისი“.",
    )
    event_date = DateTimeField(
        "თარიღი და დრო",
        format="%Y-%m-%dT%H:%M",
        validators=[DataRequired(message=_REQUIRED)],
    )
    ticket_price = FloatField(
        "ბილეთის ფასი",
        validators=[DataRequired(message=_REQUIRED), NumberRange(min=0, message="ფასი არ უნდა იყოს უარყოფითი.")],
        default=0.0,
    )
    organizer = StringField(
        "ორგანიზატორი", validators=[DataRequired(message=_REQUIRED), Length(max=150)]
    )
    category = SelectField(
        "კატეგორია",
        choices=[(c, CATEGORY_LABELS[c]) for c in CATEGORIES],
        validators=[DataRequired(message=_REQUIRED)],
    )
    submit = SubmitField("შენახვა")


class ProfileForm(FlaskForm):
    name = StringField(
        "სახელი და გვარი", validators=[DataRequired(message=_REQUIRED), Length(max=100)]
    )
    email = StringField(
        "ელფოსტა",
        validators=[
            DataRequired(message=_REQUIRED),
            Email(message="ელფოსტის ფორმატი არასწორია."),
            Length(max=150),
        ],
    )
    profile_pic = FileField(
        "პროფილის სურათი",
        validators=[
            Optional(),
            FileAllowed(["jpg", "jpeg", "png", "gif"], message="დაშვებულია მხოლოდ სურათი (jpg, png, gif)."),
        ],
    )
    submit = SubmitField("ცვლილებების შენახვა")
