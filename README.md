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
