from src.app.bandit.thompson import ThompsonBandit, ArmState


def test_bandit_prefers_best_arm():
    bandit = ThompsonBandit({"good": ArmState(), "bad": ArmState()}, exploration=0.0)
    for _ in range(30):
        bandit.update("good", 1.0)
        bandit.update("bad", 0.0)
    wins = sum(bandit.sample() == "good" for _ in range(20))
    assert wins > 15
