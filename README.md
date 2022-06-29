# Klimadiskurs.info

A Flask/Heroku web app for the German climate change discourse.

This app lives on [http://klimadiskurs.herokuapp.com](http://klimadiskurs.herokuapp.com)
and [http://www.klimadiskurs.info](http://www.klimadiskurs.info]).

This README explains how to work with the app. See `Thesis.pdf` for theoretical background (in German).

## Running the app

After cloning this repo, create a new virtual environment and install the dependencies from `requirements.txt`. After activating the virtual environment you can run the app on [http://127.0.0.1:5000](http://127.0.0.1:5000) with `python run.py`

Flask watches for changes in the code base and automatically restarts the server when saving a Python file, don't forget to refresh your browser.

Note that environment variables are not stored in this repository but [directly on Heroku](https://devcenter.heroku.com/articles/config-vars#managing-config-vars). 
You'll need to create your own `.env` file in the root directory or request it from the project owner.

Sometimes JavaScript files are not loaded correctly in the local version. This works fine once deployed to Heroku.

## Repository structure

- `klimadiskurs` contains the app itself.
- `tools` contains the raw word list and stand-alone Python scripts for building the database. They are never accessed by the app itself.
The master files of all texts, `texts_contra.txt` and `texts_pro.txt`, are too large to be 
pushed to GitHub. They can be generated from the raw text files found in the 
[Climate Change Glossary](https://github.com/ajgoecke/climate_change_glossary) using
`create_master_text_files.py`
- The root directory contains this README, the thesis PDF and some Heroku files that must be placed
in the root directory.

## App structure

- `app` contains the app logic as Flask/Python files.
- `static` contains CSS, JavaScript, fonts, images, favicons and the JSON database in respective subdirectories.
The app currently uses only plain CSS and JavaScript (+ jQuery), no front-end frameworks.
- `templates` contains all Jinja2/HTML templates.

To add new functionality you'll most likely want to edit `app/routes.py` and the respective HTML template.

## Deployment

All changes to the `main` branch of this repository are automatically deployed to Heroku.

## External services

The app currently relies on three external services. All API keys are stored in the app config variables, 
other login data may be requested from the project owner.

- Twitter API: Needs [Academic Research access](https://developer.twitter.com/en/products/twitter-api/academic-research).
- GitHub API: All submissions as well as a list of tweeted terms are stored in [this repository](https://github.com/noelsimmel/klimadiskurs-files/)
and updated via the API.
- [Uptimerobot](https://uptimerobot.com/dashboard#791343305): Pings the app every 21 minutes to prevent idling.
Also shows various statistics like uptime and response time.

The klimadiskurs.info domain is hosted at [webspace4all](https://www.webspace4all.eu/).

## Handling submissions

All submissions are collected a TSV file that can be [downloaded from the website](https://klimadiskurs.herokuapp.com/download/submissions). Place the file in `tools` and edit it to keep only the submissions that should be transferred to the glossary, Excel is recommended, make sure to open with UTF-8 encoding. Then run `add_new_entries.py` to add the submissions to `glossary.json`

## Further reading

See the [Heroku Dev Center](https://devcenter.heroku.com/categories/reference) for help with all things Heroku.

See this [YouTube series](https://www.youtube.com/playlist?list=PL-osiE80TeTs4UjLw5MM6OjgkjFeUxCYH) for an introduction to Flask.

Questions? Please contact No&#235;l Simmel: noeldev [&#230;t] proton.me