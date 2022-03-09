from __future__ import division
from flask import Flask, render_template, request, url_for,send_from_directory,session,redirect,make_response,jsonify
#from lxml import html;
# from werkzeug import secure_filename
import os
import re
import binascii


# from helpers import ElementToShow
from mlModule.FastPredict import FastPredict

from mlModule.Predict23LSTM import Predictor23LSTM

from SimilarUIRoutes import similarUIRoutes
from SUTutorialRoutes import sUTutorialRoutes

# Setting all folders
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'templates/uploads')
STYLESHEETS_FOLDER = os.path.join(APP_ROOT, 'templates','stylesheets')
IMAGES_FOLDER = os.path.join(APP_ROOT, 'templates','images')
FONTS_FOLDER = os.path.join(APP_ROOT, 'templates','fonts')
FONTS_AWESOME_CSS_FOLDER = os.path.join(APP_ROOT, 'templates','font-awesome','css')
FONTS_AWESOME_FONTS_FOLDER = os.path.join(APP_ROOT, 'templates','font-awesome','fonts')
SCRIPTS_FOLDER = os.path.join(APP_ROOT, 'templates','javascripts')
STORAGE_FOLDER = os.path.join(APP_ROOT, 'PrimaryScreenShots','StoreElement')
UI_IMAGES_FOLDER= os.path.join(APP_ROOT, 'PrimaryScreenShots','PrimaryFocus')
TURK_UI_IMAGES_FOLDER= os.path.join(APP_ROOT, 'PrimaryScreenShots','SecondBatch')
FULL_UI_IMAGES_FOLDER= os.path.join(APP_ROOT, 'PrimaryScreenShots','FullUI')

output_directory = os.path.join(APP_ROOT,'My23Records5')
export_dir = os.path.join(APP_ROOT,'My23Records5','tb')



ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg','PNG','JPG','JPEG'])
TemplateFolder = os.path.join(APP_ROOT, 'templates')
ProjectGenerateFolder = os.path.join(APP_ROOT, 'templates', 'sketchupload')




# Loading Model for faster prediction

PREDICTOR = Predictor23LSTM(export_dir,output_directory)
FASTPREDICT = FastPredict(PREDICTOR.classifier,PREDICTOR.example_input_fn)


app = Flask(__name__)
app.secret_key = "pix2appSMDrawKey"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Creating Blue Print for Tutorial and Similar Retrieval
app.register_blueprint(similarUIRoutes)
app.register_blueprint(sUTutorialRoutes)


@app.route('/ClassSelect/', methods=['GET', 'POST'])
def ClassSelect():
    if request.method == 'POST':
        session['CurrentClassLabel'] = str(request.form['selectClassLabel'])
    return "Success"

# Set Canvas Size for Retrieval
@app.route('/SetCanvasSize/', methods=['GET','POST'])
def SetCanvasSize(): 
    
    session['canvas_width'] =  request.form['canvas_width']    
    session['canvas_height'] =  request.form['canvas_height']    
    response = jsonify(success ="ok")
    return response


@app.route('/HomePage/')
def HomePage():
    return render_template('homepage.html')



@app.route('/sketchupload/<filename>')
def send_zip_file(filename):
    return send_from_directory(ProjectGenerateFolder, filename)

@app.route('/uploads/<filename>')
def send_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/stylesheets/<filename>')
def send_css(filename):
    return send_from_directory(STYLESHEETS_FOLDER, filename)

@app.route('/images/<filename>')
def send_img(filename):
    return send_from_directory(IMAGES_FOLDER, filename)

@app.route('/fonts/<filename>')  
def send_fonts(filename):
    return send_from_directory(FONTS_FOLDER, filename)

@app.route('/font-awesome/css/<filename>')
def send_fontawscss(filename):
    return send_from_directory(FONTS_AWESOME_CSS_FOLDER, filename)

@app.route('/font-awesome/fonts/<filename>')
def send_fontawsfont(filename):
    return send_from_directory(FONTS_AWESOME_FONTS_FOLDER, filename)
    

@app.route('/NewImage/<filename>')
def send_new_img(filename):

    curelement = ElementToShow.getElementName(UI_IMAGES_FOLDER )   
    session['current_element'] =  curelement
     
    curDrawingName= session['current_element']+ ".png"

    return send_from_directory(UI_IMAGES_FOLDER, curDrawingName)



@app.route('/ElementHeaderImage/<filename>')
def send_new_header_img(filename):
    if 'doodleHeader' in session:
        session['doodleHeader'] =  (int(session['doodleHeader'])+1)%3
    else:
        session['doodleHeader'] =  0
    
    curDrawingName= "row" + str(session['doodleHeader'])+ ".png"

    return send_from_directory(IMAGES_FOLDER, curDrawingName)


@app.route('/SimHeaderImage/<filename>')
def send_sim_header_img(filename):
    if 'simHeader' in session:
        session['simHeader'] =  (int(session['simHeader'])+1)%8
    else:
        session['simHeader'] =  0
    
    curDrawingName= "simrow" + str(session['simHeader'])+ ".png"

    return send_from_directory(IMAGES_FOLDER, curDrawingName)

@app.route('/TurkNewImage/<filename>')
def send_new_turk_img(filename):
   
    curDrawingName= session['current_element']+ ".jpg"

    return send_from_directory(FULL_UI_IMAGES_FOLDER, curDrawingName)

@app.route('/TurkCurentImage/<filename>')
def send_turk_interval_img(filename):


    curDrawingName=  session['current_element']+ ".jpg"
      
    return send_from_directory(FULL_UI_IMAGES_FOLDER, curDrawingName)

@app.route('/CurentImage/<filename>')
def send_interval_img(filename):


    curDrawingName=  session['current_element']+ ".png"
      
    return send_from_directory(UI_IMAGES_FOLDER, curDrawingName)

@app.route('/IntervalImage/<filename>')
def send_interval_blur_img(filename):

    newName = "blur.jpg"
    return send_from_directory(IMAGES_FOLDER, newName)
    
@app.route('/javascripts/<filename>')
def send_jss(filename):
    return send_from_directory(SCRIPTS_FOLDER, filename)

@app.route('/doodle/images/<filename>')
def send_fullUI_img(filename):
    return send_from_directory(IMAGES_FOLDER, filename)
if __name__ == "__main__":
    
    app.run(threaded=True)
