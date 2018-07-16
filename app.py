import base64
import json
import os
import io
import scipy.misc
from flask import (
    Flask,
    render_template,
    url_for,
    request,
    redirect,
    flash,
    send_from_directory,
    jsonify,
    Response,
    make_response,
    send_file,
)
from werkzeug.datastructures import Headers
from werkzeug.utils import secure_filename
from rpc_client import FibonacciRPCClient
from neural_style_client import NeuralStyleRPCClient

UPLOAD_FOLDER = "./static/uploads/"
ALLOWED_EXTENSIONS = set(["txt", "pdf", "png", "jpg", "jpeg", "gif"])

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = os.path.abspath(UPLOAD_FOLDER)
# Limit the upload size to 16MB
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

fibonacci_rpc = FibonacciRPCClient()
neural_style_rpc = NeuralStyleRPCClient()


@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")


@app.route("/echo/<name>", methods=["GET", "POST"])
def greeting(name):
    raw = request.args.get("raw", 0)
    return "Glad to meet you, {} in this form: {}!".format(name, raw)


@app.route("/fib/<number>")
def fibonacci(number):
    resp = fibonacci_rpc.call(int(number))
    return jsonify(resp)


@app.route("/info")
def env_info():
    return os.getenv("VCAP_SERVICES", "")


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/upload/", methods=["GET", "POST"])
def process_file():
    if request.method == "POST":
        # check if the post request has the file part
        if "filename" not in request.files:
            flash("No file part")
            return redirect(request.url)
        file = request.files["filename"]
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == "":
            flash("No selected file")
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            return redirect(url_for("uploaded_file", filename=filename))
    return redirect(url_for("index"))


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    if request.args.get("raw"):
        return send_file(
            os.path.join(app.config["UPLOAD_FOLDER"], filename),
            mimetype="image/jpeg",
            attachment_filename="tmp.jpg",
        )
    else:
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


@app.route("/transform/", methods=["GET", "POST"])
def transform_file():
    if request.method == "POST":
        # check if the post request has the file part
        if "filename" not in request.files:
            flash("No file part")
            return redirect(request.url)
        file = request.files["filename"]
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == "":
            flash("No selected file")
            return redirect(request.url)
        if file and allowed_file(file.filename):
            # filename = secure_filename(file.filename)
            # file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            # Send a request to style_transfer program with this file and expect a response to saved file location
            msg = {
                "filename": file.filename,
                "content": base64.b64encode(file.read()).decode(),
                "content_type": file.content_type,
                "num_iterations": request.args.get('num_iterations', 1),
            }
            resp = neural_style_rpc.call(json.dumps(msg))
            resp = json.loads(resp)

            if request.args.get("raw", "0") == "1":
                # send binary
                return send_file(
                    io.BytesIO(base64.b64decode(resp["content"].encode())),
                    mimetype="image/jpeg",
                    attachment_filename="tmp.jpg",
                )
            else:
                # send usual
                return jsonify(resp)

            # return jsonify(resp)

            # scipy.misc.imsave(
            #     os.path.join(app.config["UPLOAD_FOLDER"], filename),
            #     scipy.misc.imresize(
            #         scipy.misc.imread(
            #             os.path.join(app.config["UPLOAD_FOLDER"], filename)
            #         ),
            #         size=05,
            #     ),
            # )

    return render_template("transform.html", q_string=request.query_string.decode())


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    # Run the app, listening on all IPs with our chosen port number
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)
