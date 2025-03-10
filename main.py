import os
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from flask import Flask
from flask import request
from flask import send_from_directory
from flask_cors import CORS
from flask_restful import Api
from flask_restful import Resource

PLOT_DIR = "plots"

application = Flask(__name__)
application.config["CORS_HEADERS"] = "Content-Type"
application.config["CORS_RESOURCES"] = {r"/api/*": {"origins": "*"}}
application.config["PROPAGATE_EXCEPTIONS"] = True

cors = CORS(application)
api = Api(application)


class Index(Resource):
    def get(self):
        return "Hello World"


class Plot(Resource):
    def post(self):
        data = request.get_json()
        response = {
            "code": 0,
            "message": ""
        }
        try:
            plot_description_str = data.get("plot_description", "{}")
            plot_data = json.loads(plot_description_str)
            x_values = plot_data["x_axis"].get("values", [])
            y_values = plot_data["y_axis"].get("values", [])
            num_paths = len(y_values)
            legend = plot_data.get("legend", [])
            plt.figure(figsize=(10, 6))
            for i in range(num_paths):
                plt.plot(x_values, y_values[i], label=legend[i])
            plt.legend(loc="best")
            plt.title(plot_data["title"])
            plt.xlabel(f"{plot_data['x_axis']['label']} ({plot_data['x_axis']['unit']})")
            plt.ylabel(f"{plot_data['y_axis']['label']} ({plot_data['y_axis']['unit']})")
            os.makedirs(PLOT_DIR, exist_ok=True)
            file_name = "brownian_motion.png"
            plot_path = os.path.join(PLOT_DIR, file_name)
            plt.savefig(plot_path)
            plt.close()
            full_url = request.host_url + "plots/" + file_name
            response["url"] = full_url
        except Exception as e:
            response["code"] = -1
            response["message"] = str(e)
        return response


@application.route("/plots/<filename>")
def get_plot(filename):
    return send_from_directory(PLOT_DIR, filename)


api.add_resource(Index, "/", endpoint="index")
api.add_resource(Plot, "/api/plot", endpoint="plot")

if __name__ == "__main__":
    # application.debug = True
    application.run(host="0.0.0.0", port=5050)
