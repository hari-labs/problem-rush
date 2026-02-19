from app import create_app, db
from app.models import Round1Question, Round2Question


def seed_round1():
    questions = []

    # 4 subrounds
    for sub in range(1, 5):

        # 5 Easy
        for i in range(1, 6):
            questions.append(
                Round1Question(
                    subround_number=sub,
                    difficulty="easy",
                    base_marks=50,
                    hackerrank_link=f"https://dummy-link.com/round1/sub{sub}/easy{i}"
                )
            )

        # 3 Medium
        for i in range(1, 4):
            questions.append(
                Round1Question(
                    subround_number=sub,
                    difficulty="medium",
                    base_marks=75,
                    hackerrank_link=f"https://dummy-link.com/round1/sub{sub}/medium{i}"
                )
            )

        # 2 Hard
        for i in range(1, 3):
            questions.append(
                Round1Question(
                    subround_number=sub,
                    difficulty="hard",
                    base_marks=100,
                    hackerrank_link=f"https://dummy-link.com/round1/sub{sub}/hard{i}"
                )
            )

    db.session.add_all(questions)
    db.session.commit()


def seed_round2():
    questions = []

    for i in range(1, 6):
        questions.append(
            Round2Question(
                base_marks=100,
                hackerrank_link=f"https://dummy-link.com/round2/q{i}"
            )
        )

    db.session.add_all(questions)
    db.session.commit()


if __name__ == "__main__":
    app = create_app()

    with app.app_context():

        # Only seed if empty
        if not Round1Question.query.first():
            seed_round1()

        if not Round2Question.query.first():
            seed_round2()

        print("Seeding completed.")
