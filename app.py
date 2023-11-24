# Import required packages
import os
from glob import glob
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from kalido import create_and_save_image

# Define constants
UPLOAD_FOLDER = './static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Set the app up
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000

# Checks if the passed filename is valid
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Remove all files from given directory
def remove_files(staticDir):
    files = glob(f'./static/{staticDir}/*')
    for f in files:
        os.remove(f)

# Display's the kaleidoscopic image, and let's the user click to download
@app.route('/uploads/<name>')
def display_image(name):
    create_and_save_image(name)
    return render_template('displayImage.html', name=name)

# The landing page of the website
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('display_image', name=file.filename))
        else:
            return redirect('/')
    
    # remove the uploaded and outputted files from their respective directories 
    remove_files("images")
    remove_files("output")
    
    return render_template('upload.html')