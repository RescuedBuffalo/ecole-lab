from pathlib import Path

from src.app.roles.teacher import Teacher
from src.app.schemas import Draft

CONSTITUTION = Path("src/app/playbook/teaching_constitution.yaml")


def test_teacher_enforces_constitution():
    teacher = Teacher(CONSTITUTION)
    bad = Draft(outline=[], text="This is a post with no goals.")
    res = teacher.review(bad)
    assert res.status != "pass"

    good_text = (
        "Students will learn to remember, understand and apply? "
        "Here is an example that may help you."
    )
    good = Draft(outline=[], text=good_text)
    res2 = teacher.review(good)
    assert res2.status == "pass"
