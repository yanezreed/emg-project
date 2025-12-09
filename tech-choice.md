## Choice Code Language

Having gained confidence working with both C code and Python throughout my studies in Harvard's CS50 and CS50P courses. 
Because of this, I have now made the decision to develop my application primarily with Python.

The decision itself was based on the combination of my program's user base, practicality, security considerations, and support in the form of documentation, which will be essential for me to be able to learn.
​
Python's library ecosystem was also a major factor. Supporting the core functionality for my project with OAuth authentication, API communication, and the integration of my own AI models, all acting as vital components for my application. 

Working with these technologies at a higher level, rather than at a lower level in C code, is definitely more manageable for me at this stage. Not having to worry about manual memory management, pointer mismanagement, buffer overflow or any kind of low level error easily created in C, allows me to focus on understanding the underlying concepts before anything else. Which will perfectly fit my incremental approach. As I will be developing each piece of my application separately, to ultimately integrate the various core components later on.

While it's completely possible for me to reproduce all of this functionality and output using C. Doing so would significantly increase the amount of research, work, and planning it would take to get this project off the ground.
Having previously handled memory management, network requests, and parsing json structures within my previous project, in a C coded HTTP server. I’m well aware that the easily made errors in any of these areas could cause critical faults or security vulnerabilities within both development, and within the business when deployed. The additional time it would take, in low level implementation and testing to ensure any errors are dealt with, would be substantial and unrealistic within my timescope.
​

Performance wise, C would undoubtedly be superior. With memory efficiency and faster processing times far outperforming Python as an object oriented programming language. However, because of the nature of this program I am designing, high optimisation may not yield meaningful real world benefits at this scale. The project is simplistic in the fact it will be single user in operation, with a very low data throughput. Meaning, while optimisation with C is possible and beneficial, it would not provide a significant impact on performance at this scale. With the limiting factor instead being the speed of the user's interaction with the UI, rather than task processing speeds.

In conclusion, I believe that Python is more than sufficient. Considering development speed, security, testing, and library support. The language is a far more efficient choice for achieving the objectives of my application at this scale.

## UI Framework Choice

When deciding on a user interface framework to use alongside Python, I chose to use PySide6. Highly compatible with my language choice, it provides the ideal set of widgets and layout structures for the purpose driven simplistic interface, requested by the business.

A key factor in my decision to use this framework was also its integrated visual design tool, Qt Designer. As a computer animation graduate, avoiding the disconnect between my visualization of the desired interface and the code constructing it is invaluable. Being able to translate my wireframe prototypes drawn within Photoshop, directly into a functional layout, allowed me to best use my skillset and work far more efficiently.

Furthermore, because of PySide6’s support of modular design, each individual widget or component is into clean, separate readable files. Giving me confidence that the codebase, when written in Python, will remain clear, maintainable, and understandable long term. Reducing any risk of technical debt.

Lastly, by using PySide6, I will be able to produce an application that will be able to function cross platform. In the case of the business transitioning operating systems from Windows to Linux or macOS, my application would not require any sort of major redesign.

Before deciding on PySide6, I also explored possible alternatives.

Kivy, which is another open source Python framework, similar also in its creation of cross platform software. Appealed to me through its primary use to create UI for mobile devices. Useful as the staff of this business would occasionally commute and could be actively replying to customers. However, having little to no experience with mobile interface design myself, and finding comparatively limited relevant beginner friendly documentation online. Therefore adopting Kivy would bring unnecessary risk in the form of missing critical project deadlines, so I decided against it.

Electron, in contrast, is extremely beginner friendly. Offering an extensive amount of documentation and tutorials, and containing far superior tools to those available in PySide6. I was confident in the use of Electron, due to the help I would receive, I could produce more modern dynamic interfaces even within the deadlines I have set.

However, with Electron being web based rather than desktop, subsequently it is run using a Chromium engine. I’m cognizant of the significant memory usage and processing power the software would require.

So if I were to choose Electron as the framework I would use, I believe I would be introducing unnecessary resource demands Without utilizing the benefits of the framework because of my relatively simple, purpose driven user interfaces, that don’t require any modern sleek widgets or layouts.

Overall, PySide6 would simply provide a practical balance of performance, documentation, maintainability, and suitable design capabilities. Offering everything I would require without any unnecessary complexity that could affect my ability to reach my project deadlines.

## Software Development Methodology

In terms of my methodology and approach to the development of this project, I’ve decided to take an incremental approach. Which would entail the researching, extensively planning, and implementing of each core element of the application systematically. Allowing me to isolate any errors through debugging early on in the process, working in small manageable steps.

With many decisions at each stage of development hinging on feedback received from the business. I will be forced to make constant design alterations for the evolving requirements. By using a modular approach to designing each element of my program, I will be able to adjust said features at any stage. Preventing me from hard committing to any rigid, inflexible design, early on in the process.

By breaking the project into approachable milestones, I can also prevent myself from being overwhelmed with the idea that I must consider how each component will interact with the entire system. Which would hinder my productivity, as I second guess each of my design choices.

Focusing on core functionality piece by piece, with OAuth authentication, the UI structure, and API communication being examples of said milestones. I can ensure that the self contained increments are well tested, documented, and assembled cleanly at a smaller scale. Each element can then be successfully integrated down the road, assuring that errors will not compound and avoiding wasting development time seeking out the problems source.

As explained in earlier sections, this mirrors my reasoning behind choices in both my core language and UI framework. Because of the modular nature of both Python and PySide6, this process is both realistic and aligns well with the technologies I intend to use.

I will also be maintaining my codebase using GitHub. Giving me access to version control, where I can track my progress, review my sets of changes, and safely revert any past errors introduced through integration. As unpredictable bugs may cause issues when I do eventually combine my separate modules. Having the ability to branch, merge, and roll back these changes will be invaluable.

## Security Considerations

...
