# Forms file
# This currently only contains the EntrySubmitForm for suggesting new terms

from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, ValidationError
from klimadiskurs import db

class EntrySubmitForm(FlaskForm):
    # used for writing submissions to submissions.tsv
    fieldnames = ["term", "id", "definition", "sources", 
                  "association", "examples", "spellings", "related"]

    # anti-spam honeypot
    # https://dev.to/felipperegazio/how-to-create-a-simple-honeypot-to-protect-your-web-forms-from-spammers--25n8
    url = StringField("URL")

    term = StringField("Begriff", validators=[DataRequired()])
    definition = TextAreaField("Beobachtungen oder Stichpunkte zur Definition")
    association = StringField("""Dieser Begriff wird von Menschen verwendet, 
                                 die den menschengemachten Klimawandel...""")
    ass_pro = BooleanField("anerkennen")
    ass_con = BooleanField("nicht anerkennen")
    sources = TextAreaField("Quellen (erforderlich)", 
                            render_kw={"placeholder": "Eine Quelle pro Zeile eingeben"},
                            validators=[DataRequired(), Length(min=10)])
    examples = TextAreaField("Beispielsätze", 
                             render_kw={"placeholder": "Einen Satz pro Zeile eingeben"})
    submit = SubmitField("Absenden")

    def validate_term(self, term):
        """WTForms custom validator.
        https://wtforms.readthedocs.io/en/2.3.x/validators

        Args:
            term (Field): The filled-out term form field.

        Raises:
            ValidationError: If the term doesn't start with "Klima".
            ValidationError: If the term contains special characters that are not -.
            ValidationError: If the term already has a definition in the database.
        """

        if not term.data.lower().startswith("klima"):
            raise ValidationError("Das Wort muss mit \"Klima\" beginnen!")
        if not term.data.isalpha() and "-" not in term.data:
            raise ValidationError("Das Wort darf nur Buchstaben und Bindestriche (-) beinhalten.")
        # check if the word already exists in the database AND has a definition
        # this way users can either submit new words or provide definitions for existing words
        if self.__term_in_db(term.data) or self.__term_in_db(term.data):
            raise ValidationError("Dieses Wort hat bereits eine Definition.")

    def __term_in_db(self, term):
        """Helper function. Checks if the term is in db and has a definition."""

        result = (term in db and db[term]["definition"]) or \
                 (term.lower() in db and db[term.lower()]["definition"])
        return result
