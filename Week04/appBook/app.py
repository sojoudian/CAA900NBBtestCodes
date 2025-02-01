from flask import Flask, render_template, send_file

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/view")
def view_pdf():
    """
    Serves the PDF file inline so that it can be viewed in the browser.
    """
    pdf_path = "engineering-software-products-introduction.pdf"
    return send_file(pdf_path)

@app.route("/download")
def download_pdf():
    """
    Serves the PDF file as an attachment for download.
    """
    pdf_path = "engineering-software-products-introduction.pdf"
    return send_file(pdf_path, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5002)
