from flask import request, jsonify, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from database import *
from linear_regression import *
from generate import generate_question, generate_choices
from test_data import users_list

login_manager = LoginManager()
login_manager.init_app(app)

with app.app_context():
    db.create_all()


# Uncomment for local testing
# @login_manager.user_loader
# def load_user(user_id):
#     return User.query.get(int(user_id))


# Comment for local testing
@login_manager.request_loader
def load_user_from_request(req):
    user_id = req.headers.get('id')
    return User.query.get(int(user_id))


@login_manager.unauthorized_handler
def unauthorized():
    message = {'message': 'Nisi prijavljen.'}
    return jsonify(message), 401, {'Content-Type': 'application/json'}


@app.route('/addTestData', methods=['POST'])
def add_test_data():
    leaderboard_table = determine_leaderboard_table("addition")

    # Iterate over the list of users
    for user_dict in users_list:
        # Create a new User instance
        new_user = User(email=user_dict['email'], username=user_dict['username'], password=user_dict['password'])
        # Add the user to the database
        db.session.add(new_user)
        db.session.commit()
        # Create a new Leaderboard entry for the user
        new_entry = leaderboard_table(user_id=new_user.id, score=user_dict['score'])
        # Add the leaderboard entry to the database
        db.session.add(new_entry)
        db.session.commit()

    return '', 201


@app.route('/register', methods=['POST'])
def register():
    data = request.json
    try:
        exists = User.query.filter_by(email=data.get('email')).first()
        if not exists:
            user = User(email=data.get('email'), username=data.get('username'), password=data.get('password'))
            db.session.add(user)
            db.session.commit()
            return jsonify({'username': user.username, 'password': data.get('password')}), 201, \
                {'Content-Type': 'application/json'}
        else:
            message = {'message': 'E-mail zauzet.'}
            return jsonify(message), 400, {'Content-Type': 'application/json'}
    except ValueError as e:
        return jsonify({'message': e.args[0]}), 400


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data.get('username')).first()
    if user and bcrypt.checkpw(data.get('password').encode('utf-8'), user.password.encode('utf-8')):
        login_user(user)
        return jsonify({'id': str(user.id), 'username': user.username, 'password': data.get('password')}), 200, \
            {'Content-Type': 'application/json'}
    else:
        message = {'message': 'Krivi nadimak ili lozinka.'}
        return jsonify(message), 401, {'Content-Type': 'application/json'}


@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    message = {'message': 'Odjavljen.'}
    return jsonify(message), 200, {'Content-Type': 'application/json'}


@app.route("/gameSettings", methods=["POST"])
@login_required
def set_game_mode():
    user = User.query.get(current_user.id)
    new_game_mode = request.json["type"]
    user.game_mode = new_game_mode
    new_level = request.json["level"]
    user.level = new_level
    db.session.commit()
    return '', 200


@app.route("/questions", methods=['GET'])
@login_required
def get_questions():
    questions = []
    num_questions = 10
    user = User.query.get(current_user.id)
    game_mode = user.game_mode
    level = user.level
    for i in range(num_questions):
        question, answer = generate_question(game_mode, level)
        choices = generate_choices(answer, level)
        questions.append({"question": question, "choices": choices, "answer": answer})
    return jsonify({"questions": questions}), 200, {'Content-Type': 'application/json'}


@app.route("/answers", methods=["POST"])
@login_required
def send_answers():
    data = request.json
    user = User.query.get(current_user.id)
    game_mode = user.game_mode
    level = user.level
    total_time = int(float(data["time"]))
    score = sum(data["answers"]) / len(data["answers"]) * 100 * level

    # Deduct one point for every second taken
    time_deduction = total_time
    score -= time_deduction

    # Set score to 0 if it's negative
    if score < 0:
        score = 0

    # Determine which leaderboard table to query
    try:
        leaderboard_table = determine_leaderboard_table(game_mode)
    except ValueError as e:
        return jsonify({'message': e.args[0]}), 400

    # Add scores
    new_score = Score(current_user.id, game_mode, score)
    db.session.add(new_score)
    db.session.commit()

    # AI
    median = 0
    scores = get_last_3_scores(game_mode=game_mode, user_id=current_user.id)
    for value in scores:
        median += value.score
    if not len(scores) == 0:
        median = median / len(scores)

    last_score = get_last_score(user_id=current_user.id, game_mode=game_mode)

    new_median = MedianValues(user_id=current_user.id, game_mode=game_mode, median=median, last_score=last_score)
    db.session.merge(new_median)
    db.session.commit()

    leaderboard = db.session.query(leaderboard_table).filter_by(user_id=current_user.id).first()
    if not leaderboard:
        # Create a new Leaderboard entry for the user
        new_entry = leaderboard_table(user_id=current_user.id, score=int(score))
        # Add the leaderboard entry to the database
        db.session.add(new_entry)
    else:
        # Update Leaderboard entry for the user if higher
        if leaderboard.score < int(score):
            leaderboard.score = int(score)
    db.session.commit()
    return '', 200


# @app.route('/leaderboard', methods=['GET'])
# @login_required
# def get_leaderboard_of_last_game():
#     user = User.query.get(current_user.id)
#     game_mode = user.game_mode
#     if not game_mode:
#         message = {'message': 'Missing game_mode parameter in the query string.'}
#         return jsonify(message), 400, {'Content-Type': 'application/json'}
#     return redirect(url_for('get_leaderboard', game_mode=game_mode))


@app.route('/leaderboard/<string:game_mode>', methods=['POST'])
@login_required
def get_leaderboard(game_mode):
    data = request.json
    message = None

    if get_count(game_mode) > 10 and data["afterGame"]:
        user = User.query.get(current_user.id)
        level = user.level
        # Train
        model = treniraj(get_all_medians(game_mode), get_all_last_scores(game_mode))
        # Predict
        prediction = predvidi(get_last_score(game_mode, current_user.id), model)
        # Message
        message = vrati_poruku(predvidjeni_bodovi=prediction, realni_bodovi=get_last_score(game_mode, current_user.id),
                               level=level)

    # Determine which leaderboard table to query
    try:
        leaderboard_table = determine_leaderboard_table(game_mode)
    except ValueError as e:
        return jsonify({'message': e.args[0]}), 400

    # Query the leaderboard data from the selected table
    leaderboard_data = leaderboard_table.query.order_by(leaderboard_table.score.desc()).all()

    # Create an empty list to store the data
    leaderboard_list = []

    # Loop through the leaderboard data and append the ranking, user, and score to the list
    ranking = 1
    for data in leaderboard_data:
        leaderboard_list.append({
            "ranking": ranking,
            "username": data.user.username,
            "score": data.score,
            "isTopThree": True if ranking <= 3 else False,
            "isUser": True if current_user.id == data.user.id is not None else False
        })
        ranking += 1

    # Return the leaderboard data as a JSON object
    return jsonify({'items': leaderboard_list, 'message': message}), 200, {'Content-Type': 'application/json'}


if __name__ == '__main__':
    app.run(debug=True)
