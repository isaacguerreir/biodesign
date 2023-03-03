import os, io, json
from api import app
from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory
from Bio import SeqIO
from werkzeug.utils import secure_filename
import json

#Check file format functions
class checkit(object):

    def __init__(self, path):
        self.file = path
        
    def allowed_file(self, name):
        return '.' in name and name.rsplit('.', 1)[1].lower() in set(['fasta', 'fa', 'faa', 'gb'])

    def is_fasta(self):
        with open(self.file, 'r') as handle:
            fasta = SeqIO.parse(handle, "fasta")
            return any(fasta)
        
    def is_gb(self):
        with open(self.file, 'r') as handle:
            gb = SeqIO.parse(handle, "gb")
            return any(gb)

@app.route('/')
def hello_world():
    return 'Teste'

@app.route('/file-upload', methods=['GET', 'POST'])
def upload_file():

    file = request.files['file']
    filename = secure_filename(file.filename)
    path = os.path.join(app.config['UPLOAD_DIR'], app.config['UPLOAD_PATH'], filename)
    file.save(path) 
    checkformat = checkit(path)
	
    # check if the post request has the file part
    if 'file' not in request.files:
        resp = jsonify({'message' : 'No file part in the request'})
        resp.status_code = 400
        return resp
    
    #check if the post request has a file
    file.seek(0, os.SEEK_END)
    if file.tell() == 0:
        resp = jsonify({'message' : 'No file selected for uploading'})
        resp.status_code = 400
        return resp
    
    if file and checkformat.allowed_file(file.filename):
        
        if checkformat.is_fasta():
            
            resp = jsonify({'message' : 'Fasta format'})
            resp.status_code = 201
            annotation = []

            #Extract fasta content       
            for x in SeqIO.parse(path, 'fasta'):
                
                annotation.append({'ID': x.id, 'sequence': str(x.seq),'format':'fasta'})
                
            resp = json.dumps(annotation, indent = 1)

            return resp

        if checkformat.is_gb():

            x = SeqIO.parse(path, 'gb')
            resp = jsonify({'message' : 'Genbank format'})
            resp.status_code = 201
            return resp
        
        else:
            resp = jsonify({'message' : 'Corrupted file'})
            resp.status_code = 400
            return resp
    
    else:
        resp = jsonify({'message' : 'Allowed file types are fasta, fa, faa, gb'})
        resp.status_code = 400
        return resp
    
@app.route('/static/uploads/<filename>')
def upload(filename):
    return send_from_directory(app.config['UPLOAD_PATH'], filename)
    

if __name__ == "__main__":
    app.run(debug=True)