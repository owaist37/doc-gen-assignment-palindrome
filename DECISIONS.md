# Decisions 
## Introduction
This document covers the major decisions that were made duing the development of the assessment

## Updating output locations
The first major change was ensuring that each run creating it's own folder and output. This will allow us to compare the improvements run to run.

## LLM Judge
The llm judge has been postponed once improvements are made. Having a run to run tracking will allow us to validate the improvements afterwards also. 

## Architecture
Currently there is a single llm flow. We will move to a more agentic flow following the llm judge addition as this will allow us to create a feedback loop where the agent can decide once the appropriate document has been created. 

## Client 01
For client 01 the major change was to ensure that the llm was not making up any values. For this the prompts were updated

## Client 02 prep-process db
The first step for client 02 was to ensure that the database is pre-processed to handle any duplicate accounts ensuring the newest valid record is kept. This was done by first flattening the db to ensure each account_id only appears once. 

## Client 02 update account table
The account table is prepopulated to ensure that it is generated correctly from the db data. The llm prompt is updated to ensure that the table values are updated based on the reports using date metadata but not when using approximate figures. 

## Client 02 update risk statement and capital gains 
For the conclusion the template has been updated to add in the standard risk statement the same way it is for the FCA regulation statement rather than being generated which could cause issues. This also makes it more inline with the template specification. It also updates the capital gains tax template to be more inline with the template. 

## Client 03 update gct warining
The cgt warining was appearing in the recomendations sesction. The prompt was updated to ensure that it was not included. The prompt from the account values section was updated to ensure that the GIA values appear as the way to update values table was still updating with approximate values. The recomendations prompt has also been updated to ensure that all of the avilable funds are used and not double counting any 

## Client 03 inccorect isa valuues
Updating the prompt for the clients isa calculation did not work therfore we are going to precalculate the isa ammounts from the database so it can be used in the prompts. ALong with this the prompts are updated to ensure that the calculation is worked out as expected using the new values.

## Client 04 missing accounts
When running client 04 there were a number of changes that need made the scope prompt in the introduction needed to ensure that it included all of the accounts rather than the examples listed in the text with the recomendations skippin SIPP top up. The prompt was updated to account for all products before going thorugh and making the calculation to ensure that there are no missing values.

## Client 04 incorrect recomendations
For the tax implication the example made the llm only look for matching cases. This was replaced with a more generic prompt. It also required the phrase "the dispoal of" to be moved into the prompt as the sentance structure when including it read awkwardly. 

## Client 04 closed accounts
The meeting notes said not to include any closed accounts. There are two places that this could be updated in the table creation or the LLM prompt in this case the prompt has been updated so the account is not added back in once the LLM updates the values based on the documents.

## Regression test
Some of the fixes for client 4 introduced errors for client 3. The prompts created in section 3 had to ensure that the correct results were still being produced for previous clients. The approach taken was to make prompts more specific and targeted rather than reverting, to avoid re-introducing the original bug.

## Prompt guardrails
Prompts were tightened with explicit exclusion rules to prevent hallucinated figures — excluding contingent amounts, requiring deductions before stating a net total, using ordered calculation steps, and writing `<<insert value here>>` when a value cannot be derived. Where multiple accounts of the same type exist, the model is instructed to match by platform name to identify the specific account ID rather than merging or guessing.

## LLM judge
An LLM judge has been implemented that checks each section of the generated report against the section prompt and global instructions, using the client source files as context. It returns a structured JSON verdict with severity-rated errors (`low / medium / high`). Outputs are a `judge_report.md` per run and a row appended to `run_metrics.csv` for trend tracking. The judge also checks conditional sections for presence/absence mismatches and runs automatically at the end of every generate run.


## Future work 
### Updating Tooling
Rather than focusing on updating the existing funcationality using base python the tooling could be updated to enable more features. This also include using pydantic for allowing checking of types and options within the data. Along with this we could use langraph and langsmith to standerdise the way each indibidual component of the llm is built and how each model call is traced allowing for more evaluation metrics and understanding of the process. 

### Agentic Architecture
Based on our earlier analysis there is a lot of future work that can be carried out. The first one is agentic archietcture we could move to a agent for each of the sections and a supervisor agent that will we pick which agents to use based on the report configurations alternatively a routing and sytnthesisng agent that will split the requirements up and put it into a sinuglar document. This could give us more flexiability and mangement of what we can do. Along with this we could add some of the numerical calculations as tools rather than calculating them beforehand such as creating a tool for adding up account values to ensure it is calculated correctly. 

Along with this the judge can be updated to be included in a feedback loop that will allow for the correcion of the mistakes that are made.


### Update use if condition
Currently the llm decides if a section is needed or not if the use_if is not always currently this is only one section. In the future this may increase to a number of sections. It would be possible to create a facts sheet that as part of full document parsing that returns a structure allowing us to know what should and shouldn't be created each run.

### Remove full document parsing 
Currently each LLM call parses the full document, for the size of our documents chunking would be costly. Another option is to split the pipeline further so that we create a number of documents that is passed. This could mean creating a finalised accouts table that will include information from the text and the tabular data. This will allow us to create tools for each of the calculations. We can then also create a singular document from all of the documents that can be consildated and correct to ensure that there are no conflicing facts. This also means less information and processing needs to be calculated for each section. 


### Agentic Implementation
Currently it is still a number of attached LLM calls with a single feedback loop. This could be transformed into a more agentic solution where it can decide when and if human input is needed and when the task is accurate enough to mark it as complete.
