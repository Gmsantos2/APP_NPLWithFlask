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


from pprint import pprint
from SPARQLWrapper import SPARQLWrapper, JSON, N3

# flask
from flask import Flask, url_for, request, render_template, jsonify, send_file
from flask_bootstrap import Bootstrap
import json

# NLP Pkgs
import spacy
nlp = spacy.load("es_core_news_sm")
# nlp = spacy.load("en_core_web_sm")



# Initialize App
app = Flask(__name__)
Bootstrap(app)


#ruta inicial donde nos devuelve la página principal
@app.route('/')
def index():
	return render_template('index.html')


#ruta de analisis del texto enviado por el metodo post
@app.route('/analyze', methods=['GET', 'POST'])

#funcion que me devuelve el template de mi página con algunos atributos a presetar (tokens, entidades, resultados de la consulta a dbpedia)
def analyze():
	

	if request.method == 'POST':
		rawtext = request.form['rawtext']
		# Analysis
		docx = nlp(rawtext)

		# Tokens
		custom_tokens = [token.text for token in docx]
		# NER

		#entidades
		custom_namedentities = [(entity.text, entity.label_)for entity in docx.ents]
		entitieslabel = [(entity.text)for entity in docx.ents]


		#especificacion hacia que servicio de datos nos vamos a comunicar (dbpedia sparql) para hacer la consulta 
		sparql = SPARQLWrapper('https://dbpedia.org/sparql')
		
		#print de prueba
		print(entitieslabel[0])
		val = entitieslabel[0]

		val = val.replace (' ', '_')
		
		#print de prueba
		print(val)

		#consulta a dbpedia desde dbpedia sparql 
		sparql.setQuery(f'''
    		SELECT ?object ?image
    		WHERE {{ dbr:{val} rdfs:label ?object .
					dbr:{val} dbo:thumbnail ?image .}}
		''')
		sparql.setReturnFormat(JSON)
		qres = sparql.query().convert()
		
		#print de prueba
		print(qres)
		for result in qres['results']['bindings']:
    	# print(result['object'])
    		
			lang, value, imag = result['object']['xml:lang'], result['object']['value'], result['image']['value']
    		
			
			print("el resultado")
			
			print(f'Lang: {lang}\tValue: {value}\Image: {imag}')

		#obtencion de valores resultantes de la consulta	
		result_img = [(result['image']['value'])for result in qres['results']['bindings']]
		result_lan = [(result['object']['xml:lang'], result['object']['value'])for result in qres['results']['bindings']]
		
		#información de la palabra que nos brinda el componente del modelo de spacy
		allData = [('"Token":"{}","Tag":"{}","POS":"{}","Dependency":"{}","Lemma":"{}","Shape":"{}","Alpha":"{}","IsStopword":"{}"'.format(
		    token.text, token.tag_, token.pos_, token.dep_, token.lemma_, token.shape_, token.is_alpha, token.is_stop)) for token in docx]

		result_json = json.dumps(allData, sort_keys=False, indent=2)

	
	return render_template('index.html',ctext=rawtext,custom_tokens=custom_tokens,custom_namedentities=custom_namedentities,result_json=result_json,result_lan=result_lan, result_img= result_img)




	