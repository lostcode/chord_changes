from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
import datetime

app = Flask(__name__)

# to transmit the csv import file
# use the enctype="multipart/form-data" on the html form
# to access, in flask, f = request.files['thefile']; f.save('dest_file.txt')

# cookies
# request.cookies.get('username') |
# resp = make_response(template); resp.set_cookie('username', 'the username')

client = MongoClient()

@app.route('/hello/<name>')
def hello_world(name=None):
    return render_template('hello.html', name=name)

@app.route('/changes', methods=['POST'])
def post_changes():
    """
    :form prog: chord progression delimited by -
    :form date: optional which date, default today
    :form times: number of times
    :form sec: optional number of seconds, default 60
    """
    prog = request.form['prog'].split('-')
    times = request.form['times']
    date = get_date(request.form.get('date'))
    duration = request.form.get('duration') or 60

    # insert the doc
    insert_doc({
        'prog': prog,
        'date': date,
        'times': times,
        'duration': duration
    })

    return 'created'


@app.route('/changes', methods=['GET'])
def get_changes():
    # todo should be default today...now

    if not request.args.get('start'):
        start = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        start = get_date(request.args['start'])

    end = get_date(request.args.get('end'))
    return jsonify(results=get_docs(start, end))


@app.route('/changes', methods=['DELETE'])
def delete_changes():
    raise NotImplementedError('delete not yet implemented')


def insert_doc(doc):
    db = client.guitar
    chord_changes = db.chord_changes
    post_id = chord_changes.insert(doc)
    return post_id


def get_docs(start, end):
    db = client.guitar
    chord_changes = db.chord_changes
    docs = []
    for doc in chord_changes.find({'date': {"$gte": start, "$lte": end}}):
        del doc['_id']
        docs.append(doc)
    return docs


def get_date(req):
    return datetime.datetime.strptime(req, '%Y-%m-%d') if req else datetime.datetime.now()

if __name__ == "__main__":
    app.run(debug=True)
