import flask
from monitor import db_init
from pymongo import DESCENDING

app = flask.Flask(__name__)
app.secret_key = 'key'

coll = db_init()


@app.route('/')
def index_view():
    return flask.render_template('monitor.html')


@app.route('/chart/recent/cpu', methods=['GET'])
def chart_recent_cpu():
    labels = [60, 55, 50, 45, 40, 35, 30, 25, 20, 15, 10, 5, 0]
    data_lists = list(coll.find().sort("created_time", DESCENDING).limit(len(labels)))
    index_of_1min, index_of_5min, index_of_10min = 0, 1, 2
    recent_data_1min = [d['datasets']['cpu_load_data']['data'][index_of_1min] for d in data_lists]
    recent_data_5min = [d['datasets']['cpu_load_data']['data'][index_of_5min] for d in data_lists]
    recent_data_10min = [d['datasets']['cpu_load_data']['data'][index_of_10min] for d in data_lists]
    r = {
        'success': True,
        'labels': labels,
        'data': [recent_data_1min, recent_data_5min, recent_data_10min],
    }
    print('recent_cpu', r)
    return flask.jsonify(r)


@app.route('/chart/recent/mem', methods=['GET'])
def chart_recent_mem():
    labels = ['used memory', 'idle memory']
    data_dict = list(coll.find().sort("created_time", DESCENDING).limit(1))[0]
    recent_data = data_dict['datasets']['mem_io_data']['data'][1:3]
    r = {
        'success': True,
        'labels': labels,
        'data': recent_data,
    }
    print('recent_mem', r)
    return flask.jsonify(r)


if __name__ == "__main__":
    app.run(debug=True)
