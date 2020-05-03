#!flask_api_todo/bin/python

from flask import Flask, jsonify, abort, make_response, request, url_for

app = Flask(__name__)

tasks = [

    {
        'id': 1,
        'title': 'First Task',
        'description': 'Flask, Django',
        'done': False
    },
    {
        'id': 2,
        'title': 'Second Task',
        'description': 'Mysql, Perl, JS',
        'done': False
    }
]

# Convert id to URL
def make_public_task(task):
    new_task = {}
    for field in task:
        if field == 'id':
            new_task['url'] = url_for('get_task', task_id=task['id'], _external=True)
        else:
            new_task[field] = task[field]
    return new_task


# If you don't write our own error response then Flask will send the response in HTML format
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not Found'}), 404)

@app.errorhandler(400)
def incorrect_request(error):
    return make_response(jsonify({'error': 'Incorrect Request'}), 400)

# curl http://localhost:5000/todo/api/V1.0/tasks
@app.route('/todo/api/V1.0/tasks', methods=['GET'])
def get_tasks():
    return jsonify({'tasks': list(map(make_public_task, tasks))})
    return jsonify({'tasks': [make_public_task(task) for task in tasks]})


# curl http://localhost:5000/todo/api/V1.0/tasks/2
@app.route('/todo/api/V1.0/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    return jsonify({'task': task[0]})


# Linux
# curl -i -H "Content-Type: application/json" -X POST -d '{"title":"Read a book"}' http://localhost:5000/todo/api/v1.0/tasks
# Windows
# curl -i -H "Content-Type: application/json" -X POST -d "{\"title\":\"Read a book\"}" http://localhost:5000/todo/api/V1.0/tasks

@app.route('/todo/api/V1.0/tasks', methods=['POST'])
def create_task():
    if not request.json or not 'title' in request.json:
        abort(400)

    task = {
        'id': tasks[-1]['id'] + 1,
        'title': request.json['title'],
        'description': request.json.get('description', ''),
        'done': False
    }
    tasks.append(task)
    return jsonify({'task':task}), 201

# curl -i -H "Content-Type: application/json" -X PUT -d '{"done":true}' http://localhost:5000/todo/api/V1.0/tasks/2
# curl -i -H "Content-Type: application/json" -X PUT -d "{\"done\":true}" http://localhost:5000/todo/api/V1.0/tasks/2
@app.route('/todo/api/V1.0/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = [task for task in tasks if task['id'] == task_id]

    # If no record found for given task_id
    if len(task) == 0:
        abort(404)

    # If no data provided
    if not request.json:
        abort(400)

    for field, ftype in {'title':str, 'description':str, 'done':bool}.items():
        if field in request.json and type(request.json[field]) is not ftype:
            abort(400)
    task[0]['title'] = request.json.get('title', task[0]['title'])
    task[0]['description'] = request.json.get('description', task[0]['description'])
    task[0]['done'] = request.json.get('done', task[0]['done'])

    return jsonify({'task': task[0]})

# curl -i -H "Content-Type: application/json" -X DELETE  http://localhost:5000/todo/api/V1.0/tasks/2
@app.route('/todo/api/V1.0/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(400)
    tasks.remove(task[0])

    return jsonify({'result': True})


if __name__ == '__main__':
    app.run(debug=True)