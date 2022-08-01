# requirements
# pip install flask
# pip install flask-boostrap
# pip install -U pip setuptools wheel
# pip install -U spacy
# python -m spacy download en_core_web_sm
# python -m spacy download es_core_news_sm
# pip install textblob
# pip install wordcloud

# venv\scripts\activate
# pip freeze
# flask run

from html import entities
import matplotlib.pyplot as plt
from pprint import pprint
from SPARQLWrapper import SPARQLWrapper, JSON, N3
from rdflib import Graph
import time
import random
from io import BytesIO
from wordcloud import WordCloud
from flask import Flask, url_for, request, render_template, jsonify, send_file
from flask_bootstrap import Bootstrap
import json

# NLP Pkgs
import spacy
from textblob import TextBlob
nlp = spacy.load("es_core_news_sm")
# nlp = spacy.load("en_core_web_sm")


# WordCloud & Matplotlib Packages


# Initialize App
app = Flask(__name__)
Bootstrap(app)


@app.route('/')
def index():
	return render_template('index.html')


@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
	start = time.time()
	# Receives the input query from form
	

	if request.method == 'POST':
		rawtext = request.form['rawtext']
		# Analysis

		docx = nlp(rawtext)
		for ent in docx.ents:
			if ent.label_ in ['LOC', 'GPE']:
				print(ent.text, ent.label_)

		# Tokens
		custom_tokens = [token.text for token in docx]
		# NER
		# custom_namedentities = []
		custom_namedentities = [(entity.text, entity.label_)for entity in docx.ents]
		entitieslabel = [(entity.text)for entity in docx.ents]
		# for ent in docx.ents:

		# print(custom_namedentities)
		# print("arriba")

		sparql = SPARQLWrapper('https://dbpedia.org/sparql')
		print(entitieslabel[0])
		val = entitieslabel[0]

		val = val.replace (' ', '_')
		print(val)
		sparql.setQuery(f'''
    		SELECT ?object ?image
    		WHERE {{ dbr:{val} rdfs:label ?object .
					dbr:{val} dbo:thumbnail ?image .}}
		''')
		sparql.setReturnFormat(JSON)
		qres = sparql.query().convert()
		
		print(qres)
		for result in qres['results']['bindings']:
    	# print(result['object'])
    		
			lang, value, imag = result['object']['xml:lang'], result['object']['value'], result['image']['value']
    		
			
			print("el resultado")
			
			print(f'Lang: {lang}\tValue: {value}\Image: {imag}')

			
		result_img = [(result['image']['value'])for result in qres['results']['bindings']]
		result_lan = [(result['object']['xml:lang'], result['object']['value'])for result in qres['results']['bindings']]
		
		blob = TextBlob(rawtext)
		blob_sentiment, blob_subjectivity = blob.sentiment.polarity, blob.sentiment.subjectivity
		allData = [('"Token":"{}","Tag":"{}","POS":"{}","Dependency":"{}","Lemma":"{}","Shape":"{}","Alpha":"{}","IsStopword":"{}"'.format(
		    token.text, token.tag_, token.pos_, token.dep_, token.lemma_, token.shape_, token.is_alpha, token.is_stop)) for token in docx]

		result_json = json.dumps(allData, sort_keys=False, indent=2)

		end = time.time()
		final_time = end-start
	
	
	return render_template('index.html',ctext=rawtext,custom_tokens=custom_tokens,custom_namedentities=custom_namedentities,result_json=result_json,result_lan=result_lan, result_img= result_img)




	