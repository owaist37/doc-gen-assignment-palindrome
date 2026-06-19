# Decisions Long
## Document Purpouse
This document contains a full list of all of the decisions made. This will be a superset of the decisions.md and be used for the interview presentation. 

## Current workflow
The current structure calls an a llm that at each stage;
- Parses all of the data
- Understand the requirements of the section it is going to write
- Append each the section to the final document
- Write to a output file

This can be improved in a number of ways;
- overwrite the result each run
- Move towards and agentic workflow
- Move to determinanistic calculations for numerical calculations 
- Use fixed text inserts for text that must be in every section 
- Make use_if more determenistic as it can change between different runs and currently based on an LLM reply which could respond with a different value
- Update prompts to include constraints and more details around what is needed
- Remove full documnent parsing for every llm call
- Add a feedback loop for each of the sections to validate the outputs
- Add a method for evaluating the outputs for each of the runs

## Ability to compare the runs
The first major thing to address is that each run overwrites the previous run. This means we cannot compare the results between each of the runs. Without this we do not know if the changes we have made are improvements on the previous runs. We will do this by creating a baseline folder that will store the results for the first run witwh the baseline setup and a timestamp format for the rest of the runs. 


## Architecture Options
The current structure of the code can be considered a "simple" workflow that each of the steps is executed one after another without any consideration for the previous steps. 