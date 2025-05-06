"""
main.py
-------
Version 1.0, updated on 2025-05-06

"""

from action import Action


def run_prototype(strategy_nr, action: Action, **kwargs) \
        -> None:
    """
    Runs the methods of the specified sentiment analysis prototype.

    Performs the specified action for English.

    Parameters
    ----------
    strategy_nr : int
        Number of the prompt engineering strategy to use.

    action : Action
        The action to execute.

    kwargs : Any
        Any optional keyword arguments needed for the execution of the
        specified action.

    """

    # Default language for prompt engineering
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


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    """
    Usage
    -----
    Set the correct values for the number of the strategy you wish to use, 
    the action you want to execute and, if so, the prompt group you want to 
    analyze with the PROMPT_GROUP_EVALUATION action.
    
    Execute the run_prototype function for the different sentiment analysis 
    actions one by one, verifying the results after each step and moving 
    created files into special subfolders.
    
    Especially, after sentiment analysis and before executing further actions,
    
    - move the checkpoints created in SentimentAnalysis/data/txt to a 
      special subfolder for the strategy used, and
      
    - move the chunks that have been created in SentimentAnalysis/data/csv 
      to a special subfolder for the strategy used.

    """

    strategy_nr = 4
    action = Action.PROMPT_OPTIMIZATION

    # Insert the prompt numbers here that constitute the prompt group to
    # analyze:
    prompt_group = []

    run_prototype(strategy_nr, action, prompt_group=prompt_group)

