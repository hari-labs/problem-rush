from app import create_app, db
from app.models import Round1Question, Round1Subround, Round2Question


def seed_round1():

    # --- ROUND 1 CONTEST LINKS ---
    round1_links = [
        "https://www.hackerrank.com/1-1771517371",
        "https://www.hackerrank.com/2-1771517413",
        "https://www.hackerrank.com/3-1771517440",
        "https://www.hackerrank.com/round-4-1771551891"
    ]

    subrounds = []

    for i in range(4):
        subrounds.append(
            Round1Subround(
                subround_number=i + 1,
                contest_link=round1_links[i]
            )
        )

    db.session.add_all(subrounds)
    db.session.commit()

    questions = []

    for sub in range(1, 5):

        # 5 Easy
        for _ in range(5):
            questions.append(
                Round1Question(
                    subround_number=sub,
                    difficulty="easy",
                    base_marks=50
                )
            )

        # 3 Medium
        for _ in range(3):
            questions.append(
                Round1Question(
                    subround_number=sub,
                    difficulty="medium",
                    base_marks=75
                )
            )

        # 2 Hard
        for _ in range(2):
            questions.append(
                Round1Question(
                    subround_number=sub,
                    difficulty="hard",
                    base_marks=100
                )
            )

    db.session.add_all(questions)
    db.session.commit()


def seed_round2():

    round2_link = "https://www.hackerrank.com/pattern-contest-psgi-2026"

    questions = []

    for _ in range(5):
        questions.append(
            Round2Question(
                base_marks=100,
                hackerrank_link=round2_link
            )
        )

    db.session.add_all(questions)
    db.session.commit()


if __name__ == "__main__":
    app = create_app()

    with app.app_context():

        if not Round1Subround.query.first():
            seed_round1()

        if not Round2Question.query.first():
            seed_round2()

        print("Seeding completed.")
