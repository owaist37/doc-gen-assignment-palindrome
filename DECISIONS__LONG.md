# Decisions Long
## Document Purpouse
This document contains a full list of all of the updates and decisions made. This will be a superset of the decisions.md and be used for the interview presentation. 

## Current workflow
The current structure calls an a llm that at each stage;
- Parses all of the data
- Understand the requirements of the section it is going to write
- Append each the section to the final document
- Write to a output file

This can be improved in a number of ways alongside what is suggested by the FDE;
- overwrite the result each run
- Update prompts to include constraints and more details around what is and is not needed
- Move to determinanistic calculations for numerical calculations
- Make use_if more determenistic as it can change between different runs and currently based on an LLM reply which could respond with a different value
- Remove full documnent parsing for every llm call
- Add a feedback loop for each of the sections to validate the outputs
- Add a method for evaluating the outputs for each of the runs
- Move towards and agentic workflow


## Ability to compare the runs
The first major thing to address is that each run overwrites the previous run. This means we cannot compare the results between each of the runs. Without this we do not know if the changes we have made are improvements on the previous runs. We will do this by creating a baseline folder that will store the results for the first run witwh the baseline setup and a timestamp format for the rest of the runs. 

### LLM Judge 
The next step for this workflow would be to create an llm judge this would take the data that is given to the llm workflow and the template and compare it against the output that was generated. This would then produce a score on how well the current output matches the template specification. We will hold off on this for now to improve the current implementation first. We can take a look back using the runs later on. 

## Architecture Options
The current structure of the code can be considered a "simple" workflow that each of the steps is executed one after another without any consideration for the previous steps. There are number of ways this can be changes to make it more of an agentic system. Typically an agentic system is one that has a feedback loop where the agent itself can decide when a task is done. In our case we do not require a full agentic system as our main goal is to improve the current pipeline. 

With the future structure we could also use the current breakdown of steps to create a supervisor agent that manages subagents for each part of the report or a router agent and then an agent that combines the outputs from each of the individual agents. 

The current files are also small therfore chunking or verctorisation would take more time and cost to implment than be useful.

We could also improve performance using a stronger model.

## Prompt updates
### Client 01
Client 01 focuses on two things the first is that the capital gains tax on any disposal and the platform and adviser fees rates are confirmed before sending out to the recipants. We can see from the Fees & Charges section this is currently included in the output. This is currently done by chaning the prompts for capital gains tax and the fees. The FCA line is already fixed and therefore cannot be re-written. From the updated output we can see that the llm now does not make up the fees. Capital gains tax in this case is not applicable. 

### Client 02
For the conclusion the template has been updated to add in the standard risk statement the same way it is for the FCA regulation statement rather than being generated which could cause issues. This also makes it more inline with the template specification. This also stops the whole of the document being re-repeated for the section. This also updates the conclusion to be more inline with what is expected from the template. The tax satement is update to be more inline with the template and ensure no values are made up or extra repeated contetent is generated. 

### Client 03
We can see that based on our changes that the CGT warning is in the recomendation section, the prompt needs to be updated to remove tax statements from this section. Along with this the GIA value is inconsistent this was updated to ensure that it is correct. Along with this the prompt for the account values needed to be updated to ensure about and similar words aren't used to cause an approximation update. The recomendations prompt has also been updated to ensure that all of the avilable funds are used. 

When making alterations the tax implications and background_objectives sections prompts had to be tightend as they were causing issues to arrise with some of the changes made. This meant ensuing that they were not repating any information from following sections or having context for other sections in the current section.

### Client 04
When running client 04 there were a number of changes that need made the scope prompt in the introduction needed to ensure that it included all of the accounts rather than the examples listed in the text with the recomendations skippin SIPP top up. The prompt was updated to account for all products before going thorugh and making the calculation to ensure that there are no missing values. For the tax implication the example made the llm only look for matching cases. This was replaced with a more generic prompt. It also required the phrase "the dispoal of" to be moved into the prompt as the sentance structure when including it read awkwardly. 

Including the SIPP in the recomendation broke some of the existing calculations. To ensure the correction did not break the calculations further the prompt needed to be updated to include guardrails around exclude contingent/unreceived amounts and requiring deductions before stating the net total. This also meant any calculations had to ensure that no calculations were made with assumed figures if one of the values is currently unkown.

The meeting notes said not to include any closed accounts. There are two places that this could be updated in the table creation or the LLM prompt in this case the prompt has been updated so the account is not added back in once the LLM updates the values based on the documents.


## Determinisitic Processes
### Client 02
The first thing we need to cover with client 2 is how the the values that go into the reports are generated, the first step is per database to get a single record for each of the accounts that is passed to the llm. This will reduce the token count and the amount of information the llm will have to process. It will also reduce any changes of hulucinations of figures. This process also makes account_id the unique id for the table. 

The next step is to create a pre-populated holidings table rather than letting the llm create it as this will improve accuracy. The prompt can then be updated to include the conflict resolution with the statement_summary file. Alternatively this could be done in the table creation or have a tool created for it or a seperate sub process. 

### Client 03
Updating the prompt for the clients isa calculation did not work therfore we are going to precalculate the isa ammounts from the database so it can be used in the prompts. ALong with this the prompts are updated to ensure that the calculation is worked out as expected using the new values.

### Client 04
In some cases there are stale readings that need to be taken into account. In our case there was a flag where there is a large difference between the snapshot date and the meeting date meaning the value could have changed significantly since then. In this case we will flag  those values. 

## LLM Judge 
A basic LLM Judge has been implemented into the project it is a basic error checking judge. For each section/placeholder, global_instructions + the section prompt to over a context of all client source files. This is a basic judge that does not produce any weights. This allows us to track how the models would improve or get worse over time. This LLM judge could be improved by using a stronger model i.e. gpt-4o which would be more capable of spotting errors. Along with this we upgrade the judge to track token usage, latencty and cost.  It can also be extended to test different models and how well they perform. 

## Future work 
### Updating Tooling
Rather than focusing on updating the existing funcationality using base python the tooling could be updated to enable more features. This also include using pydantic for allowing checking of types and options within the data. Along with this we could use langraph and langsmith to standerdise the way each indibidual component of the llm is built and how each model call is traced allowing for more evaluation metrics and understanding of the process. 

### Agentic Architecture
Based on our earlier analysis there is a lot of future work that can be carried out. The first one is agentic archietcture we could move to a agent for each of the sections and a supervisor agent that will we pick which agents to use based on the report configurations alternatively a routing and sytnthesisng agent that will split the requirements up and put it into a sinuglar document. This could give us more flexiability and mangement of what we can do. Along with this we could add some of the numerical calculations as tools rather than calculating them beforehand such as creating a tool for adding up account values to ensure it is calculated correctly. This will also allow for parrelisation. 

Along with this the judge can be updated to be included in a feedback loop that will allow for the correcion of the mistakes that are made.


### Update use if condition
Currently the llm decides if a section is needed or not if the use_if is not always currently this is only one section. In the future this may increase to a number of sections. It would be possible to create a facts sheet that as part of full document parsing that returns a structure allowing us to know what should and shouldn't be created each run.

### Remove full document parsing 
Currently each LLM call parses the full document, for the size of our documents chunking would be costly. Another option is to split the pipeline further so that we create a number of documents that is passed. This could mean creating a finalised accouts table that will include information from the text and the tabular data. This will allow us to create tools for each of the calculations. We can then also create a singular document from all of the documents that can be consildated and correct to ensure that there are no conflicing facts. This also means less information and processing needs to be calculated for each section. 

### Confidence / uncertainty flags
The LLM signal when it is uncertain about an extracted value (e.g. missing or conflicting source data) rather than silently picking one, so advisers know where to double-check


### Agentic Implementation
Currently it is still a number of attached LLM calls with a single feedback loop. This could be transformed into a more agentic solution where it can decide when and if human input is needed and when the task is accurate enough to mark it as complete.

### Examples and UAT
Example reports along with ideal outputs could be created that will allow us to fine tune a model if needed or improve accuracy of the existing model. It will also allow us to set better validation criteria. User Acceptance Testing (UAT) will also ensure that the end users are happy with output and cand provide feedback. 



