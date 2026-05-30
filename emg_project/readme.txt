## Project Overview

This project contains my native desktop application. Developed to be used as an internal tool for a small local business, operating as an ebay based ecommerce company, that specialises in the sale of custom made guitar parts.

The application itself is designed to assist staff in managing the ever increasing number of enquiries received through eBay’s platform messaging platform. With its primary goal being to reduce the company's response times while also improving the reply quality, consistency, and accuracy.

## Initial Idea and Restrictions
   
The original concept was to create a highly automated system, heavily relying on the use of ai, to assist with, and also generate business to customer responses on command.

However, due to the constraints imposed by both the eBay Developer Program Licensing Agreement, and compliance requirements related to the Data Protection Act, the direction of my project then had to be reconsidered.

As a result I decided on a design with two optional workflows, both incorporating varying levels of ai usage while remaining compliant with the relevant legal and platform requirements. Such as detailed in the acts above.

## System Overview

I structured this application around three primary components.
A user interface layer, an application layer and an integration layer.

Each of these layers has been fashioned to keep files separated within a modular design. 
Purposely built to allow for each of these layers to be tweaked and modified without the need to deal with the entire scope of the system's code at once. Allowing myself and other future users, less experienced with programming, to understand exactly where to look when dealing with certain issues and project elements.

In hindsight, this modular approach also allowed me to isolate the relevant inputs into outputs involved with each of my methods, making it easier to follow my applications workflow and behaviour, to then identify the source of my issues throughout all stages of development.

As by separating functionality into distinct layers, I was able to recognise possible design faults and imminent critical errors effectively. With the following solutions to these issues, having very little impact on my project at scope. Improving my ability to then debug my application and passively redefine its design, as I continued to expand my codebase.

Further details about the use of modular design can be found within the `tech-methodology.md` file. Below is an explanation of each layer.
