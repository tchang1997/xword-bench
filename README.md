# XWordBench

**Can LLMs solve the New York Times crossword?**

LLMs just officially got Gold on the 2025 IMO. But there is still something I can beat them at (I think): the New York Times crossword. Let's change that!

## Motivation

**Why crosswords?**
It feels like 99% of LLM stuff focuses on math. That's important, but it's not the only verifiable thing in the world.
Crossword-based reasoning is complex:
  - Even solving one clue in isolation can require skills such as fact retrieval, word-play, or self-reference to other parts of the grid
  - Clues must solve intertwined constraints - *i.e.*, LLMs may not have an inherently good sense of constraint violations in a grid of letters

And, there's a natural "curriculum:" for example, New York Times (NYT) crossword difficulty scaling increases from Monday -> Saturday (Sunday is a bit weird). These published crosswords contain expert-curated and edited clues, making NYT crosswords an admittedly U.S./New York centric but high-quality measuring stick for some sort of logical + linguistic reasoning + fact retrieval. 

**Some shoutouts:**
* [CrosswordBench](https://arxiv.org/html/2504.00043v1), approaches this problem from a different angle - they synthetically generate crosswords and pass an *image* of the grid, instead of using expert-curated crosswords as in our benchmark. 
* The [Berkeley Crossword Solver](https://arxiv.org/abs/2205.09665) combines neural QA with loopy belief propagation to algorithmically solve crosswords, instead of the classic "smash it into tokens, throw it into an LLM, and see what happens" (zero-shot). Their system outperformed all human competitors at the 2022 American Crossword Puzzle Tournament. 

## Data Processing

I pay for a subscription to the NYT crossword, but I can't go around releasing raw crossword data w/o permission from the lots of creators put in a lot of hard work into these. If you are a subscriber, you can find your specific cookie from the NYT in browser (under `NYT-S` -- it looks something like `"0^...."`) and use it to access their API using the endpoints specified in the scripts.

All crosswords puzzles follow a standardized JSON schema. Here's an example with placeholder data + comments:
```javascript
{
   puzzle_id: 22291,
   date: 2025-01-01,
   title: "",
   author: Firstname Lastname and Otherperson Constructor,
   size: {
      rows: 15, # standard grid size
      cols: 15
   },
   answers: [
     [
       "O"
       "R"
       "E"
       "O"
       "" # empty string for squares that can't be filled in
       ...
     ] # each inner list has length size.cols (15)
   ], # and there are size.rows such lists (15)
   clues: {
     across: {
       1: { # clue for 1-Across, matching "OREO" from above
         "text": "Black and white sandwich",
         "length": 4
       }, 
       ... # more clues go here 
     }
   },
   gridnums: [
      [
        1,
        2,
        3,
        4,
        ...
      ]
   ] # giant grid in the same shape as "answers" to help locate N-Across/Down clues  
}
```

## Evaluation pipeline

In general, our evaluation pipeline follows this template for using the crossword JSON:
* **Prompting**: The LLM receives some processed version of the "clues" and "gridnums" keys, and is instructed to fill in clues that it's confident about in some arbitrary manner. 
* **Programatic infilling:** Then, the rules-based system takes over and fills in a grid based on the responses (for now, we focus on a one-turn setup).
* **Reward assignment:** We score the LLM's response as per below.

## Results 

### Results on open-weight models

Coming soon!

### Informal results on closed models

Sadly I don't have the $$$ to run full eval here, so here's a mini "copy-paste" eval. **If you have an API key/are willing to contribute credits so I can run a larger, more "official" eval, please reach out.**

I copy-pasted the prompt for the 01/06/2025 puzzle I designed into the chat box in a new chat instance for these models. 

#### Results on Monday-difficulty

This is a Monday crossword, so it's considered the easiest level. As a benchmark, I can generally solve these with 100% accuracy in ~5 min, and I'd consider myself a slightly-above-average solver. o4-high does the same. 

|**Model**|**Clues Solved**|**Length Violations**|**Grid Inconsistencies**|**Time**|
|-|-|-|-|-|
|Gemini 2.5 Flash|51/76|13|6|~0:05|
|Gemini 2.5 Pro|65/76|4|1|~3:00|
|o4-mini |43/76|13|2|0:34|
|o4-mini-high |76/76 |0|0 |5:10| 

#### Results on Saturday-difficulty

Here's a Saturday crossword, so it's considered the hardest level. I can generally solve these with ~90-95% accuracy in ~20 min (the pros do these in sub-5). Saturday is much harder for both humans and LLMs! Seems like the tougher/intentionally ambiguous wordplay makes this more challenging.

|**Model**|**Clues Solved**|**Length Violations**|**Grid Inconsistencies**|**Time**|
|-|-|-|-|-|
|Gemini 2.5 Flash|17/62|31|21|~0:05|
|Gemini 2.5 Pro|18/62|20|16|~5:00|
|o4-mini |failed|-|-|-|
|o4-mini-high |failed |-|- |-| 

*I'd like to think I could solve more than 25% of a Saturday puzzle in 5 min...*

"Failed" means the model refused/declined to solve the puzzle (e.g., acting like it was helping me), or responded with additional questions. We can redesign the prompt and re-run full eval. 

## Training (not implemented fully)

The above looks like a verifiable reward, so, hurr durr "you can just do things" RLVR go brrr.

**But Trenton, you can already solve crosswords algorithmically!**
* Yes, we already know that, via some combo of inference over clues + loopy belief propagation, we can solve NYT crosswords quite well (well enough to win the ACPT). 
* It's possible to try and replicate that, possibly with some tool-calling (*wooooo agentic*) stuff.
* I'm interested on if we can just have the model learn this behavior with good reward design 
* What's more interesting to me is whether we can, via good reward design, simply fine-tune a model to solve these puzzles out of the box, that is - without crossword-specific heuristics — just a good 'ol verifier and a dream. 

Our contribution here isn't to claim SOTA, but to (hopefully) show that the complex constraint-satisifying behavior required to solve crosswords can emerge from RL-based fine-tuning without baking in extra heuristics. 

**On reward shaping**
* To design a reward, we want to incentivize correct *full* clues, clues of the right length, and disincentivize clues with the wrong length, or constraint violations.
* We combine four rewards: format (to parse JSON answers), clue correctness, length correctness, and grid consistency. We normalize these all to a 0-1 scale (see `rewards.py`).

**Training algorithm**
* Like everyone else we use a policy-gradient style method (e.g., GSPO). 
