"""LoanWise AI - prediction.

Runs one applicant through all five trained models and applies the
voting rule from the spec:
  5 approval votes   -> APPROVED
  5 rejection votes  -> REJECTED
  anything mixed     -> FURTHER REVIEW
No prediction is ever made without trained models - the routes check
for an active trained dataset first and block otherwise.
"""
from ml.preprocessing import applicant_to_features


def final_decision(approval_votes):
    if approval_votes == 5:
        return "APPROVED"
    if approval_votes == 0:
        return "REJECTED"
    return "FURTHER REVIEW"


def predict_all(models, applicant):
    """models: {name: pipeline} in display order. Returns per-model votes.

    Returns {"votes": {name: 1/0}, "approval_votes": n,
             "rejection_votes": 5-n, "final_decision": str}
    """
    X = applicant_to_features(applicant)
    votes = {}
    for name, pipe in models.items():
        votes[name] = int(pipe.predict(X)[0])
    approval = sum(votes.values())
    return {
        "votes": votes,
        "approval_votes": approval,
        "rejection_votes": 5 - approval,
        "final_decision": final_decision(approval),
    }
