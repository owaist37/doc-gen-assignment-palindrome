# Forward-Deployed Engineer take-home

## The problem

You need to review the data in the client folder which contains both structured and unstructured data
which is required to generate the report. This output format should follow the template_spec.md sections
and content. fde_notes.md contains notes that a colleague made on the case, note these may be incomplete, 
and you will have to review the data yourself if there are other nuances in the data to discover (e.g. 
conflicting information, data hierarchy, etc.).

The existing pipeline you are given is the bare minimum that runs. It works, but it is naive - and will
need to be improved. A frontier model on its own will not get these reports right. There are intentional 
data quality issues. Getting it right takes good data investigation and problem solving, then building it
into a well-planned agentic system with thorough, structured prompt tuning. You will want to set up an
evaluation pipeline, to ensure that the pipeline is working as expected and to validate your outputs quantitatively. 

Use any tools and AI assistants you like; we want you to work as you normally would. Just ensure you own the
design decisions that you make, and ensure you understand the input data for each client yourself.

## What you are given

```
data/                                four clients, increasing in difficulty
src/
  agent_pipeline/generate.py         reads the config and a client's files, produces a report
  document_formatter/loading.py      reads each source file into text
  document_formatter/formatting.py   turns section content into the final .md (leave as-is)
config/
  template_config.json               the report definition; most of your work goes here
outputs/                             generated reports land here
```

Each client folder holds:

- `meeting_notes.docx`: the adviser's latest conversation with the client.
- `client_data_db.json`: structured account and holdings data from our systems.
- `report_request.docx`: what this report should cover.
- `fde_notes.md`: notes on the data sources and how they fit together. These are a starting point
  from an earlier pass, not a complete list. There may be other things in the data worth handling
  that the notes do not call out. Read the notes, then read the data yourself.
- `template_spec.md`: what each section of the report should contain.

A client folder may also contain other files, and not everything in it is relevant to the report.
Some sources are more relevant than others. Deciding what to feed the model is part of the task: the
starter pipeline naively loads every file in the folder and pushes all of it into every prompt.

## The config

`template_config.json` defines the document. The fields:

- `document_title`: the report title.
- `global_instructions`: instructions applied when generating every section.
- `sections`: an ordered list. Each section has:
  - `id`, `title`: an identifier and the heading shown in the report.
  - `use_if`: when the section is included. Either `"always"`, or a plain-language condition. A
    section whose condition is not met is dropped from the report entirely.
  - `template`: the section's fixed wording, with `<<placeholder>>` slots where generated content
    goes.
  - `placeholders`: one entry per `<<slot>>`, each with a `prompt` telling the model how to produce
    that slot's content from the client's data.

So a section is fixed text (`template`) with generated holes (`placeholders`) and a rule for whether
it appears (`use_if`). For example, the introduction's `template` contains a `<<scope>>` slot, and
the `scope` placeholder's `prompt` says how to fill it. The prompts, the `use_if` rules, the
templates, and how each value is sourced are the main levers you have.

## What to do

We recommend understanding the data clearly before you begin.

1. **Make the reports correct.** Work through the clients, `client_01_clean` to
   `client_04_stretch`. Each report should reflect that client's situation and the adviser's
   instruction. Most of this lives in `template_config.json`: the prompts, the inclusion rules, and
   where each value comes from. Treat the prompts as code: structure them, iterate them, keep them
   readable, and let your commits show that. The clients get harder, and the last one is a deliberate
   stretch; we want to see how you approach it.

2. **Improve the pipeline.** What you are given is the minimum that works, and it can be improved a
   lot. Weigh speed, cost, and effectiveness - it is currently not an agentic system, just llm calls.
   
   *You do not have to build the perfect, production-ready system in the time you have. Be clear about
   what you have done now and what you would take further for production with more time; we care as
   much about that judgement as about the code.*

3. **Write your own evaluation.** We do not give you expected outputs. Decide what correct means for
   these reports, and write something that checks it.

4. **Keep a short decisions log** (`DECISIONS.md`): the hardest calls you made and why, and how you
   would improve the pipeline and the agent setup if you took it further.
  
5. **Code review and presentation.** After you submit, we review your code. Then, in a follow-up
   stage, you walk us through how you approached the problem, the trade-offs you made, and the
   solution you landed on. Present it however you like.

## Do not overfit

The four clients are examples, not the test. We have a held-out set of clients with the same themes
and different specifics, and we will run your pipeline on it. Build for the general case. Prompts
that bake in a particular client's figures, names, or facts will break on the held-out set.

## Extensions (optional)

If you want to show more, these are directions we would actually care about:

- CI, type hints
- Good agentic architecture and agent capabilities.
- Generalising the setup: what happens if a data source changes shape, or a new source is added, and
  the prompts have to follow? How easy is that in your design?
- More than one document type: how would you support several report configs without duplicating
  everything?
- Exploring the idea of prompts as code for prompt tuning and iteration

These are optional. A focused, correct core beats a broad, shaky one.

## Submitting

- Fork this repo and keep your fork public. Work in your fork and commit as you go; we read the
  history, so let it show your thinking rather than one final dump.
- Use whatever AI and coding tools you like.
- Send us your fork URL. It should contain your `config/`, your `src/`, your eval, your
  `DECISIONS.md`, and the generated reports in `outputs/`. We will re-run the generation ourselves from your fork, so
  it needs to run end to end from a clean checkout. 

## How we assess it

We weigh judgement and your problem solving skills over software polish:

- Did the reports get the facts right, including which source to trust when sources disagree?
- Did the right sections appear, and the wrong ones stay out?
- Are the prompts clear, structured, and iterated?
- Is the pipeline's shape sensible on speed, cost, and effectiveness, and did you improve it or set
  out how you would?
- Does it hold up on the held-out set?
- How is the agent setup put together, and how would you take it further?
