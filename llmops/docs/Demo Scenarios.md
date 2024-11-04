# Demo

1. Clone the repository to your local machine.
    git clone ...

2. Navigate to the `aidemos/llmops` directory.

3. Run the following command to install the dependencies.
    pip install -r requirements.txt

## Chat Session

1. Start the local application server, in commad line run:
    **pf flow serve --source ./ --port 8080 --host localhost**
    Make sure you are in the `aidemos/llmops` directory.

2. The chat UI will be opened automatically in your default browser. If not, you can manually open the browser and navigate to `http://localhost:8080`. 
    
3. Start the chat. Ask some questions about the Microsoft Fabric or Azure AI Studio. Select some session id and use it during the coneversation.
Examples for the chat session are:
    - What is Fabric Data Pipeline?  
        Session ID 1      
    - What're the data source it support? 
        Session ID 1
    - Does it support Cosmos DB as a data source?
        Session ID 1
    - List the main data sources it does support.
        Session ID 1

4. Check the trace
   From command line run
    **pf service status** 
    Notice the prompt flow port number and open the browser and navigate to `http://localhost:<port_number>`. 
    Select the first trace m click on it. 
    Select the "Show Gantt" button in the upper right corner.

5. Explore the traces


## Evaluation
TODO
