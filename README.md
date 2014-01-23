# The New Yhat Client


## Lessons from attempt 1
### Questions

- What format must data be in when I make a request to my model?
- Does the answer depend on the protocol (REST, Websocket, Batch)?
- Do I send one observation or multiple observations at a time when calling
 predict?
- Do I need to convert my data into JSON at any point?
- What should my csv or Excel file look like when I want to use batch mode?

### Why does it suck so badly?

- Nobody knows how to start using it
- It's extremely unclear how to use it
- There is no consistent format for input/output
- The error messages don't give helpful feedback
- It's not very fun. Once you use it, nothing really happens. It's still a 2 
player game but (nearly always) only 1 player is present.
- The only reasy to use it is for deployment. This also sort of inherently makes
the assumption that you're formatting your analysis in a manner that plays nice 
with Yhat.
- Deployment can mean a variety of different things to different people. The 
most common are:
    - Real-time API
    - Batch predictions
    - Precomputation/cacheing the data in a DB (`redis`/`MySQL`)
    - Recurring jobs/scripts
    - Automated email/reports

### What would make it easier to use?

- Better documentation; in reality if Austin can't document it, then it's
probably too confusing to use 
- Better docstrings for IPython; we should have the best object/function docs
- Bulletproof, idiotproof examples
- More structured handling of data; (i.e. input will be put into a DataFrame)
- Common format across functions; We'll always use `{"key": [list]}` JSON or
something of that nature.
- Get rid of the classes?
- Better error messages and/or the ability to preview things locally.
- UI wizard for batch (?)

### What would make it more fun to use?

- Remove some of the burden from the user; We need there to be some sort of 
carrot at the end of the road that the user knows they'll get if they activate.
This could be something like a pre-canned model or a fun app they could play 
with.
- make it into a game
- Do more things than just deploying your models
- yeoman style config for project templates
- setup project directory and sample files
- handle nulls / custom null config
- generate plots based on project config
- email and automatic reports
- export project to a server and run it there; config notebook and ec2 and then 
let the user run scripts
- sync directory w/ server
- plugins and example code / yeoman walk-thru for setting up projects
- auto-generate documentation and/or application that can be used
- conda and/or pip support
- component for getting data: SQL, MongoDB, etc.
- displaying results and reports
- testing so you know what's going on w/ Yhat
- ".vimrc" for Yhat
- optimize their code somehow? generate C? something else? yeoman on their own
code?
- automatically horse-race algos and present results
- guide for how to create new plugins, projects, etc.
- live grep on code snippets (?)

## Gameplan

### How can we make it suck less?

### How will we make it easier to use?

### How we will make it more fun?

### NOTES from AO
- create projects based on business purpose / goal; type of problem (e.g. regression vs. classification or ranking); by primary algorithm used
- projects could include an application
- can users create their own template structure
	- can users share their templates with other users in their org or publically
- yhat-cli should show full help

## TODO
- wizard for new project/analysis
- config an existing project and yhat deployment with client
- standardize types of IO
- figure out which types of io work the best
    - DataFrame to DataFrame
    - dictionary
    - both?
- standard way to handle null values -> "execution plan"
- automatically spin up and send your data to aws
    - should include Rstudio/IPython Notebook
    - should print off commands for accessing server and make it super obvious
    how to use it
- yhat aws configuration / manipulation
    - pass it in a license key?


