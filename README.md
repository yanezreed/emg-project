# EMG-Project

## Project Overview

This project, is a native desktop application used as an internal tool for the staff at Guitar Anatomy, an eBay based ecommerce company based in the North East of England. Whom specialise in selling specialized guitar parts.

The application itself is designed to assist staff in managing the ever increasing inquiries received through eBay’s platform messaging system. The primary goal being to reduce response times, improve consistency, accuracy, and generalize tone across all customer communications.

Initially aiming to create a fully automated program, the project's use of AI necessitated a design pivot. Constraints on the use of customer data, imposed through the eBay Developer Program License Agreement and the Data Protection Act, led me to develop an application with two optional workflows, ensuring constant user involvement and review throughout the process. Each of the workflows contains a different level of AI involvement, but both are alike in the fact that data is never stored, persisted, or used to train AI models.

Lastly, this is a project built as a portfolio piece and is in no way affiliated with eBay.

## System Overview

This application, at its core, contains three primary components; a user interface layer, an application layer, and an integration layer.

I have designed this system to keep these layers completely separated, through a modular design, with the intention of allowing each of these features to be modified or replaced without affecting the full scope of the system. Therefore, improving the ability to maintain the program long term and reducing any risk of unintended side effects. Further details about the use of modular design can be found within the `tech-methodology.md` file.

### User Interface Layer

The interface has been built purposely, using PySide6, to guarantee ease of use for staff members through a simple layout. Prioritizing clarity, usability, and error prevention over any sort of aesthetics.

Through the user interface, the user will be able to;

- Select and approve an optional workflow.
- Authenticate API access, using a personal business account.
- View customer/business conversations retired through eBay’s API
- Select a business to customer conversation, initiating the reply process.
- Review AI generated content from either the local AI model or eBay’s platform.
- Input non sensitive customer data into the local AI model for a response.
- Manually review/edit responses at each stage of the process.

By guiding the user through this process rather than committing to full automation, user reviews can be utilized to avoid any violations of policy with the use of sensitive customer data.
