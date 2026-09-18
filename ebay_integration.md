# Ebay integration

## Introduction

This document explains how my application communicates with ebay's external api. 

It covers how the user of this application initially authorises their ebay account to be accessed via the api, how customer conversations and message data is retrieved, and how this data is processed and displayed within the application while remaining compliant to ebays terms and conditions.

Finally, this document provides an in depth look of the oauth 2.0 authorisation process, covering each stage of its implementation within this system. Including the roles of the external render hosted server and the desktop application in transferring token data and enabling communication directly with ebay.

## Ebay developer license

As a developer, before being allowed access to ebay’s api, it is necessary that you must first signup to an ebay developer account. This account must be approved by ebay, which involves the company reviewing both my details as an individual, and the intent of the application that will use the api. Part of this process includes an acceptance to follow the ebay developer program license agreement.

This signed agreement places strict restrictions on how data can be stored, or processed within the application. If these requirements are not adhered to, it will result in api access for the developer account being revoked.

"use, store, copy, modify, distribute, or process User Data (including transaction information, user messages, or personal data) for the purpose of training, retraining, or improving any artificial intelligence or machine-learning model." 

This restriction above significantly impacted the design of my project, resulting in a complete redesign during the earlier stages of development. As it influenced not only how the customer data was handled, but also how ai was used/implemented within my system.

My original design intention was to fine tune a mistral 7b ai model using historical customer conversations, critically retrieved through the api. After discovering that this approach would violate the ebay developer agreement, it became clear that this design was not suitable, even if the data being used had first been anonymised.

This pivot led to the introduction of a dual workflow design for the application. Where both workflows would provide ai assistance, without using any data retrieved through the api to train the model, anonymised or not.

For a full detailed explanation of both workflows, and how they each adhere to the compliance requirements, please see the document `design.md`. In addition, the specific considerations for each workflow’s compliance can be found within this document's data handling section.

## Environmental variables 

My flask server retrieves its configuration on startup, using `os.environ.get`, which reads the value of an environment variable, by name. These values are then retrieved by my flask server at runtime and are stored within the set variables within `server.py`.

This approach is used as an alternative to storing any sensitive details directly within my program’s source code, which will be accessible through my github repository. Values such as `client_id` and `client_secret` are instead stored as render’s environment variables.

By storing all sensitive credentials separate from my publicly accessible application source code, they are never included within the project's current or previous github commits. Allowing my applications code to remain publicly accessible still, while keeping sensitive credentials out.

Note, that these variables are made accessible to `os.environ.get` through render’s dashboard and anyone deploying their own instance of this server will need to input these environmental variables themselves, using their own ebay api credentials.

Lastly, this is a straightforward one time setup process, and because this project is not meant for public deployment, no guide will be created to encourage third party usage. As encouraging external third party deployment could incur violations of ebay's developer licence agreement.

## Api scope
One of the environment variables used by my flask server is called `api_scope`. Unlike `client_id` or the `client_secret` mentioned above, this value is not sensitive in nature, due to it simply identifying a requested permission rather than containing any private credentials. And is hardcoded within the `ebay_client.py` with no issue.
Note, that unlike the credentials above, storing this value within the source code, is not exposing any sensitive information.
The scope value contains the url `https://api.ebay.com/oauth/api_scope/commerce.message` and is used by ebay to understand what level of access my application is asking for. As readable within the url, my application is requesting access to the commerce message api for the currently logged in ebay account.
One issue with the nature of this url value however, is that it is passed as a parameter within a larger url built within my `/start` route. Because it contains reserved url characters such as a forward slash or a colon, browsers will misinterpret these parts of the value and parse them incorrectly. Recognising them as parts of the url itself and not as a parameter of the `scope` value.
The solution was to alter these problematic characters by percent encoding the `api_scope` value, before it is stored as an environment variable within render’s dashboard. 
Percent encoding replaces these reserved characters with a percentage sign, followed by a two digit hexadecimal effectively representing the value that was there beforehand. Meaning that the `api_scope` value can now be inserted into the full authorisation url being sent to ebay, without altering its structure. The downside of this approach however is that if ebay’s api scope changes, this hardcoded value will need to be updated manually.
 ## Oauth authentication

To enable any of the authenticated http requests made to ebay’s api, oauth authorisation 2.0 is firstly required to be completed. A process which involves the user signing into their own personal ebay account, to authorise my application, to access to the api.

This process is carried out completely externally from my application, meaning that the user’s ebay login credentials are never held or stored within either the flask server or the desktop app. Instead ebay issues time sensitive access tokens, which are used by my application to make api requests on behalf of the user, delegating the authentication process entirely to ebay.

## Render hosted server

Because ebay’s oauth implementation requires a callback url, which must be publicly accessible, the decision was made to implement a flask server hosted on the cloud hosting platform render to receive the authorisation code. Once the user has fully completed the login process within ebay's platform, ebay itself redirects the browser to my callback url, passing an authentication code to the render server.

Once received, the render server then exchanges this authorization code for an access token from ebay. This is accomplished through the use of an http post request made to ebays token endpoint. The token data itself is then made available through the render servers `/check_token` route to my desktop application, which regularly polls this route throughout the authorisation process. 

Before the `/check_token` route returns the token data however, it uses the method `token_expired_check` to confirm the token has not expired. If it has, the token data is not returned and the desktop application will continue to poll. Otherwise the token data is returned as a json response, which is then stored locally within the file `ebay_tokens.json`.  This process will be explained in more detail later in this document.

At this point, the render servers role within the process is over, as the initial authorisation process has been completed. The desktop application now can communicate directly with ebay for as long as the locally stored access token remains valid. So the render server is used to support the oauth process and to transfer the token data to the application, but is not involved in later api requests.

## Render server windup

Render, as a cloud hosting platform, offers a free tier of service, which runs my projects external flask server. While completely cost free, the downside of the server comes in the form of a wind down process that activates after long periods of inactivity.

The first request made to the server after this period will take several seconds to process. This is because the server itself actively needs to restart before processing any incoming requests. Which caused me some design issues, as requests made to the server in this state would automatically fail. Causing me a design headache as the oauth process needed to account for this start up delay.

## Windup solution

The route `/start` within `server.py` will always be the initial route requested at the start of the authorisation process.

When the user begins oauth authorisation, the desktop application starts the process by passing the url of my render servers `/start` route to the method `webbrowser.open`. This opens the url within the users own web browser, sending a http get request to the address. If the render server at this point is not active, then this initial request will cause the service to restart and wind up. Once the server is ready, this route then redirects the user to the ebay login page. 

Within testing, it became apparent that this wind up process would result in around a fifteen second wait for the user before the login page becomes available.

This start up delay consequently occurs before the user begins the authorisation process within ebays login page. Which is important as the server must be readily available to receive ebays later redirect to the `callback` route.

To account fot delays during this process, polling from my application begins once the browser has been opened using `webbrowser.open`. The polling process, while separate from the initial start request, repeatedly checks the `/check_token` route until valid token data becomes available.

This allows time for the user to approve access, for ebay to return an authorization code, and for my render server to complete the token exchange process. 

This is done instead of the alternative, where the process would rely on a single check to the `/check_token` at a point when the valid token data may not yet be available.

While the user is completing the authentication process, my desktop application sends a request every two seconds to my flask server, for a total of thirty attempts. If the server is still in the process of restarting, valid token data may not be available through the `/check_token` route. Or if the user simply hasn't completed the logging in process, then no valid token data will yet be available within the server. 

In either situation, requests will continue to be made to this route until the attempt limit has been reached or valid token data becomes available.

If a valid token data is found, the `/check_token` route then returns it to the desktop in the form of a json response. Where it will be stored locally within the file `ebay_tokens.json` by the desktop application. And if the attempt limit is reached with no success, the polling process stops and the authorisation attempt times out. Also the user is made aware of this through a message box on screen.

## Oauth workflow

Within this section, the three separate files that make up the oauth process will be covered in detail. Each of these files contributes to the authorisation process directly, each with their own distinct responsibility.

The first file, `oauth_start.py` is responsible for initiating the workflow, by opening the users browser to the render servers `/start` route via http get request, and polling for a result. The second file `server.py` contains all of the render hosted flask servers routes, that construct the authorisation request, receive the callback from ebay, and then exchange the given authorisation code for actual access token data.

The third file, `ebay_client.py` provides methods to save the token data locally, and run checks to discover if it is indeed valid or not. These methods are used both by the render hosted flask server, and my desktop application. Note, it also holds the current code to close the program in the case of a invalid token, as the refreshing functionality of my design is not yet up and running. This restart is required approximately every two hours, as that is the current lifespan of the tokens my application has received in testing.

The sections below contain a more detailed explanation of the role of each of these files, within both my desktop application, and the external render hosted flask server.

## Desktop application, oauth_start.py

The file `oauth_start.py` is responsible for managing the oauth process from the desktop application’s side.

This file's responsibility is to coordinate communication between my desktop application and the render hosted server throughout the oauth process. 

When the user chooses to connect their live ebay account, this file is in charge of opening the user’s browser, displaying the updated oauth dialog to instruct the user to continue within the browser opened, and then continually checking for valid access tokens stored within the render server.

Once a valid token is received and stored within the render server, it is then detected through the polling process, and retrieved by the application. The token is then saved locally, and the desktop application is notified that the authorisation process is complete. 

### Initialization

On initialization a `qtimer` object is created, and connected with the `request_server` method through the pyside6 signal and slot system. The specific signal that triggers this connection is the `qtimer` unique `timeout` signal, which is emitted at a set interval once the timer is started by the program.

### Process

The first method within the workflow is called `start_oauth`, not to be confused with the name of the file `oauth_start.py`.

This method is triggered by the user, when the connect ebay account” button is clicked within the desktop applications ui. Once called, this method opens the user’s default browser to the render’s server `/start` endpoint. The `qdialog` is then updated to display instructions for the user to complete the ebay login process within the just opened browser.

Meanwhile, the `qtimer` object is activated, emitting a `timeout` signal every two seconds. Each of these emissions from this `qtimer` calls the method `request_server`.

This method `request_server` then increments the variable `connect_attempts` each time it is called. 

This variable `connect_attempts` is initialized when the dialog is created, and then later set to zero within the `start_oauth` method instead of within the initiation of the class. Ensuring that on each authentication attempt, this counter is set to zero, as multiple connection attempts may occur within the same session. 

If the `connect_attempts` variable exceeds thirty counts, the waiting `qdialog` is closed and the user is informed visually, via a `qmessagebox`, that the process has timed out and failed.

However if the limit has not been reached, a get request is made to the renders server’s `/check_token` endpoint. If this request returns a response of anything other than a `200` status code, the method returns and waits for the next call.

Note that this next call will come in the form of a timer event, signalled by the `qtimer` object when it emits its next `timeout` signal.

If a `200` response is received, this indicates that a valid access token is stored within the flask render hosted server. This access token is then extracted from the json response to my desktop application, and is then saved locally through the use of `save_tokens` which is a method provided by `ebay_client.py`.

On success, the `qtimer` is stopped, the oauth dialog is closed and an `accept` value is returned. Signaling that the process has completed successfully, and allowing the login workflow can continue.

If at any point the user clicks the “cancel” button in the dialogs ui, `cancel_process` is called. This method stops the `qtimer` and returns `rejected` instead. The user is then returned to the login screen without completing authorisation.

## Render hosted flask server, server.py

This file `server.py` contains the external flask server hosted on render. The responsibility of this server is to receive the authorization code after the user has authenticated themselves within the ebay login webpage. 

It reads the code from the callback request and exchanges it for token data from ebay. The returned token response is then saved server side within `ebay_tokens.json`. Making the token data readily available through the `/check_token` route, enabling the application to retrieve the essentials fields within this data, through its polling requests, to store them locally for later use within ebay api requests.

### Route, /start

The `/start` route builds the ebay oauth authorisation url needed to redirect the user’s browser to the ebay login page where they can login into their personal account.

Here are the four values are combined to create a query string, which is part of the url -> `https://auth.ebay.com/oauth2/authorize`;

`client_id` is used to identify the application within ebays system
`response_type` holds the set value `code`, which indicates that my application is requesting the authorization code from ebay, and not the token directly
`redirect_uri` holds the `runame` value assigned to my application, used by ebay to identify my callback ur within their system
`scope` defines the level of access my application is requesting. Which is set to the messaging scope only, allowing access only to messaging api

Note, scope within ebays api once requested can be accessed at a lower security level but never higher. Meaning that the access token provided, can only be used for the operations permitted, and can’t provide broader access. This is documented within ebay's api terms.

As already covered, opening `/start` may possibly wake the inactive render server, so the browser may take around fifteen seconds to display the ebay authentication login page to the user. 

### Route, /callback

This is the route that was created to receive the authorization code returned by ebay's api, after the user has completed the authentication process within the platform. This code is passed to my render hosted flask server by a http request to the callback url, attached to the url as a query parameter, that can be seen as a key value pair after the `?` in the url.

Gunicorn, which is the program that allows my flask application to run as a web server within render, receives the incoming http request first, and then hands the request off to my flask application, which runs the matching `/callback` route.

Flask then automatically parses the query string of an incoming http request, storing each query parameter as a key value pair within `request.args`. This is how the authorisation code is accessed.

If there is no authorisation code within the url, a four hundred status code is returned. Which is an unlikely error to occur, but is protected against none the less.

The server now with access to the authorisation code within the args, exchanges the code for an access token, through another http post request made this time to ebays api. This request includes several values.

`grant_type` set to `authorization_code` informs ebays api that this is an initial code exchange request and not a refresh request for a invalid token
`code` which contains the authorisation code received from ebays api
`redirect_uri` holds the `runame` value assigned to my application, used by ebay to identify my callback ur within their system
`auth` passed to my `requests` library, containing `client_id` and `client_secret`


Http basic authorisation, is a standard method of identifying a specific application to a server. 

The `requests’ library allows me to pass these two values in `client_id` and `client_secret` through the `auth` parameter. That then combines the two values, formats them and then encodes them for http basic authentication. Note, a full explanation of this can be found within my `technology.md` doc.

The encoded result is then placed within the http `authorization` header, in the format `Basic …`. As this is the format expected by ebay, and noted in their documentation. Allowing ebay to verify the identity of my application, through the credentials given.

If this http request is accepted by ebay's api, a `200` status code is sent back to my application, along with the token data requested. 

The token response is then saved server side through the user of my `save_tokens` method from `ebay_client.py`. 

After the token response has been saved, my `/callback` route returns some html to the web browser.

This html displays text confirming that the authorisation process had been completed, and that the user can now close that webpage.

### Route, /check_token

This route is polled by my desktop application throughout the oauth authorisation process. Using the method `request_server` within `oauth_start.py`, which determines whether the flask server currently stores a valid access token following the user’s successful ebay login.

When the `check_token` route is called, data is loaded from the server side json file `ebay_tokens.json`, using the method `load_tokens`, which again is another instance of an imported method from `ebay_client.py`, which will be covered in the next section.

If no data exists within `ebay_tokens.json`, or the access token stored is found to be expired, this route returns the `202 accepted` status code, which indicates to my application that the token data is not available yet and the polling should continue.

This check for the validity of the token is carried out by the method `token_expired_check`, also imported from `ebay_client.py`. 

If a valid access token is found to be stored within the server, the route constructs and returns a python dictionary containing the vital values `access_token`, `expires_in` and `received_at`.

Flask automatically recognises this dictionary returned by the route, converting it to json within the body of a http response. This is sent back to the desktop application in response to the current polling request.

The rest of the server side data is excluded. Including the `refresh_token` which is not yet transferred to my application in the current version.

This response to the original http get request to `/check_token` will then be decoded from json to a python dictionary, importantly containing the `access_token` value.The desktop application then saves the token locally using `save_tokens`.

Other important values returned in the response include; `expires_in` which is how long the token is actually valid for in seconds, and `received_at` which is a timestamp of when the token was saved.

## Token management, ebay_client.py

This file provides key functionality for both my flask server and desktop application, in the form of accessible methods for token management, including saving and checking the token data. Two key examples of these methods, discussed above, are `save_tokens` and `token_expired_check`.

### Method, save_tokens

The `save_tokens` function is called by my flask server’s `/callback` route. After exchanging the authorization code for an access token, through a post request made to ebay's token endpoint, the response received from ebay is then passed to the `save_tokens` method. Which then writes the token to `ebay_tokens.json` on the render server.

This method is also called by the `oauth_start.py` method `request_server`. Once polling from my desktop application detects a valid token stored on the render server, the data returned from the get request to `/check_token` is then passed to `save_tokens`. Note, this time within the desktop application’s local storage and not the external server.

In both cases, `save_tokens` also adds a timestamp to the token data, as a python dictionary, before writing it to either the server or application. Under the key `received_at`, with the value expressed as the number of seconds since nineteen seventy, recording the exact time the token was saved within my application or flask server.

It is worth noting that this value will be overwritten when the token is saved again within the desktop application, after initially being stored on the flask server. The solution to this slight discrepancy in the `received_at` value, comes in the form of a buffer, explained in the method below.

### Method, token_expired_check

The function `token_expired_check` is called by the flask servers `/check_token` route. As well as within the desktops own token checks. It is used to determine if the stored access token is valid, and has not reached its expiry time, before it is used within the application.

The two values `expires_in` and `received_at` are taken from the stored token data in question. The `expires_in` value representing the total lifespan in seconds of the token, provided by ebay. And `received_at`, which is the timestamp added by the above `save_tokens`.

By adding these values together, the method is able to calculate the time in seconds, in which the token will expire. This resulting expiry time can then be used to compare against the current time, which can be retrieved by python's `time` function. Again returning the number of seconds elapsed since the unix epoch. If the current time is greater than the expiry time, this method will return a true value, indicating that the access token has expired.

Note that a thirty second buffer is subtracted from the calculated expiry time before any comparison is made. Providing a margin of safety, accounting for the delay between the token received on the render server, transferred to the desktop application and then finally used to authenticate an api request. Also compensating for the slight difference in the `received_at` timestamp caused as the token is saved twice.

By introducing this buffer, tokens that are close to expiring are treated as expired. Through this approach the risk of a token expiring while the api request is in progress, is massively reduced. 

## Oauth summary

The user presses the “connect ebay account” button, within the ui
The `start_oauth` method opens a browser to the flask servers `/start` endpoint
Pyside6 `qtimer` now starts to call the `request_server` method every two seconds
A short delay occurs as the server awakens
This `/start` route builds the ebay oauth url, redirecting the browser to it
The user authenticates with ebay within the login page
Ebay redirects the browser to `/callback` with the authorization code in the url
My `/callback` route exchanges the authorisation code with eBay's token endpoint
Returned token data is then saved on the render hosted flask server , via `save_tokens`
Polling then detects a valid token on the next `/check_token` request
The `save_tokens` method is then used within the desktop application
The `request_server` method then ends the `qtimer` and accepts the oauth dialog

At this stage my application now has a valid access token automatically included within the authorisation header of requests made to ebays api.

## Planned automatic token refresh

Once the initial oauth flow is completed, my desktop application now holds both the access token and its expiry details.

However, currently `/check_token` does not transfer the `refresh_token` from the render server to the application. This will be implemented later down the line.

When the initial access token does expire, detected by the `token_expired_check` method before an api request is made, a warning is displayed and the user is required to restart the application to reauthorise their ebay account once again.

In the planned implementation, the refresh request made by the `refresh_access_token` method will be sent to `https://api.ebay.com/identity/v1/oauth2/token` which is exactly the same ebay api endpoint communicated with in the initial oauth flow. However, the difference is the `grant_type` form parameter, which will be set to `refresh_token` instead of `authorization_code`.

The new token data returned will then be saved locally, again using the function `save_tokens` which will overwrite the previous token data saved within `ebay_tokens.json`. As a result the subsequent token refresh could then be handled by `ebay_client.py` within the desktop application.

## Api endpoints

Once my application has access to valid tokens, which are stored locally within the desktop application, authenticated communication can now be had directly with ebay's api. Through http requests made to the following endpoints below, which are all handled within my file `ebay_client.py`.

### First endpoint, get /commerce/message/v1/conversation

The `get /commerce/message/v1/conversation` endpoint, is used to retrieve customer conversations for my application, and is called by the `get_conversations` function within `ebay_client.py`.

My application requests up to thirty five conversations at a time, using the parameter value `conversation_type = from_members`. Asking ebay to return conversations from the corresponding ebay account, involving only active buyers and ebay members. Filtering out any spam messages sent from ebay itself.

The `sort` parameter is also included, which ensures that the conversations returned are delivered in order of date. Specifically in descending order, `sort = date_desc`, so that the most recently active conversation is returned at the top of the `.json` response. Allowing my application to then display the newest customer enquiries at the top of the conversation list, within the user interface, without needing to sort the data within my program.

Thirty five conversations, for an application this size, are currently more than enough to cover the volume of active customer conversations this application was built for. And if the volume of customer conversations grows in the future, this hardcoded limit can easily be increased. Done so through the `limit` value within the requested parameters.

If ebay returns a successful `200` response to the request, the http response body will contain json data, which will need to first be converted to a pythonic dictionary before the data can be processed.

The resulting dictionary contains a list under the key `conversations`. This `conversations` list holds a separate dictionary for each of the conversations returned to my application.

Each of these separate dictionary objects represents a specific conversation, and includes a `conversation_id` and a `latest_message`.

My `get_conversations` function extracts this list of dictionary objects, and returns it to `chat_widget.py` where it is looped through to obtain each conversation and its information from the list.

The sender of the `lastest_message` is discovered by comparing the username to the users ebay account authenticated to my application. Useful as this determines which username belongs to the customer.

A separate qlist wiget is created for each conversation, within the applications `qlistwidget` displaying the most recent conversations received on the linked ebay account, as a list within my application. Along with the information of the customers username, the latest message and the item referenced in the conversation.

### Second endpoint, get /commerce/message/v1/conversation/{conversation_id}

My second endpoint `get /commerce/message/v1/conversation/{conversation_id}` is called by `get_conversation_messages` within the `ebay_client.py` file.

This method is used to retrieve the full message thread for a specific conversation.

The `conversation_id` value from each response object, returned through the use of the first endpoint, is initially converted into a string and then stored to its corresponding `qlistwidget` item within the list, again through the use of the `qt.userrole` system.

When the user now selects a conversation, this now stored `conversation_id` is fetched from the selected item and passed into the endpoint url.

Pyside6’s signal and slot system makes this an incredibly easy process. As to retrieve the correct `conversation_id` from the specific conversation selected, all that is needed to be done is to set up the `itemclicked` signal on the `qlistwidget` which is again what contains all the conversation items.

When triggered, by the user clicking on one of the individual conversation items within the list, the `itemclicked` signal is emitted and the method `select_conversation` is executed, with the selected `qlistwidget` item passed as an argument.

The `select_conversation` method then retrieves the `conversation_id` from the item, stored within, through again the `qt.userrole` system.

This is ideal, as the customer identity/username does not need to be used as the identifier for the specific conversation selected by the user. As it is very possible that the same account or customer within ebay is messaging the business more than once, concerning different items, or enquiring about two separate things. 

Instead, because each item within the `qlistwidget` contains a unique `conversation_id` corresponding with each conversation, this acts as the unique identifier for this design. Once the correct `conversation_id` is found, it is passed to the `get_conversation_messages` method. 

This method utilizes the  `conversation_type = from_members` parameter, within a get request to ebays conversation endpoint, with the constructed url shown above. Containing the selected `conversation_id` value.

If ebay returns a `200` status code response to this request, the current json response body is converted to a python dictionary, via the use of the `api_responce.json` method.

This conversion takes place whenever my application receives data from ebays api, and is required before this data can be processed using python within my program.

Once the data is stored pythonically, the list contained within the response dictionary is found through the `messages` key. And is extracted through the use of the `.get` method.

This `.get` method uses the `messages` key to locate and return the dictionary data stored as the corresponding value, while also using an empty list as a default value to return in the case where this key can not be found.

Within the returned `messages` list, is a series of dictionaries, each representing an individual message from the customer or user.

Inside each of these dictionaries representing the messages within the larger returned conversation, are the keys `message_body` and `sender_username` both with their paired values.

The actual message string is the value attached to the `message_body` key, and the `sender_username` is of course the username of the one who sent the message.

Using the `sender_username` value, the application when building the conversation, within the `qtextedit` in the `chat_widget.py` file. As the stored ebay account username of the authenticated user of this application, within `config.py`,  is compared against the senders username. This is done to determine how to label the message within the list as well as how to align the message within the display.

All messages within the read only `qtextedit` are labeled either “you” or “customer” and are aligned left or right respectively.

### Third endpoint, post /commerce/message/v1/send_message 

This third endpoint enables my application to send the replies created to specific conversations through the use of the `send_message` method, which is imported from the `ebay_client.py` file.

This method requires the `conversation_id` of the currently selected conversation within the user interface of `chat_widget.py` talked about above. Passed as an argument alongside the actual text written reply the user intends to send. However the `conversation_id` is not required within the endpoint url this time.

Instead the endpoint requires a python dictionary to be constructed, containing both a `conversation_id` and the text reply, this time under the key `message_text` instead of `message_body` which is how the message text was received.

So effectively a dictionary is created, in a similar fashion to how the was received from ebay within the second endpoint response.

This dictionary is required to be converted to json to allow it to be transferred successfully within a http post request, as this is what ebays endpoint expects within the http post request body. Note, all of these details are explained within ebays documentation, which can be found within the developer section of their website.

To convert the data, the dictionary is then attached to the post request and through the use of the `json` argument within the post request, `json = data` the requests library automatically converts this value to json data before it is placed within the body of the request.

Once the post request is sent, the http static code is checked for a `200` or `201` response, if successful this check will return true. Any other status code returned will result in a runtime error being raised along with an error message for the user.

## Data handling

### Data storage

Importantly, within the workflow selection window, my application informs the user that it will not persistently store the contents of customer conversations, accessed through the use of ebays api.

Customer conversations that are retrieved and displayed to the user through the ui, are always only held in memory during the current session and are discarded entirely from memory once the session ends. Meaning this sensitive data cannot persist between sessions, to support compliance with ebays data handling requirements.

As ebays developer agreement explicitly allows copies of the content where necessary, but states it requires developers to ensure this data is deleted once there it is no longer required for its original purpose.

Hence it was a deliberate design decision on my part to avoid storing the retrieved customer conversations to disk, even temporarily, as keeping everything session based would reduce unnecessary retention.

### Sanitisation

Before any customer data can possibly be passed to the local ai model within workflow one, the data in question must first be sanitised. This is done using the method `sanitise_text` within the file `user_class.py`.

The sanitization process automatically detects personally identifiable information within the text passed to the method, through the use of microsoft's presidio library. These identified areas of text are then redacted through the use of the same library, replacing the sensitive content with placeholder tags. Rather than omitting the content entirely, as both the user and the ai model need to understand clearly where these redactions have taken place after review.

As this automatic detection will never actually guarantee that all personally identifiable information will always be detected within the text, the resulting conversation returned from `sanitise_text` will be reviewed manually by the user before this information continues to progress through the workflow.

The manual review itself is enforced by the ui, as within `generate_dialog.py` the generation button itself is intentionally disabled until sanitization of the text has been completed, and confirmation has been given that the text has been manually reviewed by the user.

If the text has not been effectively sanitised by my application, the review can be canceled by the user, leaving the generation button disabled.

From this point, the user can choose to manually sanitise the text through editing out the personally identifying information within the text. Or alternatively the user can once again click the sanitise button to re attempt the process.

Meaning that through the unaltered use of my first workflow, the application will prevent unauthorized conversations passing directly to the local ai.

## Compliance

As ebays developer program license agreement does prohibit the training of ai models with the use of ebay content, such as customer personal information. My application has been designed to specifically avoid the training, or improvement, of ai models. Opting for an alternative prompt based approach instead.

Allowing the local model to use the information supplied to it through a prompt, without this data ever permanently altering the state of the model. As the conversational data is never retained for future improvement.

However, within my first workflow the sanitised customer conversations are still passed to a local ai model as context for customer reply generation.

Ebays agreement does also place restrictions on how personal information, accessed through the use of ebays api endpoints, can be processed and used within an application.

Consequently, although my workflow one has been designed with both sanitization and mandatory user review as safeguards, formal clarification from ebay would be sought before this functionality was ever used within a commercial setting.

This is also exactly the reason a second alternative workflow was created, as customer conversations are retrieved through ebays api but are not automatically passed to any ai model. 

Instead, the model works using internal business information, and questions manually entered by the user. Providing a way for ai assistance to exist within my application without ever automatically exposing the model to the sensitive customer conversations displayed within the `chat_widget.py` interface.

Workflow two was also designed specifically to provide an alternative way of using the application. As if ebay was to ever introduce tighter restrictions for the use of ai with api retrieved information, because the customer conversational data is kept separate from ai processing within this workflow, the application would still be compliant. While still offering ai support to the user without relying on the first workflows use of sanitised conversations, reviewed or not.

It should also be noted that my project has been designed for my personal use. As through every stage of development, it has been designed as an application only ever to be run by myself.

With my code containing personal development notes all over as well as a series of vital hardcoded values. In addition to elements of my program which need sufficient knowledge to configure correctly, such as ebay developer sign up, callback set up within ebays website, key generation for authorisation, and render environmental variable set up.

If the application was to ever be adapted for wider use, these areas of my project would be included within an easy to follow set up guide. As well as a simplification of my code and the addition of easily editable values instead of the hardcoded ones, for example the number of conversations requested by my application from ebay.

This would allow the values currently directly defined within the code, to be changed without requiring time and effort to manually search the program and alter the values themselves.

Therefore the technical implementation of this application, and the first workflows compliance with ebays updated developer requirements would need to be reviewed before any professional deployment was to be considered.

