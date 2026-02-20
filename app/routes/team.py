from flask import Blueprint, render_template, request, redirect, url_for, session
from werkzeug.security import check_password_hash
from app.models import Team
from app import db
from app.models import EventState
from app.models import Round1Attempt
from app.models import Round1Question
from app.models import Round2Question
from app.models import Round2Attempt
from app.models import Round1Subround

team_bp = Blueprint('team', __name__)


@team_bp.route('/')
def home():
    return "Problem Rush is running!"

@team_bp.app_context_processor
def inject_team():
    if session.get("team_id"):
        team = Team.query.get(session["team_id"])
        return {"current_team": team}
    return {}


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
    if not session.get('team_id'):
        return redirect(url_for('team.login'))

    team = Team.query.get(session['team_id'])
    state = EventState.query.first()

    leaderboard = []

    if state.leaderboard_visible:
        teams = Team.query.order_by(Team.total_score.desc()).all()

        for t in teams:

            # Round 1 total
            r1_total = db.session.query(db.func.sum(Round1Attempt.marks_awarded))\
                .filter_by(team_id=t.id)\
                .scalar() or 0

            # Round 2 total
            r2_total = db.session.query(db.func.sum(Round2Attempt.marks_awarded))\
                .filter_by(team_id=t.id)\
                .scalar() or 0

            leaderboard.append({
                "team_id": t.id,
                "team_name": t.team_name,
                "total_score": t.total_score,
                "round1_score": r1_total,
                "round2_score": r2_total
            })


    return render_template(
        "team/dashboard.html",
        team=team,
        state=state,
        leaderboard=leaderboard
    )



@team_bp.route('/round1')
def round1():
    if 'team_id' not in session:
        return redirect(url_for('team.login'))

    state = EventState.query.first()
    team_id = session['team_id']
    current_sub = state.current_subround

    subrounds = []
    selections = {}

    attempts = Round1Attempt.query.filter_by(team_id=team_id).all()

    for attempt in attempts:
        selections[attempt.subround_number] = attempt.question

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

    subround_links = {}
    subs = Round1Subround.query.all()
    for s in subs:
        subround_links[s.subround_number] = s.contest_link

    return render_template(
        "team/round1.html",
        subrounds=subrounds,
        selections=selections,
        subround_links=subround_links
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

        subround_obj = Round1Subround.query.filter_by(
            subround_number=sub
        ).first()

        return render_template(
            "team/subround.html",
            subround_number=sub,
            already_selected=True,
            selected_question=question,
            contest_link=subround_obj.contest_link
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


@team_bp.route('/event-state')
def event_state():
    state = EventState.query.first()

    return {
        "current_round": state.current_round,
        "current_subround": state.current_subround,
        "round1_active": state.round1_active,
        "round2_active": state.round2_active,
        "leaderboard_visible": state.leaderboard_visible
    }



@team_bp.route('/logout')
def logout():
    session.pop('team_id', None)
    return redirect(url_for('team.login'))
