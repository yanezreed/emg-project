# EMG-Project

## Project Overview

This project includes a desktop application intended for internal use at Guitar Anatomy, an eBay based ecommerce business situated in the north of England. Designed with the goal of assisting staff in their response to customer queries within the eBay messaging system.
To ensure full compliance with eBay’s Developer Program License Agreement and data protection requirements, the application has two optional workflows, differing in their use of AI. Being used to either generate draft responses or to provide supporting business related information to staff during the reply process. This two way solution approach has been implemented to ensure that the application will remain usable in the event of future changes to eBay’s policies.
Due to strict data handling limitations imposed by the platform, neither workflow can possibly be fully automated. Instead, both are intentionally designed as supporting tools rather than full replacements for human decision making. The ultimate aim of each workflow is to improve consistency, tone, and efficiency of customer responses, while still requiring manual review at every stage. As it is through human involvement that this application is allowed to benefit from AI assistance, while remaining fully compliant with legal and platform requirements set by eBay.

## Key features:

- A user interface built with the philosophy of function over form, implemented using PySide6.

- An API driven system, sending and receiving data from eBay directly, secured using OAuth authentication.

- AI assistance in the form of response generation to customer queries, with all outputs being reviewed manually before being sent off.

- Separate AI workflows, designed to offer two alternative compliant solutions aligning with eBay’s platform conditions, future proofing the business against potential policy updates.

- Non storage of customer data beyond the active session, improving security, and ensuring data protection and compliance requirements are met.

## Dual Workflow Design

One major challenge in building this project was trying to maximise the level of assistance I could offer staff at the business while staying compliant to strict platform constraints. With the use of customer data for training or fine tuning AI models being strictly prohibited, I was forced into redesigning my initial approach into two solutions, both fully compliant. Further details on my decision making process and the resulting AI workflows can be found within tech-methodology.md.

…

### Workflow One

Within my first workflow, all sensitive customer data received from eBay API is processed exclusively through eBay’s internal AI on the platform. Staff simply are linked to the conversation directly, where eBays built in AI generation will highlight a reply using the conversations context.

The AI generated reply is then composed into this application, meaning that the original conversation is never accessed or stored by my program. Instead the pasted reply can then be inputted into my application, to be sanitised by my program, as an extra precaution. After removing all possible sensitive data, the text is then manually reviewed by the user and passed into a local prompt driven AI model, to enrich the response using pre-stored business information. Resulting in a finished reply in light with the preferred tone of the business and update on any company prices or unique instrument part information. This final reply is then reviewed again by the user, before being sent to the customer via API. Resulting in a process that improves staff consistency and efficiency while ensuring no customer data is ever leaked into the local AI system.
