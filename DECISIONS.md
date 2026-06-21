# Decisions 
## Introduction
This document covers the major decisions that were made during the development of the assessment

## Updating output locations
The first major change was ensuring that each run created its own folder and output. This will allow us to compare the improvements run to run.

## LLM Judge
The LLM judge has been postponed once improvements are made. Having a run to run tracking will allow us to validate the improvements afterwards also. 

## Architecture
Currently there is a single LLM flow. We will move to a more agentic flow following the LLM judge addition as this will allow us to create a feedback loop where the agent can decide once the appropriate document has been created. 

## Client 01
For client 01 the major change was to ensure that the LLM was not making up any values. For this the prompts were updated to include <<insert value here>> if the value is not known. 

## Client 02 prep-process db
The first step for client 02 was to ensure that the database is pre-processed to handle any duplicate accounts ensuring the newest valid record is kept. This was done by first flattening the db to ensure each account_id only appears once. 

## Client 02 update account table
The account table is prepopulated to ensure that it is generated correctly from the db data. The LLM prompt is updated to ensure that the table values are updated based on the reports using date metadata but not when using approximate figures. 

## Client 02 update risk statement and capital gains 
For the conclusion the template has been updated to add in the standard risk statement the same way it is for the FCA regulation statement rather than being generated which could cause issues. This also makes it more inline with the template specification, The capital gains tax template was updated to be more inline with the template. 

## Client 03 update CGT warning
The CGT warning was appearing in the recommendations section, the prompt was updated to ensure that it was not included. The prompt from the account values section was updated to ensure that the GIA values appear as the account values table was still updating with approximate values. The recommendations prompt has been updated to ensure that all of the available funds are used and not double counting any values.

## Client 03 incorrect ISA values
Updating the prompt for the clients ISA calculation did not work therefore we are going to precalculate the isa amounts from the database so it can be used in the prompts. Along with this the prompts are updated to ensure that the calculation is worked out as expected using the new values.

## Client 04 missing accounts
The scope prompt in the introduction needed to ensure that it included all of the accounts rather than the examples listed in the text with the recommendations skipping SIPP top up. The prompt for recommendations was updated to account for all products before going through and making the calculation to ensure that there are no missing values.

## Client 04 incorrect recommendations
For the tax implication the example made the LLM only look for matching cases. This was replaced with a more generic prompt. It also required the phrase "the disposal of" to be moved into the prompt as the sentence structure when including it read awkwardly. 

## Client 04 closed accounts
The meeting notes said not to include any closed accounts. There are two places that this could be updated in the table creation or the LLM prompt in this case the prompt has been updated so the account is not added back in once the LLM updates the values based on the documents.

## Client 04 account confusion. 
Where multiple accounts of the same type exist, the model is instructed to match by platform name to identify the specific account ID rather than merging or guessing.

## Regression tests
Some of the fixes for client 4 introduced errors for client 3. The prompts were made more specific and targeted along with adding additional guardrails. This was then tested on all clients to ensure no new errors were introduced. 

## LLM judge
An LLM judge has been implemented that checks each section of the generated report against the section prompt and global instructions, using the client source files as context. Outputs are a `judge_report.md` per run and a row appended to `run_metrics.csv` for trend tracking. The judge also checks conditional sections for presence/absence mismatches and runs automatically at the end of every generated run.


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