from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'supersecret'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///problem_rush.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        from app import models
        db.create_all()

        # Ensure one EventState row exists
        if not models.EventState.query.first():
            default_state = models.EventState(
                current_round=1,
                current_subround=1,
                round1_active=False,
                round2_active=False,
                leaderboard_visible=False
            )
            db.session.add(default_state)
            db.session.commit()


    # Register blueprints
    from app.routes.team import team_bp
    app.register_blueprint(team_bp)

    from app.routes.admin import admin_bp
    app.register_blueprint(admin_bp)


    return app
