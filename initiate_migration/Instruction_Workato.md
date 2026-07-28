
# The following instructions are for creating analysis and md file for WebMethods package.
1. We want to analyze the files from Webmethods package so that we can create a Workato reciepe using the logic in the package. The folder containing the webmethods package is located under Git repo location <Please ask the name of package>. 
2. Please first analyze it and create a markdown file containing the details of the connectors, mappings, any scripting, triggers and anything else which is part of the package. We want to make sure that all the components of the package are captured with all its logic and connection details so that all those details can be moved into the Workato recipe components. Put analysis files under WebMethods/Analysis directory.
3. Can you also tell me what exactly is the integration/workflow logic in the webmethods package? Explain me the flow from the webmethods packages first so i know if the integration is correct. Put this analysis files under WebMethods/Analysis directory.
4. Create a PackageAnalysis.md file under WebMethods/MD folder containing all the details of the files under Webmethods/Analysis folder. This file will be used as a reference to create the Workato recipe. So this md file should be very extensive making sure it captures all the details needed to create every component of the Workato recipe.
5. Please wait until next request is made.

|--We will be updating or adding prompts based on the analysis. Specific to the package>|

# The following instructions are for creating analysis and md file for creating Workato recipe.
8. We want to create a transformation component in Workato using the excel file located in Workato folder in git. The excel file name is <Ask for the name> The excel file contains source and target column mappings and the transformations needed to create the map. The source profile should be set up as JSON and Target should 	be Database
9. We have an excel file containing the mapping of Webmethods components and flow structure with Workato Components and Flow structure. This has information like Try catch, loop, decision, branching. Please use this mapping to create corresponding components and flow structure in Workato. Please add this to claude.md file as well. Also overwrite any existing Workato recipe with this change. The excel file is located in /WebMethods folder and the file name is <Ask for the name>. If you see any components or structures that is not present the mapping documents please show and create a new excel file with those missing structures or components. If you encounter a Map shape please create an excel file with three columns Source, Transformation and Target. The pipeline in column should have fields from the pipeline in of webmethods map. The  pipeline out column should have fields from the pipeline out columns of webmethods map. The transformation column should be populated with any script or transformation logic that is used to map pipeline in and pipeline out fields.
10. Create Workato.md file which will parse the PackageAnalysis.md file and the csv files <Ask for the name>> and from Workato folder and  from the from WebMethods folder and form the component and logic which can be used to create Workato recipe and its components.
11. Wait for the next instructions.

|<We will be updating or adding prompts based on the analysis. Specific to the package>|

13. Please create Workato recipe using the final Workato.md file as a reference.

# Use following additional instructions for Webmethods Package analysis and creating Workato recipe components.

Workflow: WebMethods to Workato Migration

Step 1 — Analyze the WebMethods Package
Before creating anything in Workato, analyze the provided WebMethods package and produce a Package Analysis Document. Do not proceed to recipe creation until the document has been reviewed and explicitly approved.
The Package Analysis Document must include:

Package Overview — high-level summary of what the integration does, the systems involved, and the data flow
Shapes & Logic Breakdown — every shape identified in the WebMethods package, what it does, and the equivalent Workato construct that will be used to replicate it (step, action, conditional, loop, error handler, etc.)
Connections — all source and target system connections identified, with their equivalent Workato connectors
Operations — each operation invoked (query, insert, update, delete, invoke, etc.) and its Workato equivalent
Data Mappings — field mappings, transformations, and any data manipulation logic identified
Business Rules & Conditions — any branching logic, filters, or decision points and how they will be implemented in the Workato recipe
Error Handling — error handling and retry logic identified in the package and the equivalent approach in Workato
Equivalent Recipe Structure — a detailed outline of how the Workato recipe will be structured, including trigger, steps, and flow, based on the analysis above

WebMethods to Workato Component Mapping Reference
A WebMethods to Workato Component Mapping Excel file has been provided as a reference resource. When analyzing a WebMethods package and identifying equivalent Workato constructs, use this mapping file as a primary reference to ensure accuracy.
Guidelines for using the mapping file:

Consult first — for every WebMethods shape or component identified, look up the mapping file first to find the recommended Workato equivalent
Find the best connector — always identify the most accurate and purpose-built Workato connector available for the system or action being replicated. Do not fall back to generic or default shapes if a more specific connector exists
Not a strict rulebook — the mapping file is a guide, not an absolute constraint. If the mapped equivalent does not accurately replicate the logic of a shape, use your best judgment to find a more suitable Workato construct and flag the deviation in the Package Analysis Document
Flag gaps — if a WebMethods shape has no mapping in the file, or the mapped equivalent is ambiguous, flag it explicitly in the Package Analysis Document under a Mapping Gaps / Deviations section so it can be reviewed before recipe creation begins
Accuracy over convenience — the goal is to replicate the integration logic as closely as possible. Do not default to a mapped equivalent if it does not faithfully reproduce the original behaviour


Step 2 — Await Approval
Once the Package Analysis Document is delivered, wait for explicit approval before proceeding. Do not create any Workato recipe or components until approval is confirmed.

Step 3 — Create the Workato Recipe
Only after approval, proceed to build the Workato recipe based exactly on the approved Package Analysis Document. When building the recipe, follow these rules:

Find the best connector — for every step, identify the most accurate and purpose-built Workato connector available. Do not fall back to generic or default shapes if a more specific connector exists
Complete connections and operations before moving on — for every connector, fully configure the connection and its operation, including all fields, parameters, and logic around it, before moving on to the next. Do not leave a connection or operation partially configured
Use realistic dummy values for auth — if authentication credentials or connection values are not available (API keys, passwords, URLs, client IDs, secrets, etc.), use dummy but realistic-looking placeholder values (e.g. https://api.mycompany.com, client_id_abc123, sk_live_xxxxxxxxxxxx). Do not leave auth fields blank or use placeholder text like YOUR_API_KEY
Stay true to the analysis — do not deviate from the approved Package Analysis Document without flagging it. If something cannot be built as documented, raise it before proceeding

Follow following instructions to create a new Workato recipe using the Webmethods packages
1. WebMethods Packages are located in /WebMethods folder. We will migrate package from WebMethods\GLDFundingEngine20080714 folder
2. Use initiate_migration\Instruction_Workato.md to generate the Webmethods PackageAnalysis.md file.
3. Please create a new WMToWorkato.md file.
4. We want to create prompts which claude can use to create Workato recipe. Use ipaas-migration/webMethods/Analysis/MD/PackageAnalysis.md file to generate these prompts. For now only look at section 5 of PackageAnalysis.md file and the points underneath 5. The prompts should clearly state the connection to be created, app to be used, the actions to be used and details of the setup to be done on that Action.
5. There could be Action where there is a need for field mapping or creating JSON profiles. Please also state it accordingly. Idea is it should provide all the details of Trigger, Actions, Steps, configuration, profiles, connections in form of sequential prompts so that Workato recipe can be built step by step. Record all these prompts in WMToWorkato.md file.
6. Create a new workato recipe using instructions in WMToWorkato.md file. The new Workato recipe name should be FundingEngine. Create it under migrAIte_Training/webMethodsMigration folder. Please use the files under ipaas-migration/Workato/RecipeComponents as a reference to create the workato recipe components.