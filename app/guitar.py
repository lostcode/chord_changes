from flask import Flask, render_template, request, jsonify
import datetime
import time
import shelve
import os
import collections

app = Flask(__name__)

# to transmit the csv import file
# use the enctype="multipart/form-data" on the html form
# to access, in flask, f = request.files['thefile']; f.save('dest_file.txt')

# cookies
# request.cookies.get('username') |
# resp = make_response(template); resp.set_cookie('username', 'the username')

SHELVE_FILENAME = "database"


@app.route('/')
def index():
    return render_template('changes.html')


@app.route('/hello/<name>')
def hello_world(name=None):
    return render_template('hello.html', name=name)

CHORDS_REQ_STR = 'chords'
NUM_CHANGES_REQ_STR = 'num_changes'
DURATION_REQ_STR = 'duration'


@app.route('/changes', methods=['POST'])
def post_changes():
    """
    :form prog: chord progression delimited by -
    :form date: optional which date, default today
    :form times: number of times
    :form sec: optional number of seconds, default 60
    """
    if NUM_CHANGES_REQ_STR not in request.form:
        return "need chords and num_changes", 400
    chord_a = request.form.get('a', '').lower()
    chord_b = request.form.get('b', '').lower()
    if not chord_a or not chord_b:
        return "need chords", 400

    num_changes = request.form.get(NUM_CHANGES_REQ_STR, "")
    if not num_changes:
        return "need num changes", 400

    chords = sorted([chord_a, chord_b])
    epoch_time = int(time.time())
    duration = request.form.get(DURATION_REQ_STR, 60)

    # insert the doc
    insert(chords, num_changes, epoch_time, duration)

    return 'created'


@app.route('/changes', methods=['GET'])
def get_changes():
    d = get_all()
    od = collections.OrderedDict(sorted(d.items(), reverse=True))
    results = []
    for key, value in od.iteritems():
        doc = {'time': key}
        doc.update(value)
        results.append(doc)
    return jsonify(results=results)


def insert(chords, num_changes, epoch_time, duration):

    doc = {CHORDS_REQ_STR: chords, NUM_CHANGES_REQ_STR: num_changes, DURATION_REQ_STR: duration}
    d = shelve.open(SHELVE_FILENAME, writeback=True)
    try:
        d[str(epoch_time)] = doc
    finally:
        d.close()


def get_all():
    if not os.path.isfile(SHELVE_FILENAME + '.db'):
        return {}
    d = shelve.open(SHELVE_FILENAME, 'r')
    try:
        return dict(d)
    finally:
        d.close()


def get_date(req):
    return datetime.datetime.strptime(req, '%Y-%m-%d') if req else datetime.datetime.now()

if __name__ == "__main__":
    app.run(debug=True)
