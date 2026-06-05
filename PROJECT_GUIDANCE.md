# Forward-Deployed Engineer take-home

## The problem

You need to review the data in the client folder which contains both structured and unstructured data
which is required to generate the report. This output format should follow the template_spec.md sections
and content. fde_notes.md contains notes that a colleague made on the case, note these may be incomplete, 
and you will have to review the data yourself if there are other nuances in the data to discover (e.g. 
conflicting information, data hierarchy, etc.).

The existing pipeline you are given is the bare minimum that runs. It works, but it is naive - and will
need to be improved. A frontier model on its own will not get these reports right. There are intentional 
data quality issues, getting it right takes good data investigation and problem solving, then making it into 
a well planned agentic system and having thorough, structured prompt tuning. You will want to set up an
evaluation pipeline, to ensure that the pipeline is working as expected and to validate your outputs quantiatively. 

## What you are given

```
data/                  four clients, increasing in difficulty
pipeline/
  generate.py          reads the config and a client's data, produces a report
  formatter.py         turns section content into the final .md (leave as-is)
config/
  template_config.json the report definition; >> most of your work goes
outputs/               generated reports land here
```

Each client folder holds:

- `meeting_notes.docx`: the adviser's latest conversation with the client.
- `client_data_db.json`: structured account and holdings data from our systems.
- `report_request.docx`: what this report should cover.
- `fde_notes.md`: notes on the data sources and how they fit together. These are a starting point
  from an earlier pass, not a complete list. There may be other things in the data worth handling
  that the notes do not call out. Read the notes, then read the data yourself.
- `template_spec.md`: what each section of the report should contain.

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

1. **Make the reports correct.** Work through the clients, `client_01_clean` to
   `client_04_stretch`. Each report should reflect that client's situation and the adviser's
   instruction. Most of this lives in `template_config.json`: the prompts, the inclusion rules, and
   where each value comes from. Treat the prompts as code: structure them, iterate them, keep them
   readable, and let your commits show that. The clients get harder, and the last one is a deliberate
   stretch; we want to see how you approach it.

2. **Improve the pipeline.** What you are given is the minimum that works, and it can be improved a
   lot. Weigh speed, cost, and effectiveness - it is currently not an agentic system, just llm calls.

   Use whatever models and structure you think are right, and say why.

3. **Write your own evaluation.** We do not give you expected outputs. Decide what correct means for
   these reports, and write something that checks it.

4. **Keep a short decisions log** (`DECISIONS.md`): the hardest calls you made and why, and how you
   would improve the pipeline and the agent setup if you took it further.

## Do not overfit

The four clients are examples, not the test. We have a held-out set of clients with the same themes
and different specifics, and we will run your pipeline on it. Build for the general case. Prompts
that bake in a particular client's figures, names, or facts will break on the held-out set, and we
will see it.

## Extensions (optional)

If you want to show more, these are directions we would actually care about:

- CI, for example a GitHub Actions workflow that runs your eval.
- Generalising the setup: what happens if a data source changes shape, or a new source is added, and
  the prompts have to follow? How easy is that in your design?
- More than one document type: how would you support several report configs without duplicating
  everything?
- Dockerising, batching across clients, caching repeated calls.

These are optional. A focused, correct core beats a broad, shaky one.

## Submitting

- Fork this repo and keep your fork public. Work in your fork and commit as you go; we read the
  history, so let it show your thinking rather than one final dump.
- Use whatever AI and coding tools you like.
- Send us your fork URL. It should contain your `config/`, your `pipeline/`, your eval, your
  `DECISIONS.md`, and the generated reports in `outputs/`.

## How we assess it

We weigh judgement over software polish:

- Did the reports get the facts right, including which source to trust when sources disagree?
- Did the right sections appear, and the wrong ones stay out?
- Are the prompts clear, structured, and iterated?
- Is the pipeline's shape sensible on speed, cost, and effectiveness, and did you improve it or set
  out how you would?
- Does it hold up on the held-out set?
- How is the agent setup put together, and how would you take it further?

Clean code matters, but it is not the headline. Questions are welcome; ask us anything.

## What happens next

We read through your code, config, and decisions. Then, in the interview, we'll ask you to walk us
through it: how you approached the problem, where the hard parts were, how you got round them, and
what you settled on. Present it however you like: slides, a short write-up, a demo, or just talking
over the code. Keep enough notes as you go that you can tell that story.
