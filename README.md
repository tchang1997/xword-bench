# XWordLM

**Can LLMs solve the New York Times crossword?**

LLMs just officially got Gold on the 2025 IMO. But there is still something I can beat them at (I think): the New York Times crossword. Let's change that!

**Why crosswords?**
* It feels like 99% of LLM stuff focuses on math. That's important, but it's not the only verifiable thing in the world.
* RLVR has a huge opportunity to expand beyond getting better at reasoning problems.
* In one sense, crossword-based reasoning is extremely complex:
    - Even solving one clue in isolation can require skills such as fact retrieval, word-play, or self-reference to other parts of the grid
    - Clues must solve intertwined constraints - *i.e.*, LLMs may not have an inherently good sense of constraint violations in a grid of letters
* But there are learnable patterns:
    - Certain types of word-play are common crosswords/many words are statistically more common in crosswords than in natural language (e.g., "OREO")
* And, there's a natural "curriculum:" NYT difficulty scaling increases from Monday -> Saturday (Sunday is a bit weird) **

Oh, most importantly: **ALL THIS IS VERIFIABLE. THERE IS ONE OBJECTIVELY CORRECT ANSWER TO A CROSSWORD, BY CONSTRUCTION.** In spite of my frustration with particularly esoteric clues/bits of pop culture knowledge, the solution is generally curated/designed to be deducible and unambiguous with human intuition (*i.e.*, me, and I used to suck at these) - so we should be able to distill some verifier into this.

There are already a lot of great works that look into solving crosswords with LLMs/LLM-powered agents. Our contribution here isn't to claim SOTA, but to (hopefully) show that the complex constraint-satisifying behavior required to solve crosswords is emergent from RL-based fine-tuning without the need for additional heuristics. 

## Data Processing

I pay for a subscription to the NYT, including the crossword, but I can't go around releasing raw crossword data -- especially not without the permission of all the creators that put in hard work into these, allowing me to trade my research productivity for a little bit of satisfaction. Out of an abundance of caution I've also refrained from producing the data processing code, but it's not too hard to find this information these days. 

However, I do standardize all crosswords puzzles into a single JSON schema, so you can use this as a template. Here's an example with placeholder data + comments:
```
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

Basically, in addition to some metadata about the puzzle, we store:
* The dimensionality of the grid (usually 15x15)
* The exact grid of answers, stored as an array of characters
* Clues, including text and length of the corresponding answer
* Grid numbers, which assist in locating each clue 

## Evaluation pipeline

In general, our evaluation pipeline follows this template for using the crossword JSON:
* **Prompting**: The LLM receives some processed version of the "clues" and "gridnums" keys, and is instructed to fill in clues that it's confident about in some arbitrary manner. 
* **Programatic infilling:** Then, the rules-based system takes over and fills in a grid based on the responses (for now, we focus on a one-turn setup).
* **Reward assignment:** A score for the LLM's attempt is computed based on the number of answers w/ the right length + completely correct answers minus constraint violations, which is computed via the "answers" key.

## Training

The above looks like a verifiable reward, so, hurr durr "you can just do things" RLVR go brrr.

**On reward shaping**
* To design a reward, we want to incentivize correct *full* clues, clues of the right length, and disincentivize clues with the wrong length, or constraint violations.
* First, we apply a strict format reward.
* We'll give +2 to clues of the right length, -2 to the LLM declining to fill in a clue, and 0 for clues of the wrong length (guessing is better than nothing).
* We'll then add +10 for correct answers and +0 for incorrect answers. No reward is given for character similarity because that doesn't really matter for crossword clues -- e.g., my mistakes are usually semantic misunderstandings than a matter of edit distance. 
* An additional -1 is allocated for constraint violations.

**Why RLVR instead of a test-time approach?**
* We already know that, via some combo of inference over clues + loopy belief propagation, we can solve NYT crosswords quite well (well enough to win the ACPT). 
* It's possible to try and replicate that using some tool-calling stuff, and we would probably get comparable results.
* What's more interesting to me is whether we can, via good reward design, simply fine-tune a model to solve these puzzles out of the box, w/o these problem-specific heuristics, in a manner that's (1) competitive in performance w/ past approaches and (2) isn't so sample inefficient as to render learning infeasible.

