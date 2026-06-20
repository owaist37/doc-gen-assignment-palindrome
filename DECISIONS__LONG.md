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

Including the SIPP in the recomendation broke some of the existing calculations. To ensure the correction did not break the calculations further the prompt needed to be updated to include guardrails around exclude contingent/unreceived amounts and requiring deductions before stating the net total.


## Determinisitic Processes
### Client 02
The first thing we need to cover with client 2 is how the the values that go into the reports are generated, the first step is per database to get a single record for each of the accounts that is passed to the llm. This will reduce the token count and the amount of information the llm will have to process. It will also reduce any changes of hulucinations of figures. This process also makes account_id the unique id for the table. 

The next step is to create a pre-populated holidings table rather than letting the llm create it as this will improve accuracy. The prompt can then be updated to include the conflict resolution with the statement_summary file. Alternatively this could be done in the table creation or have a tool created for it or a seperate sub process. 

### Client 03
Updating the prompt for the clients isa calculation did not work therfore we are going to precalculate the isa ammounts from the database so it can be used in the prompts. ALong with this the prompts are updated to ensure that the calculation is worked out as expected using the new values.