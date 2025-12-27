# EMG-Project

## Project Overview

This project is a native desktop application used as an internal tool for the staff at Guitar Anatomy, an eBay based ecommerce company based in the North East of England. Whom specialise in selling specialised guitar parts.

The application itself is designed to assist staff in managing the ever increasing enquiries received through eBay’s platform messaging system. The primary goal being to reduce response times, improve consistency, accuracy, and generalize tone across all customer communications.

Initially aiming to create a fully automated program, the project's use of AI necessitated a design pivot. Constraints on the use of customer data, imposed through the eBay Developer Program License Agreement and the Data Protection Act, led me to develop an application with two optional workflows, ensuring constant user involvement and review throughout the process. Each of the workflows contains a different level of AI involvement, but both are alike in the fact that data is never stored, persisted, or used to train AI models.

Lastly, this is a project built as a portfolio piece and is in no way affiliated with eBay.

## System Overview

This application, at its core, contains three primary components; a user interface layer, an application layer, and an integration layer.

I have designed this system to keep these layers completely separated, through a modular design, with the intention of allowing each of these features to be modified or replaced without affecting the full scope of the system. Therefore, improving the ability to maintain the program long term and reducing any risk of unintended side effects. Further details about the use of modular design can be found within the `tech-methodology.md` file.

### User Interface Layer

The interface has been built purposely, using PySide6, to guarantee ease of use for staff members when navigating through the layout. Prioritizing clarity, usability, and error prevention over any sort of aesthetics. Through the user interface, the user will be able to;

- Choose one of the two optional workflows.
- Authenticate API usage by linking the desired eBay account using OAuth.
- Scroll and select a past business to customer conversation,retrieved through the API.
- Initiate the reply process.
- Click on the generated URL to access the specific conversation on eBay’s platform.
- Gather the suggested generated reply within eBay’s platform.
- Sanitize the suggested reply, ready for manual review and clearance.
- Manually input non sensitive information into the local AI model, to be enriched with business related information.

The user will also always be able to;

- Manually review/edit proposed responses at each stage of the process.
- Query the local AI model, holding only business related information, and strictly no sensitive customer data.

By guiding the user through this process rather than committing to full automation, user reviews can be utilized to avoid any violations of policy with the use of sensitive customer data.

### Application Layer

The application layer coordinates between;

- The workflow selected by the user
- Coordinating prompts and feedback from the UI components to the local AI model
- Ensuring data is passed through
- the feedback from the use of internal and external AI, and
- enforcement of user reviews

Reducing the compliance risk against sensitive data being processed through the local AI model.

...

### Integration Layer

The integration layer of my system will manage all interactions between the application itself and the many third party services being utilized primarily through eBay’s API.

That services are secured using OAuth 2.0 authentication, the recommended approach outlined by eBay, ensures that the application will only interact with the data and features intended and granted permission for.

All customer data within this layer will not be stored beyond the active session. Ensuring compliance, as no unnecessary data is also requested from the API, or persisting within my application after the process has been completed.

Through the use of the second workflow, the integration layer will adjust behaviour to further restrict API access. Minimum information, to only the message and conversational history between the customer and the business. No access to eBay’s AI model will be given.
Reducing risk of breaking platform policy, as no message content or suggested AI responses will be processed within the workflow.

## Key System Features

- PySide6 built user interface, using QtDesigner
- API based communication between application and eBay’s platform
- OAuth 2.0 authentication, for API setup and further requests
- Access to two distinct, user selected workflows
- Compliant AI assisted response generation, with enforced manual reviews
- Local prompt driven AI model, offering business related information only
- No persistent storage of sensitive customer data
- Session based data handling

## Dual Workflow Design

A key challenge in designing this project was the balance of user assistance while remaining compliant with strict platform policies and legal requirements. With the use of customer data for AI training explicitly prohibited, a fully automated system using conversational history to generate replies became unfeasible.

Instead, I pivoted to the implementation of two separate workflows. Partially automated, the workflows intentionally differ in the use of AI, both incorporating enforced manual reviews at each stage of the process. To ensure no violation of platform policies or risk for the business. Deliberately transforming the application into an assistive AI tool, rather than a core decision maker.

Described in detail below, the advantage of a two workflow solution is that I am able to maximize the use of compliant AI, while offering a zero risk alternative in case of future platform policy updates that furtherly restrict AI usage.

### Workflow Option One

Within workflow one, all sensitive customer data is processed exclusively within eBay’s platform. As due to the restrictions outlined by eBay, any use of sensitive customer data gathered through the API would constitute a violation if used to train or refine AI models, even if anonymised. Consequently, by design, the application does not process or persist/store any raw customer data for AI usage.

Staff are initially directed to the relevant conversation via the user interface, accessed through a given URL acquired through an automated API request. Here, eBay’s internal AI can generate a suggested reply using the conversational context available. With all processing and handling of sensitive customer data being performed by eBay itself. Only the generated text reply is then copied into the application, and not the original conversation. This reply, once sanitized to remove any potential sensitive information, using Pythonic libraries, is then manually reviewed by the user.

At this stage, the message can then be enriched with relevant business information within a local purposely trained AI model. Readily available within the workflow's user interface. Assisting the user with specific updated business knowledge, such as pricing, product details, or tonal guidance. Helping to increase efficiency and improve reply consistency across the entire business.

### Workflow Option Two

The second workflow is designed intentionally to be far more conservative than the first. This workflow does not access, process, store or interact with any protected sensitive customer data sent through via API. Including any sanitized content originating from eBay’s platform.

Instead this second workflow will assist the user and business through an offline, prompt driven AI model. Again preloaded with the business information, but not for the purpose of enriching a reply, but offering the information and advice needed to build the response from scratch. Providing users instant access, through prompts to the model, to private internal knowledge such as business policies, tone guidance and operating procedures.

Designed as a support tool opposed to a reply generator, this AI model does not expect to receive any customer data, and actively prompts the user to assure this before processing through a manual review. With its purpose explicitly being to help users compose and refine their responses without ever coming into contact with customer data both from and off eBay’s platform. Offering a tool to the user and the business which is overtly separated from any sensitive or regulated data, ensuring it is impervious to future restrictions imposed by eBay’s Developer Program Licence Agreement and data protection legislation.

## Workflow Decision

In an attempt not to lock the business into a single approach, which could become obsolete in the face of harsher restrictions on AI usage. I have intentionally designed this application to provide long term flexibility through this dual workflow structure. Offering staff/users an isolated support tool through the second workflow, rather than a complaint, but AI assisted enrichment in the first.
Ensuring a contrived value to the business, and consequently a use for this application, regardless of future platform or policy updates.

## Legal Disclaimer

In terms of intent for this project, the application has solely been developed as a internal tool for Guitar Anatomy. Never to be publicly released, used commercially, deployed as a production system.

Internal use will only be possible following confirmation that the system is indeed compliant with eBay’s platform policies and data handling requirements. Permission will need to be granted by both eBay, through the Developers Program, and Guitar Anatomy.

To ensure compliance, both workflows have been developed and tested within the controlled sandbox API environment provided by eBay. With the use of mock data, to guarantee that no sensitive customer data is mishandled, or processed through a local/external AI model.

## Security Considerations

With legal and data security being of the highest priority for this project, a substantial amount of effort has been taken to carefully plan and develop the application to best protect the business.

This caution is due to the sheer extensive amounts of interactions this program engages in with third party services. eBay’s API, OAuth authentication, and two AI assisted workflows are all major functional components of the system and serve as points of caution. Because of the inherent risks these components present, through a possibility of leaked or mishandled sensitive customer data.

Consequently, it was decided to employ a layered modular design strategy through development. By isolating the individual functional elements of the application, such as the application, integration, and user interface layers. All three layers’ outputs and inputs were defined clearly. Increasing the visibility of what data was received, processed, and transmitted at each stage of execution within the program.

Clear separation of responsibilities allowed for the identification of problematic behavior more easily, particularly when unexpected results were produced within an element and pasted to another. Subsequently, reducing the possibility of system flaws that could allow sensitive data to be passed to areas of my program, which could incur a leak or breach of platform policies. For example, customer data is being stored long past the current active session in the program.
