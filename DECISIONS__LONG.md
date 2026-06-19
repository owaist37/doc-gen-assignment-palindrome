# Decisions Long
## Document Purpouse
This document contains a full list of all of the decisions made. This will be a superset of the decisions.md and be used for the interview presentation. 

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

## Prompt updates
### Client 01
Client 01 focuses on two things the first is that the capital gains tax on any disposal and the platform and adviser fees rates are confirmed before sending out to the recipants. We can see from the Fees & Charges section this is currently included in the output. This is currently done by chaning the prompts for capital gains tax and the fees. The FCA line is already fixed and therefore cannot be re-written. From the updated output we can see that the llm now does not make up the fees. Capital gains tax in this case is not applicable. 

### Client 02
For the conclusion the template has been updated to add in the standard risk statement the same way it is for the FCA regulation statement rather than being generated which could cause issues. This also makes it more inline with the template specification. This also stops the whole of the document being re-repeated for the section.


## Determinisitic Processes
### Client 02
The first thing we need to cover with client 2 is how the the values that go into the reports are generated, the first step is per database to get a single record for each of the accounts that is passed to the llm. This will reduce the token count and the amount of information the llm will have to process. It will also reduce any changes of hulucinations of figures. 

The next step is to create a pre-populated holidings table rather than letting the llm create it as this will improve accuracy. The prompt can then be updated to include the conflict resolution with the statement_summary file. Alternatively this could be done in the table creation or have a tool created for it. 