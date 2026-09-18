# Readme

# Ebay messaging gateway

Cs50 final project, written by yanezreed

# Video demo link
…

## Overview

This project contains a desktop application, developed as an internal tool for a local ecommerce business, specializing in the sale of custom guitar parts.

The aim of this application is to assist its staff in their work to respond to an ever increasing amount of customer enquiries within their business accounts ebay messaging platform.

To achieve this my application employs two separate workflows, each designed to assist staff while remaining compliant with ebays developer terms and conditions, in addition to data protection laws.

The reasoning behind this decision to offer a dual workflow approach, and the supporting research that went into this decision, is covered both within the sections below and in my supporting documentation.

Note, that this project has been developed specifically as a cs50 final project at this point, and is in no way intended for commercial use.

## Application design

### Application start/design note

On initially opening this application, the user is first presented with a “start” button which, when clicked, opens up the login screen.

Many of the separate windows within this application have been designed to disappear once their part within the workflow has been completed. As my application has been designed to promote a straightforward step by step process, in an attempt to keep the applications workflow as user friendly as possible.

Developed using the user interface framework of pyside6, this application also offers an extremely simplistic layout, which should land extremely well with less technically astute staff members at possible future businesses.

### Login

Once at the login window, the user is then able to sign into their existing account or create a new one. This is achieved by inputting a username, password and confirmed password into the displayed fields.

The username and password of this account are collected and stored by my program, within my local sqlite database. Secured using the `pbkdf2-hmac-sha256` function, which for an in depth breakdown of this function and the security decision made around it, please see my `security.md` file.

 ### Linking a user ebay account

After the login process has been successful, the user is then prompted to connect their ebay account they intend to reply to customers from. This could be a business ebay account or an individual, it does not matter.

This connection between an ebay account and my desktop application is facilitated through the use of the oauth authentication process. Which is a framework designed to allow applications such as this one, to be granted permission to act on behalf of a user, without the need to share any of the connected accounts credentials.

This process of obtaining the permission to communicate with ebays api points and access the users conversational and messaging data is covered in immense detail within my documentation, so please if interested, read my `ebay_intergration.md` file.

In short, through ebays oauth 2.0 process, and my separately hosted flask server, the users browser is opened and redirected to the ebay login page. Where the user, completely separately from my application, is able to sign into their ebay account to grant the request permissions.

Once this process has been completed, my application will have received the required token data to authenticate communication with ebays api endpoints. 

Enabling my desktop application to send customer replies and collect the connected accounts conversations threads to be displayed within both of my workflows main dialogs.

## Workflow selection

Once authenticated, the application then presents the user with the option to select either of my two available workflows, alongside a brief explanation of what each one offers.

This workflow selection, carried out by the user, determines the tools and processes made available throughout the rest of the session.

### Workflow one

The first of the two workflows, offers assistance to the user when responding to an existing customer conversation within the connected ebay account.

Once logged in and authenticated, this application retrieves the active customer conversations, for the connected ebay account, through ebays api. Displaying the conversations within the main interface of this application.

These conversations can be viewed within a qwidget list, with each of the items displaying the associated customer username, a preview of their latest message to the user, and the item involved with the conversation.

By selecting a conversation from this list, the corresponding messages thread is then loaded within the right side panel of the interface, with the conversation list still remaining on the left. The messages displayed are separated according to the sender, with the messages sent from the users ebay account aligned to the right hand side, and the customer messages on the left. Each of these messages are also labelled with the senders username, and are padded above and below to improve the readability of the conversation.

Below the widget containing the message thread, on the right hand side of the window, there is a reply input area. Here a reply can be typed out by the user, edited, and sent to the current customer conversation selected. 

### Sanitisation and review

Before any of the customers conversational data can be passed to the local ai model, 
due to the restrictions implemented on my application through ebays developer licence agreement, it must first be sanitised within my application. This is because the processing of any personally identifiable information collected through the api, would cause a direct violation of the agreement.

Consequently my application incorporates microsofts presidio library, along with spacys natural language processing model, to automatically detect and redact any sensitive information found within the individual conversations transferred to my application. Note, this entire process is covered in my accompanying `ebay_integration.md` file.

As an extra safeguard, mandatory manual user review of the sanitised conversation is enforced before progressing in the workflow. 

With the user being presented with the sanitised conversation within a dedicated review dialog, with the option to further edit the text to ensure that any possible remaining sensitive content is removed. The user in this dialog can also improve the context the conversation offers, adding back any information that the presidio library might have wrongfully removed.

The “generate” button remains disabled until this entire process has been completed, and the user has explicitly confirmed that no personally identifiable information will be sent to the local ai model, through the now sanitised conversation.

### Ai generation

Once the sanitisation and review process is completed, the application then builds a prompt for the local ai model to process.

This prompt combines the sanitised conversation, internal business information imported from `business_info.txt` and any additional instructions the user has chosen to include.

The combined prompt is then sent to the local llama 3.1 8b model, through the use of ollama. Which is a program that enables large language models to be run entirely within a local machine, with importantly, no data leaving the device.

The generation window itself contains a read only chat box displaying the conversation with the local model, and positioned underneath lies two text input widgets. The first is used for any additional instructions the user wishes to send to the model, while the second will contain the suggested reply for the customer.

From this generation window, the user can continue to improve the reply by adding further  instructions, or asking the model follow up questions related to the internal business it has provided to it. Such as delivery policies or item specific details unique to the business.

### Reply

Once satisfactory, this edited response can then be sent as a reply to the customer, through the main window of the application. Or additionally the user can make any final edits to the reply using the tools available. As the window contains the standard text editing tools of undo, redo, cut, copy, paste, select all, and clear.

The reply itself is sent through a http post request to ebays messaging api endpoint, and this entire process is automated through a click of the “send” button. And for an in depth explanation of how this process, and other http requests made throughout the applications workflows, please see my `ebay_intergration.md` file.

Note, both the conversation list, as well as the displayed message thread, are updated automatically once a reply has been sent.

## Workflow two

The second of my two workflows also gives the user again access to the same local ai model, but importantly, without the inclusion of any sensitive customer data within the given prompt.

Once the user selects this option within the workflow selection screen, and has successfully connected their ebay account, they are again taken to the main window of my application. Similarly to the first workflow, this window displays both the conversation list and its associated message thread, and also includes the text input widget.

On clicking the “support” button however, instead of being taken through the process of sanitising and reviewing the selected conversation, they are instead taken directly to the window providing access to the local ai model.

On arrival, the user is reminded that no personally identifiable customer information should ever be included within any text sent to the model, and is then able to freely chat with the model.

Designed as a hard compliant alternative to the first workflow, in the case of possible future alterations to ebays terms and conditions. This workflow instead offers a way for this application to continue to assist the user without the requirement of customer data, sanitised or not, to be processed by an ai model.

As the user can simply enter questions or requests into the chat window, which are combined with the previous messages within the chat, along with the business information, to supply the local llama model with the context required to produce a helpful response.

Note that no customer data is involved, at any point within this workflow. Ensuring that it stays fully compliant regardless of future changes in ebays platform restrictions.

Do note that no customer data is included within the prompts passed to the ai model through this workflow. Allowing this alternative to provide the user with a way to ask questions about topics such as delivery information, or unique product details. While also remaining compliant focused, through the clear separation of the customer information displayed in the main window, and the assisted support functionality offered by the local ai.

## Ebay compliance

Mentioned above in both workflow sections, one significant consideration made throughout the development of this project,was balancing the applications ability to offer high quality generated replies with remaining compliant in its use of the customer data. Retrieved through the use of ebays api endpoints.

Documented in detail within my `design.md` and `ebay_intergration.md` files, the actual original design of this application included the use of a fine tuned model trained using historical business/customer conversations.

However, on review of ebays developer program license agreement, it became clear that this approach would cause a direct violation. As the use of any customer data to train large language models or algorithms is explicitly prohibited by the agreement, sanitised or not.

This, as discussed in my design documentation, caused a complete redesign of this project and an abandonment of the large language model training approach, to be replaced by an prompt driven alternative.

As rather than training a model, the application instead supplies the now local ai with the information and context required through the prompt itself. To produce replies based on sanitised customer conversation data, internal business information and specific fine tuned instructions provided by the business, regarding aspects such as reply wording and tone.

Additionally this dual workflow design offers the business support devoid of any processing of customer data retrieved from ebays api. Meaning that if ebay were to tighten their restrictions regarding prompt based processing in the future, my application would still provide meaningful support through a workflow that instead offers guidance and access to internal business information.

As while the current approach of my projects first workflow, which includes sanitised customer conversations within the prompts, is not currently restricted by ebays agreement. It was imperative that this application needs to offer value regardless of how the agreement changes.

Note that, the full reasoning behind all of the decisions of the design of this application, can be found within my supporting docs.

## Documentation

Given the sheer complexity of the final version of this project, a set of supporting documentation files have been included within this repository. As rather than cramming everything into the readme, each file instead contains an in depth level of detail  related to different areas of my applications development.

Below, each file is named and includes a quick summary of what it contains, including some of the section titles contained within each.

## Design.md

This file covers exactly how my application has been structured, and how the decisions made throughout have led to the final version.

The primary focus of this document surrounds my original three layered structure of this project, what each of these layers were responsible for, and where the separation between these layers unavoidably broke down as the project progressed, due to the nature of the pyside6 framework.

Also covered is the local database design and query building involved, as well as the reasoning behind the dual workflow structure discussed within this readme. 
## Ebay_intergration.md
My ebay integration document covers all related topics to my applications communication with ebay. 

This includes the start to finish oauth authentication process, a detailed explanation of all api endpoints used to send and receive data from ebay, how the data received was handled and processed and how the compliance considerations made throughout both my applications workflows helped to ensure they remained compliant to ebays restrictions.

And lastly, a full breakdown of the oauth authentication process throughout the `oauth_start.py` file, as well as my `server.py` and `ebay_client.py` files.

## Security.md

Covered within this file are all of my security related considerations throughout the entire development process and within the final version of my application.

This includes how my project securely handles the oauth tokens sent to my external render server, how customer conversations are held only within the current session, and how the local database holding user accounts has been built. Also included is an explanation on why certain credentials were intentionally left out of the source code, using environment variables within the render server.

## Testing.md

This file covers how my application was manually tested throughout the development, including how each specific layer was tested separately, and how the limitations of oauth process were discovered and dealt with. 

It also includes an explanation of all the bugs found during development and the resulting solutions implemented to address them. 

## Technology.md

This file covers all technology choices made throughout the project. Including the reasoning behind each choice, as well as the possible alternatives considered.

Here is a quick list of all the technologies covered in this document that are present within my application and external server.

## Technology choices

Python
Pyside6 ui framework
Oauth 2.0 authentication
Flask, used to develop my external server
Render, which hosts my flask server
Llama 3.1 8b
Olama, which enables the local ai model
Microsoft presidio library
Spacy natural language model
Sqlite, relational local database
Ebay messaging api
