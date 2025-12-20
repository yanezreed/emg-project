# EMG-Project

## Project Overview

This project, is a native desktop application used as an internal tool for the staff at Guitar Anatomy, an eBay based ecommerce company based in the North East of England. Whom specialise in selling specialized guitar parts.

The application itself is designed to assist staff in managing the ever increasing inquiries received through eBay’s platform messaging system. The primary goal being to reduce response times, improve consistency, accuracy, and generalize tone across all customer communications.

Initially aiming to create a fully automated program, the project's use of AI necessitated a design pivot. Constraints on the use of customer data, imposed through the eBay Developer Program License Agreement and the Data Protection Act, led me to develop an application with two optional workflows, ensuring constant user involvement and review throughout the process. Each of the workflows contains a different level of AI involvement, but both are alike in the fact that data is never stored, persisted, or used to train AI models.

Lastly, this is a project built as a portfolio piece and is in no way affiliated with eBay.

## System Overview

This application, at its core, contains three primary components; a user interface layer, an application layer, and an integration layer.

I have designed this system to keep these layers completely separated, through a modular design, with the intention of allowing each of these features to be modified or replaced without affecting the full scope of the system. Therefore, improving the ability to maintain the program long term and reducing any risk of unintended side effects. Further details about the use of modular design can be found within the `tech-methodology.md` file.
