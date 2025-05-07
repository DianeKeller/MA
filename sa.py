"""
sa.py
-------
Version 1.0, updated on 2025-05-07

Usage
-----
Run this script via command line:

    python -m sa s=<strategy_nr> a=<action_nr> [p=<prompt_group>]

Arguments:
----------
s : int
    Number of the prompt engineering strategy to use (between 1 and 4, e.g. 4)

a : int
    Action number according to the following mapping:

        1 = PROMPT_ENGINEERING
        2 = SENTIMENT_ANALYSIS
        3 = EVALUATION
        4 = PROMPT_GROUP_EVALUATION
        5 = PROMPT_OPTIMIZATION

p : comma-separated prompt numbers (ints) (optional).
    Prompt group to analyze. Only required if action is 4
    (PROMPT_GROUP_EVALUATION).

Action Mapping:
---------------
1 = PROMPT_ENGINEERING
2 = SENTIMENT_ANALYSIS
3 = EVALUATION
4 = PROMPT_GROUP_EVALUATION
5 = PROMPT_OPTIMIZATION

Examples:
---------
    python -m sa s=4 a=5
    python -m sa s=3 a=4 p=1,2,3

"""

import sys

from action import Action
from src.sentiment_analysis.serverless_bloom_workflow import \
    ServerlessBloomWorkflow

wf = ServerlessBloomWorkflow()


def run_prototype(strategy_nr: int, action: Action, **kwargs) -> None:
    language = 'en'
    prompt_group = kwargs.get("prompt_group", [])

    match action:
        case Action.PROMPT_ENGINEERING:
            wf.run_prompt_engineering(strategy_nr)
        case Action.SENTIMENT_ANALYSIS:
            wf.run_sentiment_analysis(strategy_nr, language)
        case Action.EVALUATION:
            wf.run_evaluation(strategy_nr, language)
        case Action.PROMPT_GROUP_EVALUATION:
            wf.run_prompt_group_evaluation(strategy_nr, prompt_group, language)
        case Action.PROMPT_OPTIMIZATION:
            wf.run_prompt_optimization(strategy_nr, language)
        case _:
            print(f"Unknown action: {action}")
            sys.exit(1)


def parse_args(argv):
    args = {}
    for arg in argv[1:]:
        if '=' not in arg:
            print(
                f"❌ Invalid argument: '{arg}'. "
                f"Usage: s=..., a=..., p=..."
            )

            print(__doc__)
            sys.exit(1)

        key, value = arg.split('=', 1)
        args[key.strip()] = value.strip()
    return args


def main(argv):
    args = parse_args(argv)

    if 's' not in args or 'a' not in args:
        print("❌ Missing arguments: Please provide arguments 's' (strategy) "
              "and 'a' (action).")
        print(__doc__)
        sys.exit(1)

    try:
        strategy_nr = int(args['s'])
    except ValueError:
        print("❌ Error: 's' must be an integer between 1 and .")
        sys.exit(1)

    try:
        action = Action(int(args['a']))
    except (ValueError, KeyError):
        print("❌ Error: 'a' must specify an action (1–5).")
        print(__doc__)
        sys.exit(1)

    prompt_group = []
    if action == Action.PROMPT_GROUP_EVALUATION:
        if 'p' not in args:
            print(
                "❌ Error: You need to specify a prompt group for Action 4 "
                "(PROMPT_GROUP_EVALUATION)."
            )
            sys.exit(1)
        try:
            prompt_group = [int(x) for x in args['p'].split(',') if x.strip()]
        except ValueError:
            print(
                "❌ Error: 'p' must be a comma-separated list of integers ("
                "e.g. 1,2,3)."
            )
            sys.exit(1)

    run_prototype(strategy_nr, action, prompt_group=prompt_group)


if __name__ == '__main__':
    main(sys.argv)
