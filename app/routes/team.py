from flask import Blueprint, render_template, request, redirect, url_for, session
from werkzeug.security import check_password_hash
from app.models import Team
from app import db
from app.models import EventState
from app.models import Round1Attempt
from app.models import Round1Question
from app.models import Round2Question

team_bp = Blueprint('team', __name__)


@team_bp.route('/')
def home():
    return "Problem Rush is running!"


@team_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        team_code = request.form.get('team_code')
        password = request.form.get('password')

        team = Team.query.filter_by(team_code=team_code).first()

        if team and check_password_hash(team.password, password):
            session['team_id'] = team.id
            return redirect(url_for('team.dashboard'))

        return render_template(
            "team/login.html",
            error="Invalid credentials."
        )

    return render_template("team/login.html")


@team_bp.route('/dashboard')
def dashboard():
    if 'team_id' not in session:
        return redirect(url_for('team.login'))

    state = EventState.query.first()

    round1_button = ""
    round2_button = ""
    leaderboard_button = ""

    if state.round1_active:
        round1_button = '<a href="/round1"><button>Round 1</button></a>'
    else:
        round1_button = '<button disabled>Round 1 (Locked)</button>'

    if state.round2_active:
        round2_button = '<a href="/round2"><button>Round 2</button></a>'
    else:
        round2_button = '<button disabled>Round 2 (Locked)</button>'

    if state.leaderboard_visible:
        leaderboard_button = '<a href="/leaderboard"><button>View Leaderboard</button></a>'

    return render_template(
        "team/dashboard.html",
        round1_button=round1_button,
        round2_button=round2_button,
        leaderboard_button=leaderboard_button
    )


@team_bp.route('/round1')
def round1():
    if 'team_id' not in session:
        return redirect(url_for('team.login'))

    state = EventState.query.first()
    current_sub = state.current_subround

    subrounds = []

    for sub in range(1, 5):
        if sub < current_sub:
            status = "completed"
        elif sub == current_sub:
            status = "active"
        else:
            status = "locked"

        subrounds.append({
            "number": sub,
            "status": status
        })

    return render_template(
        "team/round1.html",
        subrounds=subrounds
    )


@team_bp.route('/round1/subround/<int:sub>')
def subround_page(sub):
    if 'team_id' not in session:
        return redirect(url_for('team.login'))

    state = EventState.query.first()

    if sub != state.current_subround:
        return "This subround is not active."

    existing = Round1Attempt.query.filter_by(
        team_id=session['team_id'],
        subround_number=sub
    ).first()

    if existing:
        question = Round1Question.query.get(existing.question_id)

        return render_template(
            "team/subround.html",
            subround_number=sub,
            already_selected=True,
            selected_question=question
        )

    questions = Round1Question.query.filter_by(
        subround_number=sub,
        is_active=True
    ).all()

    return render_template(
        "team/subround.html",
        subround_number=sub,
        questions=questions,
        already_selected=False
    )

@team_bp.route('/round1/confirm/<int:question_id>')
def confirm_question(question_id):
    if 'team_id' not in session:
        return redirect(url_for('team.login'))

    state = EventState.query.first()

    existing = Round1Attempt.query.filter_by(
        team_id=session['team_id'],
        subround_number=state.current_subround
    ).first()

    if existing:
        return redirect(url_for('team.round1'))

    question = Round1Question.query.get(question_id)

    return render_template(
        "team/confirm.html",
        question=question
    )


@team_bp.route('/round1/lock', methods=['POST'])
def lock_question():
    if 'team_id' not in session:
        return redirect(url_for('team.login'))

    state = EventState.query.first()
    question_id = request.form.get('question_id')

    existing = Round1Attempt.query.filter_by(
        team_id=session['team_id'],
        subround_number=state.current_subround
    ).first()

    if existing:
        return redirect(url_for('team.round1'))

    new_attempt = Round1Attempt(
        team_id=session['team_id'],
        question_id=question_id,
        subround_number=state.current_subround
    )

    db.session.add(new_attempt)
    db.session.commit()

    return redirect(url_for('team.round1'))


@team_bp.route('/leaderboard')
def leaderboard():
    if 'team_id' not in session:
        return redirect(url_for('team.login'))

    state = EventState.query.first()

    if not state.leaderboard_visible:
        return "Leaderboard is not revealed yet."

    teams = Team.query.order_by(Team.total_score.desc()).all()

    return render_template(
        "team/leaderboard.html",
        teams=teams
    )

@team_bp.route('/round2')
def round2():
    if 'team_id' not in session:
        return redirect(url_for('team.login'))

    state = EventState.query.first()

    if not state.round2_active:
        return "Round 2 is not active."

    questions = Round2Question.query.all()

    return render_template(
        "team/round2.html",
        questions=questions
    )




@team_bp.route('/logout')
def logout():
    session.pop('team_id', None)
    return redirect(url_for('team.login'))
