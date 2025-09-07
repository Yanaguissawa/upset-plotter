from flask import Flask, request, jsonify, send_file
import pandas as pd
from upsetplot import UpSet, from_contents
import matplotlib.pyplot as plt
import io
import os

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_files():
    try:
        # Get uploaded files
        uploaded_files = request.files.getlist('files')
        columns = request.form.getlist('columns')
        
        # Read data from files
        data_contents = {}
        for i, file in enumerate(uploaded_files):
            if file.filename.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
            
            # Get the selected column
            col_name = columns[i]
            data_contents[file.filename] = set(df[col_name].dropna().astype(str).tolist())
        
        # Generate UpSet plot
        series = from_contents(data_contents)
        upset = UpSet(series, min_subset_size=10)
        
        # Create plot
        fig = plt.figure(figsize=(10, 6))
        upset.plot(fig=fig)
        
        # Save plot to bytes
        img_bytes = io.BytesIO()
        plt.savefig(img_bytes, format='png')
        img_bytes.seek(0)
        plt.close()
        
        return send_file(img_bytes, mimetype='image/png')
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)