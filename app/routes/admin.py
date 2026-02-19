from flask import Blueprint, request, render_template, session, redirect, url_for
import random
import string
from werkzeug.security import generate_password_hash
from app.models import Team
from app import db
from app.models import EventState
from app.models import Round1Attempt, Round1Question
from app.models import Round2Question, Round2Attempt


admin_bp = Blueprint('admin', __name__, url_prefix='/control-room')


# Hardcoded admin credentials (for now)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "problemrush123"


@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == "admin" and password == "problemrush123":
            session['admin'] = True
            return redirect(url_for('admin.dashboard'))

        return render_template(
            "admin/login.html",
            error="Invalid credentials."
        )

    return render_template("admin/login.html")


@admin_bp.route('/dashboard')
def dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin.login'))

    state = EventState.query.first()
    teams = Team.query.all()

    round2_attempt_count = Round2Attempt.query.count()
    round2_question_count = Round2Question.query.count()
    team_count = Team.query.count()

    expected_attempts = team_count * round2_question_count

    return render_template(
        "admin/dashboard.html",
        state=state,
        teams=teams,
        round2_attempt_count=round2_attempt_count,
        expected_attempts=expected_attempts
    )



@admin_bp.route('/start-round1')
def start_round1():
    if not session.get('admin'):
        return redirect(url_for('admin.login'))

    state = EventState.query.first()
    state.round1_active = True
    state.round2_active = False
    state.current_round = 1
    state.current_subround = 1

    db.session.commit()

    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/set-subround/<int:sub>')
def set_subround(sub):
    if not session.get('admin'):
        return redirect(url_for('admin.login'))

    state = EventState.query.first()  # <-- MOVE THIS UP

    if sub < 1 or sub > 4:
        return "Invalid subround."

    if sub > state.last_calculated_subround + 1:
        return render_template(
            "admin/subround_warning.html",
            expected_next=state.last_calculated_subround + 1,
            requested_sub=sub
        )


    state.current_subround = sub
    db.session.commit()

    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/force-set-subround/<int:sub>')
def force_set_subround(sub):
    if not session.get('admin'):
        return redirect(url_for('admin.login'))

    state = EventState.query.first()
    state.current_subround = sub
    db.session.commit()

    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/end-round1')
def end_round1():
    if not session.get('admin'):
        return redirect(url_for('admin.login'))

    state = EventState.query.first()
    state.round1_active = False

    db.session.commit()

    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/calculate-subround')
def calculate_subround():
    if not session.get('admin'):
        return redirect(url_for('admin.login'))

    state = EventState.query.first()
    current_sub = state.current_subround

    # Get all questions in this subround
    questions = Round1Question.query.filter_by(subround_number=current_sub).all()

    for question in questions:

        # Get solved attempts for this question
        solved_attempts = Round1Attempt.query.filter_by(
            question_id=question.id,
            subround_number=current_sub,
            solved=True
        ).all()

        solver_count = len(solved_attempts)

        if solver_count > 0:
            split_marks = question.base_marks / solver_count

            for attempt in solved_attempts:
                # Avoid double calculation
                if attempt.marks_awarded == 0:
                    attempt.marks_awarded = split_marks

                    team = Team.query.get(attempt.team_id)
                    team.total_score += split_marks

    state.last_calculated_subround = current_sub

    db.session.commit()

    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/manage-attempts', methods=['GET', 'POST'])
def manage_attempts():
    if not session.get('admin'):
        return redirect(url_for('admin.login'))

    state = EventState.query.first()
    current_sub = state.current_subround

    attempts = Round1Attempt.query.filter_by(
        subround_number=current_sub
    ).all()

    if request.method == 'POST':

        for attempt in attempts:
            attempt.solved = False

        solved_ids = request.form.getlist('solved_attempts')

        for attempt in attempts:
            if str(attempt.id) in solved_ids:
                attempt.solved = True

        db.session.commit()

        return redirect(url_for('admin.manage_attempts'))

    return render_template(
        "admin/manage_round1.html",
        attempts=attempts,
        current_sub=current_sub
    )


@admin_bp.route('/create-team', methods=['GET', 'POST'])
def create_team():
    if not session.get('admin'):
        return redirect(url_for('admin.login'))

    if request.method == 'POST':
        team_code = request.form.get('team_code')
        team_name = request.form.get('team_name')

        raw_password = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        hashed_password = generate_password_hash(raw_password)

        new_team = Team(
            team_code=team_code,
            team_name=team_name,
            password=hashed_password
        )

        db.session.add(new_team)
        db.session.commit()

        return render_template(
            "admin/create_team.html",
            generated=True,
            team_code=team_code,
            raw_password=raw_password
        )

    return render_template("admin/create_team.html", generated=False)


@admin_bp.route('/reset-password/<int:team_id>')
def reset_password(team_id):
    if not session.get('admin'):
        return redirect(url_for('admin.login'))

    team = Team.query.get(team_id)

    if not team:
        return "Team not found"

    new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    team.password = generate_password_hash(new_password)

    db.session.commit()

    return render_template(
        "admin/reset_password.html",
        team_code=team.team_code,
        new_password=new_password
    )


@admin_bp.route('/show-leaderboard')
def show_leaderboard():
    if not session.get('admin'):
        return redirect(url_for('admin.login'))

    state = EventState.query.first()
    state.leaderboard_visible = True
    db.session.commit()

    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/hide-leaderboard')
def hide_leaderboard():
    if not session.get('admin'):
        return redirect(url_for('admin.login'))

    state = EventState.query.first()
    state.leaderboard_visible = False
    db.session.commit()

    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/start-round2')
def start_round2():
    if not session.get('admin'):
        return redirect(url_for('admin.login'))
    
    if not teams or not questions:
        return "Cannot start Round 2. Teams or Questions missing."

    state = EventState.query.first()

    # Activate Round 2
    state.round1_active = False
    state.round2_active = True
    state.current_round = 2

    db.session.commit()

    # Auto-generate Round2Attempt entries
    teams = Team.query.all()
    questions = Round2Question.query.all()

    for team in teams:
        for question in questions:
            existing = Round2Attempt.query.filter_by(
                team_id=team.id,
                question_id=question.id
            ).first()

            if not existing:
                attempt = Round2Attempt(
                    team_id=team.id,
                    question_id=question.id
                )
                db.session.add(attempt)

    db.session.commit()

    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/manage-round2', methods=['GET', 'POST'])
def manage_round2():
    if not session.get('admin'):
        return redirect(url_for('admin.login'))

    state = EventState.query.first()

    attempts = Round2Attempt.query.all()

    if state.round2_finalized:
        return render_template(
            "admin/manage_round2.html",
            attempts=attempts,
            state=state
        )

    if request.method == 'POST':

        for attempt in attempts:
            solved_key = f"solved_{attempt.id}"
            char_key = f"char_{attempt.id}"

            attempt.solved = solved_key in request.form

            char_value = request.form.get(char_key)
            attempt.character_count = int(char_value) if char_value else None

        db.session.commit()

        return redirect(url_for('admin.manage_round2'))

    return render_template(
        "admin/manage_round2.html",
        attempts=attempts,
        state=state
    )


@admin_bp.route('/calculate-round2')
def calculate_round2():
    if not session.get('admin'):
        return redirect(url_for('admin.login'))

    state = EventState.query.first()

    if state.round2_finalized:
        return "Round 2 already finalized."

    questions = Round2Question.query.all()

    mark_scale = {
        1: 100,
        2: 90,
        3: 80,
        4: 70,
        5: 60
    }

    for question in questions:

        attempts = Round2Attempt.query.filter_by(
            question_id=question.id,
            solved=True
        ).filter(Round2Attempt.character_count != None).all()

        attempts.sort(key=lambda x: x.character_count)

        current_rank = 0
        previous_char = None
        position = 0

        for attempt in attempts:
            position += 1

            if attempt.character_count != previous_char:
                current_rank = position

            previous_char = attempt.character_count

            marks = mark_scale.get(current_rank, 0)

            attempt.marks_awarded = marks

            team = Team.query.get(attempt.team_id)
            team.total_score += marks

    state.round2_finalized = True

    db.session.commit()

    return redirect(url_for('admin.dashboard'))



@admin_bp.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('admin.login'))
