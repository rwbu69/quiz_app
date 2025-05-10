from flask import Flask, render_template, redirect, url_for, request, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from database.models import db, User, Question, QuizAttempt
from services.weather import WeatherService
from datetime import datetime
from database.db import init_app
from config import Config
from sqlalchemy import func
import requests
import locale
import random

app = Flask(__name__)
app.config.from_object(Config)
init_app(app)
locale.setlocale(locale.LC_TIME, "id_ID.UTF-8")


def get_current_user():
    if "user_id" in session:
        return User.query.get(session["user_id"])
    return None


@app.template_filter("id_date")
def indonesian_date_filter(date_str):
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    return date_obj.strftime("%d %B %Y")


@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            flash("Login successful!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password", "danger")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        password_confirm = request.form["password_confirm"]
        nickname = request.form["nickname"]
        email = request.form.get("email", "")

        errors = []

        if User.query.filter_by(username=username).first():
            errors.append("Username sudah digunakan")

        if User.query.filter_by(nickname=nickname).first():
            errors.append("Nama panggilan sudah digunakan")

        if password != password_confirm:
            errors.append("Konfirmasi password tidak sesuai")

        if len(password) < 8:
            errors.append("Password minimal 8 karakter")

        if errors:
            for error in errors:
                flash(error, "danger")
            return redirect(url_for("register"))

        new_user = User(
            username=username,
            password=generate_password_hash(password),
            nickname=nickname,
            email=email,
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Pendaftaran berhasil! Silakan login", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/", methods=["GET", "POST"])
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    location = "Jakarta"  # Default location
    weather_data = None

    if request.method == "POST":
        location = request.form.get("location", "Jakarta")

    if location:
        weather_data = WeatherService.get_forecast(location)

    # Prepare forecast data
    forecast_days = []
    if weather_data and "forecast" in weather_data:
        for day in weather_data["forecast"]["forecastday"]:
            date_obj = datetime.strptime(day["date"], "%Y-%m-%d")
            forecast_days.append(
                {
                    "date": day["date"],
                    "day_name": date_obj.strftime("%A"),
                    "date_formatted": date_obj.strftime("%d %B %Y"),
                    "day_temp": day["day"]["maxtemp_c"],
                    "night_temp": day["day"]["mintemp_c"],
                    "condition": day["day"]["condition"]["text"],
                    "icon": day["day"]["condition"]["icon"],
                    "sunrise": day["astro"]["sunrise"],
                    "sunset": day["astro"]["sunset"],
                }
            )

    return render_template(
        "dashboard.html",
        current_user=get_current_user(),
        location=location,
        forecast=forecast_days,
        current_weather=weather_data["current"] if weather_data else None,
    )


@app.route("/weather")
def get_weather():
    if not Config.WEATHER_API_KEY:
        return jsonify({"error": "Weather API not configured"}), 500  # noqa: F821

    try:
        params = {"key": Config.WEATHER_API_KEY, "q": "Indonesia", "aqi": "no"}

        response = requests.get(Config.WEATHER_API_URL, params=params, timeout=10)
        response.raise_for_status()

        weather_data = response.json()

        return jsonify(  # noqa: F821
            {
                "location": weather_data["location"]["name"],
                "temp_c": weather_data["current"]["temp_c"],
                "condition": weather_data["current"]["condition"]["text"],
                "icon": weather_data["current"]["condition"]["icon"],
                "last_updated": weather_data["current"]["last_updated"],
            }
        )

    except requests.exceptions.RequestException as e:
        app.logger.error(f"Weather API error: {str(e)}")
        return jsonify({"error": "Unable to fetch weather data"}), 500  # noqa: F821


@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))

    # Handle finish quiz request
    if request.method == "POST" and "finish_quiz" in request.form:
        return redirect(url_for("quiz_result"))

    question = Question.query.order_by(func.random()).first()

    if request.method == "POST" and "answer" in request.form:
        # Process answer
        question_id = request.form.get("question_id")
        selected_option = int(request.form.get("answer"))
        question = Question.query.get(question_id)

        if question:
            is_correct = selected_option == question.correct_option

            if is_correct:
                user.total_score += 10
                flash("Benar! +10 poin", "success")
            else:
                correct_answer = getattr(question, f"option{question.correct_option}")
                flash(f"Salah! Jawaban benar: {correct_answer}", "danger")

            attempt = QuizAttempt(
                user_id=user.id,
                question_id=question.id,
                selected_option=selected_option,
                is_correct=is_correct,
            )
            db.session.add(attempt)
            db.session.commit()

        return redirect(url_for("quiz"))

    # Randomize answer options for GET request
    options = []
    if question:
        options = [
            {"value": 1, "text": question.option1},
            {"value": 2, "text": question.option2},
            {"value": 3, "text": question.option3},
            {"value": 4, "text": question.option4},
        ]
        random.shuffle(options)

    return render_template(
        "quiz.html", current_user=user, question=question, options=options
    )

    # Acak urutan opsi jawaban untuk GET request
    options = []
    if question:
        options = [
            {"value": 1, "text": question.option1},
            {"value": 2, "text": question.option2},
            {"value": 3, "text": question.option3},
            {"value": 4, "text": question.option4},
        ]
        random.shuffle(options)

    return render_template(
        "quiz.html", current_user=user, question=question, options=options
    )


@app.route("/quiz_result")
def quiz_result():
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))

    total_questions = QuizAttempt.query.filter_by(user_id=user.id).count()
    correct_answers = QuizAttempt.query.filter_by(
        user_id=user.id, is_correct=True
    ).count()
    incorrect_answers = total_questions - correct_answers

    score_percentage = (
        (correct_answers / total_questions * 100) if total_questions > 0 else 0
    )

    user_rank = (
        db.session.query(func.count(User.id))
        .filter(User.total_score > user.total_score)
        .scalar()
        + 1
    )
    total_players = User.query.count()

    return render_template(
        "quiz_result.html",
        current_user=user,
        score=user.total_score,
        score_percentage=score_percentage,
        correct_answers=correct_answers,
        incorrect_answers=incorrect_answers,
        total_questions=total_questions,
        rank=user_rank,
        total_players=total_players,
    )


@app.route("/leaderboard")
def leaderboard():
    top_players = User.query.order_by(User.total_score.desc()).limit(10).all()

    current_user_rank = None
    if "user_id" in session:
        current_user = User.query.get(session["user_id"])
        if current_user:
            current_user_rank = (
                db.session.query(func.count(User.id))
                .filter(User.total_score > current_user.total_score)
                .scalar()
                + 1
            )

    return render_template(
        "leaderboard.html", top_players=top_players, current_user_rank=current_user_rank
    )


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("You have been logged out", "info")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
