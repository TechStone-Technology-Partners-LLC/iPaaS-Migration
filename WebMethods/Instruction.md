
# The following instructiona are for creating analysis and md file for WebMethogs package.
1. We want to analyze the files from Webmethods package so that we can create a Boomi process using the logic in the package. The folder containing the webmethods package is located under Git repo location <Please ask the name of package>. 
2. Please first analyze it and create a markdown file containing the details of the connectors, mappings, any scripting, triggers and anything else which is part of the package. We want to make sure that all the components of the package are captured with all its logic and connection details so that all those details can be moved into the Boomi process components. Put analysis files under WebMethods/Analysis directory.
3. Can you also tell me what exactly is the integration/workflow logic in the webmethods package? Explain me the flow from the webmethods packages first so i know if the integration is correct. Put this analysis files under WebMethods/Analysis directory.
4. Create a PackageAnalysis.md file under WebMethods/MD folder containing all the details of the files under Webmethods/Analysis folder. This file will be used as a reference to create the Boomi integration process. So this md file should be very extensive making sure it captures all the details needed to create every component of the Boomi process.
5. Please wait until next request is made.

|--We will be updating or adding prompts based on the analysis. Specific to the package>|

# The following instructiona are for creating analysis and md file for creating Boomi process.
8. We want to create a Map component in Boomi I using the excel file located in Boomi folder in git. The excel file name is <Ask for the name> The excel file contains source and target column mappings and the transformations needed to create the map. The source profile should be set up as JSON and Target should 	be Database
9. We have an excel file containing the mapping of Webmethods components and flow structure with Boomi Components and Flow structure. This has information like Try catch, loop, decision, branching. Please use this mapping to create corresponding components and flow structure in Boomi. Please add this to claude.md file as well. Also overwrite any existing Boomi process with this change. The excel file is located in /WebMethods folder and the file name is <Ask for the name>. If you see any components or structures that is not present the mapping documents please show and create a new excel file with those missing structures or components. If you encounter a Map shape please create an excel file with three columns Source, Transformation and Target. The pipeline in column should have fields from the pipeline in of webmethods map. The  pipeline out column should have fields from the pipeline out columns of webmethods map. The transformation column should be populated with any script or transformation logic that is used to map pipeline in and pipeline out fields.
10. Create Boomi.md file which will parse the PacakageAnalysis.md file and the csv files <Ask for the name>> and from Boomi folder and  from the from WebMethods folder and form the component and logic which can be used to create Boomi process and its components.
11. Wait for the next instructions.

|<We will be updating or adding prompts based on the analysis. Specific to the package>|

13. Please create Boomi process using the final Boomi.md file as a reference.