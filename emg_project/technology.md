# Technology

## Introduction

In addition to my `design.md` file this document will cover the choices made in terms of technology throughout the development of this application. With the various reasoning behind each decision. I will also go into detail about why each piece of tech was chosen for its particular role within the project, along with any possible alternatives that were considered.

## Coding language

Python was the natural choice for this project, being that it was the initial and primarily language taught throughout harvard's cs50 course.

Developing this application in python allowed me to focus my attention solely on the design of the application. Because rather than dedicating time to learning a completely new language, my focus could be committed to planning and problem solving. Particularly important given the overall scale and complexity of this project.

Beyond familiarity, python’s widescale ecosystem of libraries was a significant factor. Libraries such as presidio, and requests offered python packages that were all critical to this project. Allowing for imported complex functionality to be integrated at any stage of development. Particularly valuable, as the overall design and organisation of my application was not fully defined at the start of the process. So as new requirements emerged, solutions could be incorporated through the use of additional pythonic libraries.

Additionally python's renowned readability also allowed my codebase to be clearly understood even at the latter stages, when at its most complex. Offering clear self explanatory syntax, and enforcing consistent convention, making for extremely readable code. Resulting in files, even that when written the month before, could be understood relatively quickly after a quick read through. Vital given how frequently jumping between files was necessary, when following signal and slot connections across the codebase. 

### Alternative language

C code was also considered, after again having gained experience with the language throughout cs50. 

Though undoubtedly offering superior performance, with faster processing times and massively more efficient memory usage in comparison to python. For a project of this scale and nature, this increased performance would not outweigh the development time required. As with the application being designed for a single user, and performing only lightweight processing involving displaying data, handling input and conducting occasional api requests. The applications performance is actually more limited by user interaction and network responses, rather than by raw data processing speeds.

Beyond performance, c code also introduces significant security risks in my case. As manual memory management, pointer creation and buffer overflow vulnerabilities were a common occurrence when first learning the language and could very well cause issues when the project's scale and complexity increases. And within a system handling both oauth tokens as well as the sensitive customer information, unforeseen errors within my program could possibly result in a serious security breach. Python’s automatic memory management, while less exciting, removes this danger, allowing me to focus on developing on logic and security design rather than low level implementation details. 

## Ui framework 

I decided to use pyside6 to build the user interface layer of my application, providing python access to the qt framework. Two alternatives were considered, before this decision was made in both kivy and electron.

### Alternative frameworks

Kivy, also an open source python framework, specialises in the creation of ui for mobile devices, which was originally interesting, as the target audience for this application would find use of a mobile version when commuting, allowing customer queries to be handled within the downtime.

However, due to the application’s original design for desktop usage, the interfaces involving multiple panels, scrollable lists and text editing, clashed with what mobile interfaces are suited for. Also due to the nature of hand held devices, compliance issues could possibly arise, with the careful manual review of customer data being significantly more difficult on a small screen. Introducing the possible violation of data protection legislation. Alongside these issues, adapting the existing oauth/api workflow to support a mobile application would increase the complexity of this project tenfold, making the transition to this framework an unnecessary risk.

Electron was also seriously considered as an alternative. Being a popular framework for building desktop applications using html, css, and javascript, three languages familiar to me through my cs50 studies. This familiarity with building web based environments was significant alone,
allowing me to focus on design work rather than an extensive learning curve to adopt a new framework such as it would be for pyside6.

Electron's ecosystem is also enormous. The framework, having been widely used for many years, offers a large amount of documentation and support in the form of tutorials, examples and community posts. Which would make the initial learning, troubleshooting and solution searches straightforward for myself as a newer developer.

However, for an internal business tool, the advantages of electron are largely negated. The main issue being that the chromium engine that the electron framework runs on, is simply too resource heavy. Designed for the rendering of complex web content and managing multiple browsers simultaneously, of which my predominately offline and local application requires none. 
Displaying text, handling button clicks, and managing dialogs, all performing just as well in pyside6. As the visual appeal of the framework is simply not a priority, as the interface design was always intended to prioritize clarity and usability over aesthetics. With staff requiring fast reliable navigation.

### Framework conclusion

For an application running on a single local machine, consuming these unnecessary system resources would bear no tangible benefit for an avoidable cost. PySide6, as a native desktop framework, runs considerably lighter. Fulfilling the job of the ui layer to simply display conversations to the user and to collect input without the overhead of electron.

Crucially, pyside6’s signal and slot system also provided me with an invaluable way to develop ui actions into my system. Connecting the widget actions to application logic without the tight coupling of components. Meaning that new functionality could be added at any stage of the project without the need to rewrite sections of code.

Access to qt designer was also a benefit. Allowing me as a computer animation grad, eliminate the disconnect between the visualization of an interface and translating that to code. As the program allowed me to translate sketched out prototypes directly to functional layouts.

Alongside qt designer, pyside6 enabled me to apply visual changes across my application in a similar way to using css to stylise html in web design. My styling, stored centrally and applied through `app.setStyleSheet`, avoided the need to repeatedly style individual widgets through the project.

Lastly, because of the modular nature of pyside6, the framework was well suited for the architecture decided on for this project. With each widget and component naturally sitting within its own separate file. Lining up perfectly with the layered design described within my plan. Allowing me to build new components or functionality for the project, test them individually and then integrate them without disturbing the rest of my program.

## Chat widget

The `chat_widget.py` file offers a central interface where the user can view and select the customer/business conversations retrieved from ebay. As selecting a conversation will display its messages in the accompanying panel. From here the user has access to the tools required to produce and send a reply back to the customer.

The interface is built around two pyside6 widgets in a `qlistwidget` to display the available customer conversations within a list, and a read only `qtextedit` which displays the full message data for the currently selected conversation.

This data displayed within the list of conversations, is gathered from the json response returned by ebays conversation api endpoint. After this response is automatically converted to a python object, each individual conversation is represented by a `qlistwidgetitem` and is added to the list within the `qlistwidget` block.

The sections below will explain how this conversation window functions and how the message data, corresponding to the conversation selected, within the list are retrieved.

## Chat widget conversation refreshing

This next section will talk about the use of the `qtimer` object offered by pyside6 within the `chat_widget.py` file.

The chat widget dialog utilizes two types of pyside6 widgets to display the conversational and messaging data this application retrieves from ebays api. The first being a `qlistwidget` that displays the selectable customer conversations within this dialog, and secondly read only qtext edits widgets that display the messages to the corresponding customer conversation selected.

Together, these widgets create the central interface for my application, allowing the user to select the specific customer they want to reply to.

### Qtimer usage

To ensure that the list of conversations, and the messages within, stay up to date for the user a `qtimer` object is used to call the method `refresh_conversations` every ten seconds. Allowing a new updated conversation list to be generated, visually seamlessly, while the application remains open.

Before the list is rebuilt however, the currently selected customer conversation within the window is recorded. This is done through the storing of the corresponding conversation id. The application uses this id to restore the same conversation displayed before the conversation list refresh. Preventing the conversation, currently being reviewed by the user, to disappear off from the dialog every ten seconds.

Note, that the timer will only effectively refresh the list of customer conversations available. The message history belonging to said conversations is requested separately, after a conversation has been selected from the list, by the user.

Keeping the methods of conversational and message data retrieval separate, also allows my application to avoid requesting the complete message history of every conversation, when populating the conversation list. Minimising the data retrieved from ebays api, as only the message data from conversations the user actually selects is requested. 
 
### Message retrieval

When the user selects a conversation within the `qlistwidget` a signal is emitted, specifically the `itemclicked` signal. This signal is again, a part of the signal and slot system offered by pyside6, and connects the signal to the method `select_conversation` within the same dialog. Causing this method to be reactively called, with the specific selected `qlistwidget` item selected by the user passed to it as an argument.

From this point, the `select_conversation` method, retrieves the conversation id stored within the item selected.

This is achieved because, each `qlistwidget` item within the list represents the conversation being displayed. As while each item includes the conversation details visible to the viewer, such as a customer account username and latest message preview. It also stores additional information through qts `userrole` data roles.

This `userrole` system ensures that the conversation id, and the reference id of the item involved in the conversation remain tightly associated with the specific conversation they represent.

The data roles themselves act almost as hidden labelled friends attached to the list item they represent. Allowing information that isn’t viewable within the interface itself, to be readily available to the application when the item is chosen.

An example of this stored information being used, is the item name displayed within each conversation in the list.

The item name related to the conversation is not included within the conversational data passed to my application, from the external render server. However it still can be found through the use of the reference id stored within the `userrole` data attached to the corresponding `qlistwidget` item. When matched, through looping through the `item_ref_dict.py` file, the item name is added to the visible details displayed for that conversation.

Storing the conversation id through the `userrole` also means that the application does not need to use the visible customer username to identify the conversation. This is important because one customer may have multiple separate conversations, each with its own conversation id.

Once the message data, for the conversation selected, is returned, the messages are reversed in order to ensure the latest message appears at the bottom of the `qtextedit` display.

The sender of each message is then identified by comparing each messages `sender_username` to the username of the ebay account authenticated within this application. Allowing messages sent by the customer to be identified and aligned to the left, and the businesses messages to the right.

Finally, both the conversational and message data are only held within memory during the active session of the application, and are discarded when the application is closed. Ensuing this application abides by the restrictions set by ebay regarding customer data protection. 

### Faulted conversation exclusion

Testing of the conversational data returned from ebays api showed that some of the conversation ids passed to my application, would return a `404` or `item not found` response when the messages belonging to that conversation were requested.

This was due to issues on ebays end, as some of the attached conversational ids would lead to corrupted corresponding message data that was no longer available through the message api endpoint.

To prevent these unavailable conversations from cluttering the `qlistwidget` within the interface, an exclusion set containing the faulty conversational ids was created within the `faulted_conversations.py` file. These ids were then imported into `chat_widget.py` on the dialogs creation.

Along with these permanently excluded conversation ids, any conversation returning a `404` within the runtime of the application would also be added to a separate exclusion set.

An automatic refresh after the discovery of a new faulted conversation ensures that, once discovered, these conversations disappear from the interface reactively.

Whenever the conversational list is rebuilt, each of the conversation ids within the qlist widget items is checked against both the permanent excluded set imported through the `faulted_conversations.py` file, as well as the session created exclusion set. When a match is found, the conversation linked to the id will not be added to the `qlistwidget` and is skipped.

If a conversation id is discovered to be faulty within the runtime of the application, identified through a returned status code of `404` when attempting to retrieve the message data, it is added to this session exclusion set.

This set of discovered faulty ids is held in memory only while the application is active, and is discarded on its closure. 

Preventing possible violation of ebays developer license agreement, as strict restrictions exist against the automated collection of api gathered information within the design of an application.

## Http communication

One library used throughout this application's creation is the `requests` library. Apart from allowing the creation of get and post http requests within my application, needed to obtain the live message and conversational data for this project, these requests also enabled communication with both the external render hosted flask server and the locally running ollama server.

Json data returned within the bodies of these responses also required decoding, typically into python dictionaries and lists. By calling the `response.json` method, offered again by the `requests` library, the json contained within the response body is decoded.

A clear example of this can be seen within my `get_conversation_messages` method within my `ebay_client.py` file. As this method uses the `requests` library to send a get request to ebays message endpoint, for the specific conversation selected by the user.

Using `api_response.json` the json data within the http response body is decoded into a python dictionary. As well as the method `.get()` along with the parameters `.get(“messages”, [])` to obtain the list of messages dictionaries stored within the `messages` key.

An absence of this method would force each of my methods receiving http responses to convert the data manually, adding additional logic to read and decode the data.

## Http basic auth

The `requests` library is also used within my application during the oauth authentication process, specifically within the token exchange. As when my render hosted flask server sends an authorisation code to ebay, through a http post request to the `https://api.ebay.com/identity/v1/oauth2/token` endpoint. The request must include the `client_id` and `client_secret` values. This is so that ebay can identify my registered application within their database, before providing a http response to my request, with the token data.

Both `client_id` and `client_secret` are passed to the `auth` parameter of the http request, as a pythonic tuple. The `requests` library automatically combines these values in the format of client_id:client_secret.

This combined value is then encoded using `base64` to represent the data. The characters within the resulting value each represent a six bit section of the original binary data. When combined, the original credentials can be reconstructed. This is the format required for http basic authorisation.

Note that, the `auth` value is a parameter passed to `request.post` to be used to create the `authorisation: basic…` header, which is completely separate from the requests body. And this is the exact format that ebay expects to receive the applications credentials, as explained within their documentation.

## Oauth server

Note for details on the purpose of this server, and how it fits into the oauth workflow, please look at my `ebay_integration.md` document.

### Oauth server framework

Flask as a framework was chosen to build the required callback server, necessary as a publicly accessible callback url is required by ebay’s oauth implementation. Redirecting the user after the successful authorisation of their account. 

Having built flask servers during cs50, this familiarity with how the framework operates played a significant role in this decision. But the simplicity of the server's responsibilities, also made the flask framework well suited for the task at hand. 

With the routes involved to facilitate the oauth process, requiring only lightweight operations. Such as generating an authorisation url within the route `/start` redirecting the user’s browser to the login page. Or within the `/callback ` route, where the received authorization code is exchanged for a valid access token via a http post request, then saved server side. The remaining routes simply return status information to the desktop application on request.

Flask’s decorator based routing makes the implementation of these endpoints simplistic and readable, with each route being a single function is a self contained process, with a direct way of being called.

Django was also briefly researched as an alternative. Django is designed for large, content heavy applications that require database interaction, and dynamic page rendering. Which my callback server does not require. Meaning that introducing django’s for a project structure as small scale as mine, with only a small number of lightweight routes, would be adding complexity to my project for the sake of it. As flasks simple readable architecture, and my existing familiarity with the framework, made it the most practical choice.

### Gunicorn

Note, when deployed to render, the flask application is not actually served using flasks in built development server. As it is intended for development and not production.

Gunicorn is instead used, a production ready web server gateway interface. Which sits between the render host and the flask application, receiving incoming http requests and passing them to the corresponding route of my flask server. Providing a reliable way of exposing the oauth callback endpoint to ebay.

## Cloud hosting

Render was chosen to host my flask server, and is a cloud hosting platform that allows web applications to be deployed, making them publicly accessible over the internet.  

The need for cloud hosting support came directly from the fact that ebay’s oauth requirements demands it. With the platform not accepting any callback urls that point towards a local host. So making a publicly accessible server is a necessity, if communication is to be had with ebays api. 

### Alternative hosting

Amazon's cloud services were the other option considered. Through my initial research, it became apparent that aws is industry standard for cloud hosting, with the service being widely used due to its reliability. However, upon further reflection, using this service to host a single lightweight server with only a handful of routes would introduce unnecessary complexity to my development.

To deploy even a basic server using aws, significant configuration is required. From my understanding, setting up the required networking and services demands considerable prior knowledge of the platform before an application can be deployed. Without even getting started on managing the pay structure involved. Unlike render, deploying a server cannot be done directly from a github repository in a short amount of time.

However that being said, aws is a platform that I had intended to develop proper experience with in the near future, through the course clf-c02. Once familiarity with the service is established, migrating the callback server to aws may be a natural step for me.

### Render

Render offers an accessible alternative in the meantime for a project of this scale. With simple github based deployment and straightforward environment variable management through renders beginner friendly server set up interface, utilizing render became the practical option.

My awareness of a possible future migration to aws came from the fact that render does have some trade offs. While completely free, the service at this tier does include a wind up delay after a period of inactivity. Meaning that the initial request can take several seconds for the server to restart. For my oauth process, this presented a unique problem.

To account for this, the polling mechanism within `oauth_start.py` actively avoids a simple single request attempt, to access a valid token from the server. Instead, a delay has been incorporated into the workflow, with the `request_server` method called every two seconds through the use of a `qtimer` object, for a maximum of thirty attempts. Giving an approximate grace period of a minute before timing out.

This compromise admittedly is not the most efficient solution. However, the wait time is acceptable for access to the free hosting service. As once valid token data has been stored within my application, any api requests made afterwards are solely directed to ebay, until that locally stored access token expires. Meaning that the render hosted server from that point on is no longer involved in the communication process.

## Local ai

The local ai component of this project is run using the program ollama. Ollama is a tool that allows for large language models to be downloaded and run entirely on a local machine. Once running, a small local server is started that listens for http requests from my application. Allowing communication with the model in the same way my program communicates with the render server, except all communication takes place locally on the user's computer.

Ollama running locally on the desktop, is accessed by the application through the use of post requests sent to the, again local `http://localhost:11434/api/generate` endpoint. With these requests created through the `call_ai` methods present in both my `reply_dialog.py` file, as well as the `workflow_two_dialog.py` file.

The requests made to the locally installed model include constructed prompts from information gathered from several files within this project, and a generated response is received in return. This response from ollama is returned within a single json object, with the text generated contained within the response data.

## Model

Llama 3.1 is the actual model chosen to run through the use of ollama. Specifically the 8b variant, which stands for the eight billion parameter version, which is downloaded and stored locally on the machine. 

Requiring 4.9 gigabytes worth of free disk storage for the current version, used within this project.

The 8B version was chosen as it offers a balance between resources required by the hardware, and the quality of the actual replies produced. Larger parameter versions of llama 3.1 exist, and do offer an improved output quality, but however do require significantly more memory and processing power. Resulting in real costs for the user/business, both in physical hardware requirements and the electrical costs of processing the data.

Originally it was my idea to instead use a fine tuned mistral 7b model, trained on historical customer conversations to heighten the quality of the responses, offering unique business specific replies to the user. Along with a consistent tone.

However, after researching into the details of the ebay developers license agreement, it became apparent this would result in a direct violation. As using customer data, accessed through the api for model training, is explicitly prohibited. Which led to the pivot towards a prompt driven approach, rather than an attempt to train the model using past customer conversational data.

Rather than training the model on customer data, the application instead hands off business specific information to the ai through the prompt itself. 

Within the first workflow this is combined with the sanitised conversational history, whereas in workflow two it purposely does not receive any sensitive information.

The contents of the file `business_info.txt` that holds all internal business information that's appropriate for customer inquiries. Product details, business policies and tone are all examples of instructional details that are handed off. Allowing the user to receive non generic, business relevant responses, without the need for the model to ever receive raw customer data. Or persist any of this information past the active session.

## Ai models first workflow

The ai response generation of workflow one, is handled primarily within the `reply_dialog.py` file.

The actual prompt used by the llama model to create the generated reply, is built within the `build_prompt` method. As a single location was required to organise order, and combine all of the information needed to produce a high quality customer reply.

Text instructions are the first information added to the combined prompt. Imported from the `prompt_workflow_one.py` file. These provide the model with the actual rules it must follow when creating a reply for the user.

Secondly, the now sanitised and also manually reviewed, specific ebay conversation is included. Giving the model the context of the customer enquiry, without needing to see the original highly sensitive customer data.

Next the internal business information from `business_info.txt` is also added to this combined prompt. Providing the model with information such as the unique business policies and product details that might be required to construct an accurate reply for the customer enquiry.

After this static information is added, the current in progress reply is added to the prompt. That is if one exists. As the generated reply produced by the ai might need to be tweaked and edited before it is sent off, as producing a fitting reply may be an on going progress.

Sending an in progress reply, along with any other messages between the user and the ai model, allows the model to see what has been already generated and what actual existing text reply is required to be improved,

Any previous conversational messages between the ai model and the user are also included. With each message being labeled when stored within the `generate_reply` method, allowing the model to identify which message was created by the user, or if it was generated by the ai.

Allowing the model to understand the previous context that has led up to the current point, and the state of the reply. As rather than treating each new request from the user as a completely separate task, in terms of how generation is approached, the model can instead continue from the work already completed within the current conversation. Using that context to form the next generation of reply.

Finally, the last addition to the combined prompt is the latest instruction entered by the user within the `qtextedit` widget. This tells the model what the user is currently asking for, as while all of the other information gathered above does provide the context required to produce a high quality response, this last request is actually the most important piece of information for the ai. Determining what the model is actually being asked to do with all of the context provided above.

This could involve the creation of a new reply, altering a current in progress reply, or answering a question the user has about how a certain customer enquiry could be handled.

## Ai models second workflow

The second workflow requires a completely separate approach to prompt creation, to be sent to the local model. Handled separately within the `workflow_two_dialog.py` file, this dialog is designed to provide general business assistance to the applications user. This is done without the need for any sensitive customer data to be involved.

The first information to be added to this workflows combined prompt, is the general instructions imported from the `prompt_workflow_two.py` file. These instructions are not created by the user, and live static within the imported file. And are used to establish that the local model is speaking to the user directly, rather than communicating with the customer of the business, as was the case within the first workflow. Ground rules are also set for the information this model should ask for within the conversation with the user, avoiding any request for possible sensitive information when answering questions.

Internal business information is the next category of information combined with the constructed prompt, and is again imported from the `business_info.txt` file. Allowing the model access to the supplied product information of the business, along with its policies and unique shipping details.

Previous messages exchanged with the model and the user are also added to the combined prompt. Again, in an attempt to provide the model with the context needed to approach the current task as a continued part of the conversation, rather than a singular external task to be completed. 

Note, similarly to the first workflow these messages contain identifying keys to distinguish between messages written by the user or generated by the ai, allowing the model to understand the ongoing conversation up until thai point.

The most recent question or instruction from the applications user is also added. To provide the model with the current task to be completed, after receiving the context provided by the combined prompt up to this point.

## Differences in workflows

The largest difference between these two approaches to prompt creation and model usage, is the mindfulness of avoiding sensitive customer data, sanitised or not, being added to the combined prompt to be sent to the model. The `workflow_two_dialog.py` file never receives any of the previously collected customer data retrieved through the api, and this was by design. As being completely separate to the customer data, temporarily stored within `chat_widget.py` there is no opportunity for any sort of violation to ebays developer license agreement. Effectively making this secondary workflow impervious against any future changes in policy to ai usage of customer data. Offering the user a beneficial use of this application, no matter what.

Along with this design, the workflows of course differ in how they are utilized by the business/user. As through workflow one the combined prompt handed to the model, along with the most recent request from the user, leads to a produced reply or advice message by the model. Offering an alternative replacement of the need for the user to construct their own reply to the customer.

However, through the second design, no final output is ever produced. This workflow is instead design to primarily offer information and advice for the applications user, through requested refined internal business information, or personalized advice on how to respond to the current specific customer enquiry.

## Data sanitisation

The data sanitisation that has been mentioned throughout this project's documentation is handled by mircosoft’s presidio library, which is used to automatically detect and redact personally identifiable information from given text segments.

Presidio was recommended to me as a solution to establishing the reliable sanitation of customer conversations. Instead of just relying solely on user review, through the use of presidio information can be automatically redacted. This is achieved through a two stage process.

First the `presidio_analyzer` class is used to scan the initial text using regex pattern matching, to identify various types of personally identifiable information, such as names, phone numbers, email addresses and regional postal codes. This is done in combination with the use of spacy’s natural language processing model, which is used to identify contextual entities that would be missed by regex patterns alone. Allowing the system to detect unstructured information.

Whilst regex patterns are indeed reliable at detecting structured personally identifiable information, unstructured information, such as an address written within a sentence, would not be caught, as context is required to identify it. Spacy’s natural language processing model complements regex by identifying the contextual entities, classifying the type of information using tags such as  “location”, "address". Whilst also noting their position within the text for the next step.

In the second stage, the `presidio_anonymizer` uses the results to redact this identified information from the original text. Replacing the targeted text with placeholder tags rather than removing it entirely. This tag will note the type of the information that existed at that location. Each placeholder identifies the type of information originally existing within that location.

Displaying to the user exactly where the information has been redacted from, when manually reviewing the sanitised text later on. These tags are also vital for when the sanitised text is passed to the local ai model as part of the prompt. Allowing the model to understand the structure of the conversation without receiving the original text.

Presidio and spacy run entirely locally, processing all text within the local machine without making any external calls. Ensuring that no customer conversational data ever leaves the device, during this process, avoiding the introduction of unnecessary security risks.

## Database 

Sqlite was the choice for my local authentication database. This engine choice and the reasoning behind it is all covered within the database design section of `design.md`.

