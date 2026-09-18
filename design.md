# Design
## Introduction
Having limited experience with designing larger scale programs with the complexity of this project, designing the structuring of this systems design really challenged me.
This document has been written to explain the design decisions, and the resulting compromises made throughout. With the aim to describe not only the design itself, but the thought process behind it. Including earlier decisions that had to be reevaluated, due to my increased understanding of all the systems related.
## Architectural overview
The layered architecture discussed throughout this document was a key design decision made early within the project, and will be covered extensively. Recommended to me early on in the project, as a way to divide up responsibilities and keep my codebase well organised.
In hindsight this recommendation was monumental for my work, allowing me to refer back to a clear organisational structure that made it significantly easier to break down problems into smaller, more manageable components and methods.
This layered design resulted in the division of the system, which is actually a widely adopted approach within software engineering. Rather than the tightly coupled code bases of my previous small scale projects, this one was split into three key layers of responsibility.
Application layer. Handling session management, and data processing. 
Api layer. For external communication with both a render server, and ebays api. 
User interface layer. To collect user input and to present the results.
While true that the current implementation of this project still uses this three layered design, as will be explained through this document, the separation between the layers is no longer fully complete.
This is due to several of my files unavoidably containing a combination of api communication, user interface interaction and application logic. A key reason for this is the pyside6 signal and slot system.
When the user interacts with a widget within my user interface, such as selecting an item within a list, the values associated with that interaction are passed directly through the signal facilitated by this system. However importantly, this passed value can only exist within the context of the file and class in which the widget resides.
Consequently if this user input requires a response using data gathered through the api layer and processed carried out by my application layer, all three responsibilities must exist within the same file. Making a cleanly separated layered design impossible.
The files within the api layer still do perform their specialized http requests to communicate with ebays api directly. But it is unavoidable that several files outside of this layer communicate with my render server or local ollama model as part of their specific workflows also. 
Therefore while the architecture of this project is layered in its overall design, in reality there is significant overlap in responsibilities across all of the layers, introduced progressively as the project expanded.
## Layers
The following sections will explain each of these layers, with an added explanation of why this architectural design was chosen, and the effect it had on my project.
## Api layer
### Files involved
The files that make up this layer include; `ebay_client.py` which is responsible for the majority of communication with ebay's api, as well as `server.py`, which holds the code for an external cloud platform hosted flask server.
### Responsibilities of layer

The api layer of this project serves as a bridge between my application, and ebays api. Primarily responsible for handling the majority of external communication that is required to send and retrieve information from ebay directly. Such as sending customer replies, retrieving customer/business conversations, and managing the oauth access tokens received. 

The `ebay_client.py` file is what actually facilitates the gathering of customer conversations and messages from ebay through the use of correctly formatted and authenticated http requests. 

In addition to retrieving customer conversation data, it is also responsible for sending completed customer replies. As well as containing the methods used to actually store the token data received from my external server, saving it locally within the `ebay_tokens.json` file. With this data also being passed to the `token_expired_check` method, before the token data is returned and saved within the desktop application.

The `server.py` file contains the flask server, designed to support the initial oauth authorisation process, hosted using the cloud platform render. This dedicated server handles the initial callback from ebay, receiving an authorization code supplied through the callback url, and then exchanges this code for the initial access token as well as the refresh token.

Requested fields within the token data are then made available to my desktop application, through the use of the `/check_token` route. Including the `access_token`, `expires_in` and `received_at` values. Enabling the authorised http requests later made by `ebay_client.py`. 

Note, a detailed explanation of this entire process is within my `ebay_integration.md` file.

### Responsibility eventual overlap

The api layer was originally designed to allow the user interface layer, and importantly the application layer, to remain completely independent of the implementation details involved. Such as the formatting of http requests, endpoint management, oauth authentication, and response error handling.

However, with the expansion of the project, the user interface and application layers could not remain completely separated from this layer.

An example of this overlap can be seen within the file `oauth_start.py` which is part of the user interface layer, as this file communicates directly with the render server through the initial stages of the authorisation process. Another example can be seen within `reply_dialog.py` and `workflow_two_dialog.py` as both of these files communicate directly with the local ollama api, allowing the user access to the local ai. 

Do note though, that while these files that technically belong to the user interface layer, they only perform the specific communication required for their corresponding workflows. And while it was definitely possible to outsource this functionality to another dedicated file within the scope of the api layer, this additional separation would have increased complexity, and made it harder for readers of the code to understand it, without providing enough benefit within the scope of this project.

### Token management
This api layer has also been designed to manage and monitor the current state of the oauth access token within both my application and external flask server, enabling authenticated communication between the desktop application and ebays’ api, via the use of http requests.
The flask server contained within `server.py` manages the initial oauth process. It is responsible for saving the complete token data received from ebay, rather than just the specific fields later passed to my application. This token data is saved within `ebay_tokens.json` using the `save_tokens` method. At this stage the token data is only saved within the server.
The access token information consequently is made available to my application, through an http request made to the `/check_token` route. Before returning this data however, a check is taken place through the `token_expired_check` method, ensuring that the access token has not expired or will not expire before reaching the desktop application.
As mentioned the `/check_token` route itself, used by the desktop application to access the token data stored within the server, does not return the complete token response from ebay. Instead, when requested, it constructs a python dictionary containing the `access_token`, `expires_in` and `received_at` values. Flask then converts this returned dictionary from the route into json, and it is returned within the body of the http get response.
When a successful response is received, indicated by a `200` response status code, the `request_server` method used by the application decodes the json back into a python dictionary for processing within the program. This data is then passed to the `save_tokens` method to be stored within the desktops own local `ebay_tokens.json` file.
The `access_token` value is what is actually used to later authenticate requests made to ebays api by my application.
The `expires_in` value is used to record the lifespan of the access token in seconds, while the `received_at` value records the time at which the token data was saved. Used in combination within `token_expired_check` these values allow the application to calculate the exact time the access token is set to expire.
This process is covered in alot more detail within my step by step explanation of the token date workflow within my `ebay_intergration.md` file. And also explains why a thirty second buffer is subtracted from the calculated expiry time to protect my application.
### Oauth callback
This section covers what was arguably the most complex aspect of building my application, which was the act of building the set workflow required to facilitate ebay’s oauth 2.0.
Naively, my original design, attempted to receive the callback from ebays api within a locally hosted flask server. During testing however it became apparent that a publicly available url is required to receive the redirect. This led to the creation of my new flask server, this time, to be run on the cloud hosting platform called render. 
Though offering free hosting services, render would offer a cost in the form of a temporary windup time for the server. With this wind up occurring if the server had previously been in a state of inactivity. This was constantly considered in the design of my flask server and its workflow, and is explained in detail within my `ebay_integration.md` file.
To account for the wind up time during the authentication process. When attempting initial communication with the render hosted server, my `request_server` function polls the server every two seconds for a max of thirty attempts. If the limit is reached and no valid token is found, it would signify that either the server is not active and functioning, the token exchange may have been unsuccessful, or the user has simply not completed the ebay login. In any of these cases, the process is then abandoned.
The `/start` route, is what initially awakens the flask server, before redirecting the users default browser to the ebay authorisation page. 
Polling of the `/check_token` route within the render hosted flask server, is also initiated separately by the application at this point.
At the beginning of the login attempt, the desktop application utilizes both `load_tokens` and `token_expired_check` to determine whether a new authorisation process is required. As if the token data already stored locally within the desktop application remains valid, there is no need to attempt to obtain a new access token.
Now here is the step by step process of how my application and render hosted flask server handles the callback from the ebay api endpoint.
The user presses the “connect ebay account” button, within the user interface.
My application opens the local desktop’s browser to flask's `/start` endpoint. 
The desktop application polls the `/check_token` endpoint of the flask server, via the `request_server` method.
An oauth authorisation url is then generated, and the user is redirected to ebay's login page to authenticate communication between the application and ebay api endpoint.
Once the user has authenticated, ebay redirects the browser to flasks server’s `/callback` endpoint, with an authorization code passed via url.
The `/callback` route then exchanges the auth code for an access token, via the use of a http post request to ebay’s api endpoint, then the token is saved within the server through the use of the method `save_tokens`. 
When polling from the desktop application detects a valid token within the server, using a `/check_token` route request, the token data is saved locally within the desktop.
Once the initial oauth callback has been completed, the application holds a valid access token as well as its expected expiry time. 
### Data Retrieval Methods
The api layer also provides methods such as `get_conversations` and `get_conversation_messages`, which utilize get requests to gather information from the ebay api to be displayed within the application. This allows the application to request customer conversations, without the need to construct any sort of api call, or be involved with the parsing of the response. Instead this is carried out within the api layer, specifically `ebay_client.py`.
### Error handling
Each of the methods within `ebay_client.py` validates that the http status code returned by the associated requests made to ebays api, are in line with expectations. 
If the request is unsuccessful, a run time error will be raised within the specific method, containing a clear error message for the user along with the returned status code. This immediately identifies where the failure has occurred, before any incorrect or incomplete data is returned. The user interface will then display a message through a `qmessagebox` to alert the user that an error has occurred within the current workflow.
Other files including `oauth_start.py`, `reply_dialog.py` and `workflow_two_dialog.py` also handle responses from http requests made to either the render server, or the local ollama model.
Although this means that http error handling is not completely contained within `ebay_client.py` the attempt was made to centralise this handling where feasible, as this was part of my original design. The aim being, to keep all error handling as close as possible to the external communication that may cause the failure. By doing this unsuccessful responses are prevented from being bypassed further into the applications, to be mistakenly taken as valid data. It also reduces the need for repeated status code checks throughout my work, making critical errors easier to locate and solve.
## Application Layer

### Files involved

One of the primary files involved within the application layer is `user_class.py`. Which defines the “user-object” designed to store all of the information about the present user within the current session of the application. Including the currently selected workflow.

Note, in the current iteration of this project, `chat_widget.py` also separately stores the `customer_selected`, `current_conversation_id` and `messages_stored` values. As it was decided that there was no need to transfer these values to the `user_class` to be then used within `chat_widget.py` and its subsequent dialogs produced, throughout the reply generation process in workflow one.

However, in addition to storing session data, `user_class.py` provides my application key methods such as `initialize_session` and `sanitise_text` used throughout the application. `user_class.py` offers accessibility to this important functionality, without requiring other modules to implement the logic separately, causing needless duplication of code.

Additional files such as `options_dialog.py` and `generate_dialog.py` contain the logical methods relevant to their corresponding areas of the project, to enabling both the editing and enrichment of user replies within `options_dialog.py`, and the generation of ai assisted customer replies within `generate_dialog.py`.

### Responsibilities of layer

This layer is primarily responsible for the decision making of the application, and the various logical processes that take place within both of the optional workflows. Sitting between the user interface and the api layers, it effectively coordinates what specific actions should be carried out in response to the user actions within the current workflow selected.

For example, when a customer conversation is selected within the user interface of my `chat_widget.py` file, the application layer requests the conversational data from the api layer, using the qlist widget items `conversation_id` value. When this response is received, the conversational messages and the sender's details then passed to the ui to be displayed. 

Do note, that in the current iteration of my project, the separation between the application and api layers have effectively been blurred. With the example above displaying that the method `get_conversation_messages` used to obtain the message data for the currently selected conversation, is effectively part of the api layer, but is present within the `chat_widget.py` file. 

This will be discussed in a lot more detail, in the layer overlap section below.

Depending on which workflow is selected by the user at the start of the application login process, this layer is also responsible for restricting/enabling certain areas of the applications functionality. Allowing both workflows to share the same underlying application, while enforcing the different behaviour required to meet the restrictions placed on the application, through the current ebay developer program license agreement.

Also included within this layer is `options_dialog.py` and `generate_dialog.py` which provide specialised logic for the specific dialogues in question. With `options_dialog.py` handling the editing and sanitisation of a manual reply, and `generate_dialog.py` handling where users can choose to instead generate a customer response via local ai.

Lastly, another key responsibility of this layer is in compliance enforcement. Ensuring that no sensitive data gathered through the use of ebay’s api is ever permanently stored within the system. This is done to avoid any violations of the ebays developer program license agreement. Instead of relying on the user, the logic of my application actively enforces the complaint process. 

### Data Sanitisation

As discussed within the section above, a core responsibility of this application layer is to ensure the data sanitisation process is effective. This is because before any information is passed to the local `llama 3.1:8b` ai model, data must first be processed using the `user_class.py` method `sanitise_text` and be manually reviewed by the user, to ensure that no personally identifiable information is present. 

This `sanatize_text` method is used exclusively within workflow one, and utilises the microsoft presidio library, residing within the `user_class` object. Allowing the method access to the current active session data, while also allowing the sanitisation of customer conversations wherever required, throughout my application.

Presidio's `presidio_analyzer` first scans the text using a combination of both regex pattern matching and the spacy natural language processing model, attempting to identify types of identifiable personal information. The locations of these identified segments within the text are then noted.

Using both the locations collected, and the type of identifiable data, this information is then redacted by presidio's `AnonymizerEngine`. Replacing the original text with placeholder tags, instead of removing it entirely. Allowing the user to see exactly where the information has been redacted in review. 

Failure to sanitise this raw data, gathered from the api, could result in a breach of ebay’s api license agreement and a violation of data protection legislation. Especially if the data were to be processed through the local ai.

### Layer Overlap

While attempting to keep this application layer as isolated as possible, it should be noted that there was an overlap of responsibility within the files `options_dialog.py` and `generate_dialog.py` as these two files both contain user interface elements in addition to application logic.

This overlap simply became unavoidable, due to the growing complexity of the project nearing the latter stages of development. 

As with the amount of logical methods, it became increasingly more difficult for me to manage the sheer number of workflow specific functions within completely separate logical modules.

Connecting user interface widgets signals to the corresponding slots, where the logical methods would be executed, became far more complex when both were located within entirely separate files, and impossible in situations where data passed through the signal was required within another file. 

Also endless jumping between modules to connect workflow actions to their corresponding slots, made the entire codebase increasingly difficult to follow and maintain.

By merging the logic for each workflow with the ui elements that directly interact with it, the relationship between the user's actions, logical processing, and the resulting output could be visually followed within the same file.

It is also key to note that the user interface elements involved, within the application layer, exist only to serve the actual logical process within the file, either by presenting results or collecting user input. An example of this is within `generate_dialog.py`, being the method `render_messages`, which renders `qlables` objects to present the conversational messages to the user. A process that would require a different solution, if the logic and ui resided within different files.

This decision occurred naturally as the project evolved, as the original intention was for each workflow to be supported by its own dedicated logical file. As the original approach would result in a large amount of functionality being shared between the two workflows, as well as possibly an alternative approach to building the user interface within my program.

### Conversation management

Conversation management within my application is yet another example of layer overlap between the application layer, and api layer. 

When `chat_widget` is opened, after the login process is complete, the `get_conversations` method is called and a `qtimer` is started. Every ten seconds this `qtimer` calls the `conversations_loaded` method which retries all of the conversation data for the linked ebay account through requests made to ebays api.

Each of the `qlist` widget items within this conversation list, holds a unique conversation id value assigned to it through the use of the `qt.userrole` system. The id itself is used to identify each of the conversations within the list.

As while it is possible for an individual customer to have two ongoing conversations with the linked ebay account at the same time. Each of these separate conversations will always hold a unique identifier in the conversation id value. 

This unique identifier, accessed through each widget items `qt.userrole + 1` value, is used to find the previously displayed, user selected conversation after each list refresh. Important as without this process, the user, every ten seconds would be forced to reselect the conversation they were viewing within the ui before the refresh occurred.

This also enables my application to keep updating the actual message data in the display. As each time the conversation list is rebuilt, the message data for the selected conversation is automatically requested from ebays api.

My application also maintains an exclusion list for the two types of faulty conversation ids that produce a `404` response from requests sent to ebays api, when attempting to gather their corresponding message data.

Firstly, permanently faulted ids, which are ids manually excluded by the viewer outside of the application, are loaded from `faulted_conversations.py` when the widget is created. And secondly, ids that fail during the current session. Both are appended to the same in memory list within the program. When the conversation list is rebuilt, excluded conversion ids within this list are compared against the ids received from ebay, and are skipped in the building process if necessary.

## Ui Layer

### List of files involved

`initial_window.py`, `login_dialog.py`, `create_account_dialog.py`, `workflow_dialog.py`, `chat_widget.py`, `options_dialog.py`, `generate_dialog.py`, `oauth_start.py`, 
`review_dialog.py`, `reply_dialog.py` and `workflow_two_dialog.py`.

Shared user interface styling is also contained in `qt_style_sheet.py`. 

### Responsibilities of layer

The core responsibilities of the user interface layer is to display information and possible actions to the user, collect the resulting input, and then present the outcome of the actions back to them. 

The ui layer does have some direct contact with the functionality of the api layer within `chat_widget.py` as this file calls retrieval and sending methods imported from the `ebay_client.py` file. But the construction of the underlying ebay http requests remain within the that api model.  

The responsibilities of this layer do expand beyond presentation however. As the ui within my project handles sensitive customer data obtained from the ebay api. 

Designed to ensure trained human decision making remains an integral part of both workflows, the interface actively supports compliance. Done through the use of mandatory user review and confirmation at key stages, actively blocking progression if needed.

### Signal and slot system

As the application user interface was developed through the use of pyside6, it has access to the qt signal and slot system. 

Within the qt framework, a signal is an event emitted by a user interface element, such as text being entered within a widget, or a button being clicked. 

A slot is a method connected to the signal, which is executed automatically by the system whenever the corresponding signal is emitted/triggered by the user. These signals are constantly listened for by the qt framework.
This mechanism allows for loose coupling between the user interface components and application logic, as the ui components have no need to understand the complexity of the method they trigger, and vice versa.

For example, within the file `chat_widget.py` the signal and slot created, `self.send_button.clicked.connect(self.send_reply)` showcases the “clicked” signal, and the “send_reply” slot. As when the “send_button” is clicked, the signal is emitted, calling the slot method via “connect”. No additional wiring or conditional logic is required.

This system was one of the main reasons psyside6 was chosen for this project. Being a newer developer, having the ability to add new functionality throughout any stage of the project through the use of simple methods and connections was invaluable. 

Without this system, tighter coupling of ui components and logic would require constant restructuring and rewriting of code. Especially as the project continued to evolve, since the overall design of the project changed so drastically during development.

### Manual review

Lastly, handling sensitive data obtained through ebay’s api, it is a key requirement that my user interface enforces the users to manually review actions made throughout the process.

An example of this can be seen within the `generate_dialog.py` workflow, where conversational history is displayed. This text must be both sanitised by the program, and then read by the user, before the process can continue to generate a reply. The mandatory review is enforced, as the generate button is intentionally disabled until sanitisation has been confirmed, and the user has verified a manual review of the text has been completed. To make sure no sensitive personal information, gathered through the api, is entered into the local ai model.

## Dual Workflow Design

The most significant design decision made throughout the entire project was the introduction of the two separate workflows, as originally this was not supposed to be the case at all.

The original design of my project included a single, highly automated workflow, where customer conversations would be retrieved through the api and then directly passed into the local ai model to then generate a reply. However as the project developed, and my understanding of data handling and the api agreement improved, two issues became clear.

Firstly ebay’s platform restrictions, imposed by the developer program, placed restrictions on how sensitive customer data could be handled and stored. And secondly, because of the limitations imposed by data protection legislation, a fully automated pipeline carries risks that sensitive information could be accidentally passed to the local ai model without review.

At this point in development, ebays own on platform ai was also evaluated as a potential answer to this problem. As this in built ai feature is capable of suggesting replies to customer messages, without said data leaving the platform. On the surface this appeared to be a compliant alternative. However on review, and through the quality of the responses produced during testing, it became clear that the system lacked access to the vital business specific knowledge required to answer customer questions effectively. While the on platform ai could produce generic responses, questions regarding item specifications, packaging details and delivery specifics require internal business information.

Without access to said data, the responses produced lacked the detail to effectively reply to the customer. The decision was therefore made to introduce automated sanitisation into the original workflow. Along with a secondary alternative optional conservative workflow. Introduced as a safeguard against any future tightening of ebay’s platform restrictions.

This introduction of automatic sanitisation within the first workflow, ensured that all personally identifiable information is either redacted by my application, or is manually excluded through the process of the enforced mandatory user review, before it reaches the local ai. With the inclusion of human review, extra additional safeguards are added to this process. Ensuring that no raw customer data retrieved through the ebay api is ever processed by the ai without explicit user approval. Directly addressing both eBay's developer program restrictions and the requirements of data protection legislation.

### Workflow summary

For an in depth step by step explanation of both workflows, please see my `README.md` file.

## Database design

Using a local `sqlite` database, as this is where most of my database experience and query building lies. A simplistic database was built with the purpose of allowing multiple users to authenticate themselves/sign in to the application at the start of each session.

This database is entirely separate from the user live ebays account used to authenticate this application. The ebay credentials are separately managed through the oauth process. Where as the only details held within here are the usernames and passwords…

The contents of this database, in an encrypted password and username, solely protect access to the application itself. Meaning that the highly sensitive login details of the user’s ebay account are never entered or stored within the database.

A local sqlite database was chosen for this project, as this is where most of my databasing and query building lies. With the simplistic purpose of allowing possible staff members to sign into my application at the start of each session, each with their own separate account.

It is worth noting that this database is entirely separate from the ebay account used by the application. The credentials for ebay are separately managed through the oauth process and never interact in any capacity with this database. The only details held within this database are the usernames and hashed passwords used to access the application itself, meaning that the highly sensitive login details of the users linked ebay account are never entered or stored at any point. 

The database contains a single table;

`CREATE TABLE IF NOT EXISTS users ( 
id INTEGER PRIMARY KEY AUTOINCREMENT, 
username TEXT UNIQUE NOT NULL, 
hashed_password TEXT NOT NULL, 
recent_login_datetime TEXT)`

Storing the users incremented id, username, hashed password with added salt, and the date and time of the most recent login, formatted as `iso 8601`. Which is the standardized format, internationally used to display date and time.

This database engine was chosen to allow the application to operate locally on a single machine. Requiring no dedicated database server, unlike alternative database engines. Sqlite stores the entire database within a single file, directly accessible by the application. Massively simplifying the process of setting up of the program, and removing the cost of maintaining a separate database service.

Postgresql, was the only other alternative considered, but again, was ruled out as it required a dedicated database server. This is because postgresql is designed for applications requiring concurrent connections, network accessibility across many machines, and for much larger datasets than this project requires. As with only a handful of staff accounts ever likely to exist. Sqlite seemed to me to be an ideal choice.

The database itself stores only account credentials and does so securely. Allowing the application to be used by multiple staff members, without sharing a single login. Login times are also recorded, giving the user/business a clear record of who was logged in when specific actions were performed.

### Password Security

Rather than simply storing passwords in the database using a standard hashing function. This project instead uses `pbkdf2-hmac-sha256`, which is a password hashing algorithm designed to securely store user credentials. As in addition to hashing the password, the algorithm combines the password converted to bytes with a randomly generated sixteen byte salt, before performing six hundred thousand iterations. This is done to significantly increase the computational effort required to test each password guess, therefore protecting against both brute force attacks and rainbow tables.

Unlike a simple hash function, `pbkdf2` repeatedly executes the hashing process using the result of the previous iteration, significantly increasing the computational effort required to test each possible password guess. Where a simple hash can be computed almost instantly, a six hundred thousand iteration process makes brute forcing a realistic password set computationally expensive for an attacker.

The value stored within the `hashed_password` column is formed from two components. First the randomly generated sixteen byte salt, and then the 256 bit key derived from the `pbkdf2` process. Both of these values are converted to hexadecimal, joined and then stored as a single string. This means that the salt can always be recovered for verification, without requiring a separate database column, keeping the schema simple while maintaining the full security benefit of the salted hashing.

Note, the salt itself is not hidden, as its purpose is to ensure identical passwords which may be used by two or more staff members, produce entirely different stored values when passed through `pbkdf2-hmac-sha256` rendering pre calculated rainbow tables useless.

Verification is handled by the `verify_password` method. When the user attempts to login, the stored value is first separated, extracting the salt and the previously generated hash. The extracted salt is then combined with the entered password, and then passed through the same `pbkdf2-hmac-sha256` process. If the newly generated hash matches the separated stored hash, the user is successfully authenticated within the desktop application.
