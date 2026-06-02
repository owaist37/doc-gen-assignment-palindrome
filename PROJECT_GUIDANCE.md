# Forward-Deployed Engineer take-home

## The problem

We turn a client's raw source material into a near-final advice document. A human adviser then
reviews it and signs it off. You are given a working pipeline that does this, four clients' worth of
source material, and a config that defines the report. Your job is to make the reports correct, and
to improve the pipeline.

The pipeline you are given is the bare minimum that runs. It works, but it is naive: one model call
per section, every source dumped into every prompt, a single model for everything, and no tools. A
frontier model on its own will not get these reports right. The data has values that disagree
between sources, values that are out of date, gaps, accounts recorded twice, and figures that must
not be filled in automatically. Getting it right takes structured prompts, choosing the right source
for each value, sometimes splitting work across calls or tools, and catching errors before they
reach the client. That is the work.

## What you are given

```
data/                  four clients, increasing in difficulty
pipeline/
  generate.py          reads the config and a client's data, produces a report
  formatter.py         turns section content into the final .md (leave as-is)
config/
  template_config.json the report definition; this is where most of your work goes
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
   lot. Weigh speed, cost, and effectiveness. Some directions:
   - run work in parallel instead of one call after another;
   - fetch specific values with a tool or lookup instead of putting every source in every prompt;
   - use a cheaper or a stronger model per task;
   - resolve a fact once and reuse it instead of re-deriving it per section;
   - add a step that checks or cleans the output before it is final.

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
