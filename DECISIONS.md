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