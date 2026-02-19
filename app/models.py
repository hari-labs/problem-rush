from app import db


class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_code = db.Column(db.String(10), unique=True, nullable=False)  # T01, T02
    team_name = db.Column(db.String(100), nullable=False)              # Display name
    password = db.Column(db.String(200), nullable=False)
    total_score = db.Column(db.Float, default=0)


# ---------------------------
# ROUND 1
# ---------------------------

class Round1Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subround_number = db.Column(db.Integer, nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)
    base_marks = db.Column(db.Float, nullable=False)
    hackerrank_link = db.Column(db.String(300), nullable=False)
    is_active = db.Column(db.Boolean, default=True)


class Round1Attempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('round1_question.id'), nullable=False)
    subround_number = db.Column(db.Integer, nullable=False)
    solved = db.Column(db.Boolean, default=False)
    marks_awarded = db.Column(db.Float, default=0)

    team = db.relationship("Team")
    question = db.relationship("Round1Question")



# ---------------------------
# ROUND 2
# ---------------------------

class Round2Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    base_marks = db.Column(db.Float, nullable=False)
    hackerrank_link = db.Column(db.String(300), nullable=False)
    is_active = db.Column(db.Boolean, default=True)


class Round2Attempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('round2_question.id'), nullable=False)
    solved = db.Column(db.Boolean, default=False)
    character_count = db.Column(db.Integer)
    marks_awarded = db.Column(db.Float, default=0)

    team = db.relationship("Team")
    question = db.relationship("Round2Question")



# ---------------------------
# EVENT STATE CONTROL
# ---------------------------

class EventState(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    current_round = db.Column(db.Integer)
    current_subround = db.Column(db.Integer)
    round1_active = db.Column(db.Boolean, default=False)
    round2_active = db.Column(db.Boolean, default=False)
    leaderboard_visible = db.Column(db.Boolean, default=False)
    last_calculated_subround = db.Column(db.Integer, default=0)
    round2_finalized = db.Column(db.Boolean, default=False)


