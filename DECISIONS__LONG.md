# Decisions Long
## Document Purpose
This document contains a full list of all of the updates and decisions made. This will be a superset of the decisions.md and be used for the interview presentation. 

## Current workflow
The current structure calls an a LLM that at each stage;
- Parses all of the data
- Understand the requirements of the section it is going to write
- Append each the section to the final document
- Write to an output file

This can be improved in a number of ways alongside what is suggested by the FDE;
- Save a result per run of the workflow
- Update prompts to include guardrails and guidelines
- Move to a deterministic solution for calculations
- Make use_if more deterministic as it can change between different runs and currently based on an LLM reply which could respond with a different value
- Remove full document parsing for every LLM call
- Add a feedback loop for each of the sections to validate the outputs
- Add a method for evaluating the outputs for each of the runs
- Move towards and agentic workflow

## Ability to compare the runs
The first major thing to address is that each run overwrites the previous run. This means we cannot compare the results between each of the runs. Without this we do not know if the changes we have made are improvements on the previous runs. We will do this by creating a baseline folder that will store the results for the first run with the baseline setup and a timestamp format for the rest of the runs. This can be further nested based on additional requirements.

### LLM Judge 
Part of being able to compare the results from different runs automatically would be to create an LLM Judge. We could use the judge to then create metrics and corrections required to each report. However, I will hold off on this for now to manually review the document outputs based on the changes we are making. This will help develop understanding of the documents and as each result is stored in its own folder we have the option of running the LLM Judge over previous runs after its implementation.

## Architecture Options
### Re-organising the workflow
The current structure of the code can be considered a "simple" workflow that each of the steps is executed one after another without any consideration for the previous steps. There are a number of ways this can be changed to make it more of an agentic system. Typically an agentic system is one that has a feedback loop where the agent itself can decide when a task is done. Two suitable options would be a routing or supervisor agent where a supervisor or routing agent breaks up the task to several smaller worker agents to carry out the specific tasks before putting it together again. This will be a future goal of the project with the near term goal of improving the workflow to provide more accurate and suitable results. 

### Document Changes
Alongside the agents or LLM calls during the workflow we can change how the documents are processed. Chunking and vectorisation (RAG) for this project would not be efficient as each of the documents are short. Doing so would increase cost and runtime. We can, however, update how each of the documents are read and processed as part of the existing pipeline. Some of this will be addressed in the current set of changes. 

## Prompt updates
### Client 01
Client 01 focuses on two things: the first is that the capital gains tax on any disposal and the platform and adviser fees rates are confirmed before sending out to the recipients. We can see from the Fees & Charges section this is currently included in the output. This is currently done by changing the prompts for capital gains tax and the fees. The FCA line is already fixed and therefore cannot be re-written. From the updated output we can see that the LLM now does not make up the fees. Capital gains tax in this case is not applicable. 

### Client 02
For the conclusion the template has been updated to add in the standard risk statement the same way it is for the FCA regulation statement rather than being generated which could cause issues. This aligns it with how the introduction template works. This also ensures that no information that is not needed is repeated or numbers are made up to form a conclusion. It keeps the expected output inline with the FDE notes and report template.

### Client 03
The CHT warning appears in the recommendations section, the prompt was tightened to ensure that the warnings and any tax information do not appear in the recommendations section. Along with this the recommendations prompt has been updated to ensure that all funds are used. 

The GIA value was appearing inconsistently along with the account values being updated based on approximate amounts making sure that words such as similarly, about and approximately are not used to update any records and to include all accounts. 

When making these alterations the tax implications and background objectives section prompts had to be tightened as they were causing issues to arise. This meant ensuring that they were not repeating any information from previous sections or having the prompt updated to include context given to the other sections.

### Client 04
In the introduction the SIPP was not appearing across the report. All section prompts needed to be updated to include the SIPP topup including all accounts across each section. The calculation prompt also had to be updated to ensure that there were no values missed from the calculations. This however, broke some of the existing calculations. To correct this the prompt needed to be updated to include guardrails around excluding contingent/unreceived amounts and requiring deductions before stating the net total and no calculations were carried out if some of the values were unknown.

For the tax implication the example made the LLM only look for matching cases. This was replaced with a more generic prompt. It also required the phrase "the disposal of" to be moved into the prompt as the sentence structure including it read awkwardly. 

The meeting notes said not to include any closed accounts. There are two places that this could be updated in the table creation or the LLM prompt in this case the prompt has been updated so the account is not added back in once the LLM updates the values based on the documents.

## Deterministic Processes
### Client 02
The first thing we need to cover is how the values that go into the reports are generated. The first step is to get a single record for each account. This means that the LLM will not have to merge any accounts and reduce the amount of tokens being used. It will also reduce the change of the LLM hallucinating any figures. 

The next step is to create a pre-populated holdings table rather than letting the LLM create it as this will improve accuracy. The prompt can then be updated to include the conflict resolution with the statement_summary file. Alternatively this could be done in the table creation or have a tool created for it or a separate sub process. 

### Client 03
Updating the prompt alone for the clients ISA calculation did not work therefore we are going to precalculate the isa amounts from the database so it can be used in the prompts. The prompt was updated to ensure that the calculation is worked out as expected using the new values and any information provided by the documents. A tool could have also been created that would for a given year work out the amount to fund an ISA.

### Client 04
In some cases there are stale readings that need to be taken into account. In our case there was a flag where there is a large difference between the snapshot date and the meeting date meaning the value could have changed significantly since then. In this case we will flag  those values. 


## Calculation guardrails
One common failure was the LLM hallucinating figures, using approximate values or inventing totals. To do this a mixture of pre-calculated values and prompt updates were used. Some of the prompt updates included;
- Exclude contingent/unreceived amounts: Include only funds that have already been received and are immediately available for investment. Exclude earnouts, deferred payments, or not-yet-received amounts.
- Deduct before stating a net total:  deductions are forced to happen before the total is named so the model cannot state a gross figure as net.
- Explicit ordered steps: the recommendation prompt uses a numbered sequence (pool funds → state net total → ISA allocation → remaining products → any new account) to prevent the model reordering or double-counting.
- Using account ids: when two accounts of the same type are present the using account ids forces the LLM to understand which account to use rather than suggesting both. 

## LLM Judge
A basic LLM Judge has been implemented into the project. For each section it combines global instructions and the section's placeholder prompts with the full client source context, then asks the LLM to check the generated content for conformance. This allows us to track how outputs improve or degrade across runs without manually diffing reports. It generates a report that covers the errors that were in the report, how severe they are and how to fix them. Along with this it generates and updates a csv that will be used to compare changes between runs. It also compares the use_if to see if a section should be created and some of our changes to ensure that they are not flagged as an error. 

## Regression Testing
Prompt changes made to fix Client 04 introduced errors in Client 03. Because all clients share the same `template_config.json`, a change to a shared prompt (e.g. the recommendations or holdings-table placeholder) can improve one client while breaking another. Therefore once changes were made the previous clients results were re-run to ensure that their outputs remain correct and to make any fixes on errors that were introduced. Such as improving constraints and prompt scope. 

## Future work 
### Updating Tooling
Rather than focusing on updating the existing functionality using base python the tooling could be updated to enable more features. This also includes using pydantic for allowing checking of types and options within the data. Along with this we could use langraph and langsmith to standardise the way each individual component of the LLM is built and how each model call is traced allowing for more evaluation metrics and understanding of the process. 

### Agentic Architecture
Based on our earlier analysis there is a lot of future work that can be carried out. The first one is agentic architecture. We could move to an agent for each of the sections and a supervisor agent that will pick which agents to use based on the report configurations alternatively a routing and synthesis agent that will split the requirements up and put it into a singular document. This could give us more flexibility and management of what we can do. This would also allow us to generate each section of the report at the same time. Alternatively we can create skills files for each of the different sections for an agent to work on each section based on the skills for it. 

Rather than relying on the LLM to carry out deterministic tasks the numerical calculations can be moved into tools or be pre-calculated. For example creating tools to add up account values, allocate funds. These changes would require significant changes in the pipeline. 

Once the report has been generated the LLM judge can be integrated further into the pipeline to create a feedback loop that will automatically correct any errors or mistakes that are made. This is something that would need to be carefully implemented as it could introduce new hallucinations or errors into the existing report. This could also be extended to include a human in the loop element where if human input is needed the agent can ask for more details.

### Update use if condition
Currently the LLM decides if a section is needed or not if the use_if is not always currently this is only one section. In the future this may increase to a number of sections. It would be possible to create a facts sheet that as part of full document parsing that returns a structure allowing us to know what should and shouldn't be created each run.

### Remove full document parsing 
Currently each LLM call parses the full document, for the size of our documents chunking would be costly. Another option is to split the pipeline further so that we create a number of documents that are passed. This could mean creating a finalised accounts table that will include information from the text and the tabular data. This will allow us to create tools for each of the calculations. We can then also create a singular document from all of the documents that can be consolidated and corrected to ensure that there are no conflicting facts. This also means less information and processing needs to be calculated for each section. 

### Confidence / uncertainty flags
The LLM signal when it is uncertain about an extracted value (e.g. missing or conflicting source data) rather than silently picking one, so advisers know where to double-check

### Examples and UAT
Example reports along with ideal outputs could be created that will allow us to fine tune a model if needed or improve accuracy of the existing model. It will also allow us to set better validation criteria. User Acceptance Testing (UAT) will also ensure that the end users are happy with output and cand provide feedback.