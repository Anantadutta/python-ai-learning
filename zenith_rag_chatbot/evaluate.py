"""
evaluate.py  -  measures whether the bot works, instead of just "it looked fine".

1. Retrieval hit-rate: for each question, is the chunk containing the answer in the top-K?
2. End-to-end: does the final answer contain the expected fact?
3. Out-of-scope: does the bot REFUSE questions the documents don't cover?

Run:  python evaluate.py              (retrieval only, no LLM key needed)
      python evaluate.py --full       (also calls the LLM)
"""
import sys

from rag import PolicyBot, NOT_FOUND
import unicodedata


def norm(text):
    """Turn special spaces/hyphens (e.g. non-breaking space) into normal ones before comparing."""
    text = unicodedata.normalize("NFKC", text)
    for ch in "\u00a0\u202f\u2009\u2007":
        text = text.replace(ch, " ")
    for ch in "\u2010\u2011\u2012\u2013\u2014":
        text = text.replace(ch, "-")
    return text.lower()

# (question, a string that must appear in the retrieved text / answer)
IN_SCOPE = [
    ("How many casual leaves do I get per year?", "12 days"),
    ("What's the process for claiming travel reimbursement?", "Travel Request"),
    ("How many sick leaves am I entitled to?", "10 days"),
    ("When do I need to submit a medical certificate?", "more than 2 consecutive days"),
    ("How much earned leave can I carry forward?", "45 days"),
    ("How long is maternity leave?", "26 weeks"),
    ("What is the paternity leave entitlement?", "10 working days"),
    ("What is the deadline for submitting expense claims?", "30 days"),
    ("Do I need a receipt for a 300 rupee taxi?", "500"),
    ("How soon are reimbursements paid?", "10 working days"),
    ("What is the per km rate if I use my car?", "12 per km"),
    ("How often do I need to change my password?", "90 days"),
    ("I lost my laptop, what should I do?", "2 hours"),
    ("How long is the probation period?", "six months"),
    ("What time should I arrive on my first day?", "9:30 AM"),
    ("How many days a week must I come to office?", "3 days"),
    ("What is the notice period for a G5 employee?", "60 days"),
    ("What is the referral bonus for a G4 hire?", "50,000"),
    ("Can I accept a gift from a vendor?", "2,000"),
    ("How do I report a phishing email?", "Report Phishing"),
    ("What is the learning allowance?", "25,000"),
    ("When is salary credited?", "last working day"),
    ("How many optional holidays can I take?", "2"),
    ("What is the home office allowance?", "15,000"),
    ("How do I connect to the VPN?", "GlobalConnect"),
    ("What is the hotel limit for a G4 employee in Mumbai?", "7,000"),   # multi-hop question
]
OUT_OF_SCOPE = [
    "What is the capital of Australia?",
    "Write me a poem about the monsoon.",
    "What is Infosys's leave policy?",
    "How do I cook biryani?",
]


def main(full=False):
    bot = PolicyBot()
    hits = 0
    print("=== Retrieval hit-rate (answer present in top-K chunks) ===")
    for q, expected in IN_SCOPE:
        chunks, best = bot.retrieve(q)
        ok = any(expected.lower() in c["text"].lower() for c in chunks)
        hits += ok
        print(f"{'PASS' if ok else 'FAIL'}  sim={best:.2f}  {q}")
    print(f"\nHit-rate: {hits}/{len(IN_SCOPE)} = {hits / len(IN_SCOPE):.0%}\n")

    print("=== Out-of-scope similarity (should be BELOW the gate) ===")
    for q in OUT_OF_SCOPE:
        _, best = bot.retrieve(q)
        print(f"sim={best:.2f}  {q}")
    print("Tip: set MIN_SIMILARITY between the lowest in-scope and highest out-of-scope scores.\n")

    if full:
        print("=== End-to-end answers ===")
        correct = 0
        for q, expected in IN_SCOPE:
            ans = bot.ask(q)["answer"]
            ok = norm(expected) in norm(ans)
            correct += ok
            print(f"{'PASS' if ok else 'FAIL'}  {q}\n      -> {ans[:160]}")
        refused = sum(NOT_FOUND[:40] in bot.ask(q)["answer"] for q in OUT_OF_SCOPE)
        print(f"\nAnswer accuracy: {correct}/{len(IN_SCOPE)}   "
              f"Correct refusals: {refused}/{len(OUT_OF_SCOPE)}")


if __name__ == "__main__":
    main(full="--full" in sys.argv)
