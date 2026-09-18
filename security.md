# Security

## Intro

Security as discussed within `design.md` has always been one of the primary considerations during the development of this project. As given the nature of this application, and its reliance on the use of sensitive customer data retrieved through ebay's api, critical design decisions had to be made to help protect both the user of this application and their customers.

## Api and token management

### Api details

The credentials listed below are required by ebay’s api during oauth authentication. 

Client id
Client secret
Render server url
Api scope

The `client_id` value enables the external flask server to identify itself as part of my registered desktop application within ebays system. Whereas the `client_secret` value, when included alongside the client id, authenticates the application during the exchange of the authorisation code. 

Within this http post request made to ebays token endpoint, authenticated using the credentials above, an exchange occurs of the already received authorisation code for token data containing a valid access token.

This process is discussed at length within my `technology.md` file. But in summary, the `client_id` and the `client_secret` are combined and encoded when assigned to the `auth` parameter. Submitted as a tuple, these values are automatically combined and encoded by the `requests` library, when the http request is constructed.

The two values, now combined in the format `client_id:client_secret` are now encoded using base64. Meaning that the binary representation of this format is separated into six bit groups, with each of these groups represented by one of the sixty four characters of base64.

The result of this process is a text value that is suitable for a http header, which can be later decoded by ebay when the request is received. 

The `requests` library then constructs the header, in the format `authorisation: basic …` with the word `basic` identifying the http basic authorisation as the version being used.

Note that the encoding of these values does not encrypt these details, as they can easily be decoded. Which is why it is so important this data is transferred using https and not http, as https provides encryption needed to protect the credentials when being transferred.

To avoid the exposure of these values through the actual source code held within my github account, these sensitive values are alternatively stored as environment variables within render’s dashboard. Accessed in run time by the flask application, through the use of the `os.environ.get` method, rather than being assigned as variables within the code.

Anyone viewing my public github repository will only be able to see the environment variable names used to retrieve these values, and not hardcoded credentials listed above within the external servers source code.

### Oauth tokens

Without storing or handling the current users actual ebay login details, this application as explained within `ebay_integration.md` uses oauth 2.0 to allow the user to authenticate their own account directly through ebay's login page to approve my applications access.

Once logged in, ebay redirects the users browser to my flask server's callback route, provided to ebay through the developer account set up.

When the users browser is redirected, an authorisation code is included as a query parameter within the url. Which is then accessed through the flask servers `request.args` value, as explained in details within my `ebay_integration.md` doc. 

Through the use of a post request, my flask server then exchanges this code for token data through ebays api token endpoint.

This token data includes an access token value. Used throughout both my applications optional workflows, to authenticate future requests made to ebays messaging api. 

The access token data is then stored within the `ebay_tokens.json` file, on the current user’s local machine. This file has been purposely included within the `.gitignore` to ensure that no raw token data is ever committed to github. Preventing the data from being publicly exposed within my repository.

This access token is now used in place of the users login details, to authenticate the requests made to ebays api, on their behalf. Avoiding the need to ever save or store the users actual ebays credentials within my program. As although this is a standard feature of oauth 2.0 rather than a design decision within my own application, it is still inline with my efforts to minimise credential exposure, and directly contributes towards improving the security of my program.

## User login

### Database

A local sqlite database is used within my project to store the user accounts required for user login within this application. The database has no involvement with either the oauth authentication process or ebay itself. It only exists to authenticate staff and users of my application, allowing them to sign into their own personal account, rather than a single shared account across a business. Storing the usernames and hashed passwords required for login.

### Password hashing

To ensure the security of user credentials within this local sqlite database, the passwords themselves are purposely never stored in plain text. As storing plain text passwords would cause immediate exposure in the case of the database being compromised. 

Protected instead, by the use of a key stretching function `pbkdf2-hmac-sha256`. This function combines the user's password with a randomly generated sixteen byte salt and a six hundred thousand iteration count, to produce a derived key, stored in place of the original password.

The `sha256` alone, is a hashing function which takes an input of any size to produce a fixed length two hundred and fifty six bit hash value as a result. And because of its deterministic nature, it will always produce the same output. Which is essential for authenticating future login in attempts.

However, the reason `sha256` is not used in isolation to secure the passwords within the database, is that the resulting hashes would be extremely vulnerable to rainbow table attacks. In addition to simple brute forcing attempts.

By instead using the key stretching function, specifically the `pbkdf2` aspect, both of these vulnerabilities are addressed. The `hmac-sha256` operation is repeatedly executed six hundred thousand times, with the output of each iteration becoming the input for the next. Greatly increasing the computational effort that is required to test each password guess. Making brute force attempts far less practical, because of the amount of time processing would take. Additionally, because of the inclusion of the random salt, even identical original passwords will produce entirely different resulting stored hash values, rendering the use of rainbow tables impractical.

This final stored value can be found within the database column `hashed_password`, and consists of a hexadecimal string containing both the salt and the derived key together. This allows the salt to be recovered for verification, without requiring a dedicated separate column within the database.

## Data protection

### Session based data handling

Already covered extensively within `ebay_integration.md`, my program never caches, logs, or writes any customer conversation data retrieved through the use of ebays api to the disk.

Instead, all conversational data is held only within memory during active applications sessions, within `self.messages_stored` inside the file `chat_widget.py`. This data is discarded in its entirety when the current application session ends.

This was a deliberate design decision made to avoid the storing of sensitive customer data, while also helping my application remain compliant to the ebay developer license agreement. As the persistent storing of these customer conversations within my program, be it within either the flask server or desktop application, would cause a violation of these requirements.

### Sanitisation

As covered within `ebay_integration.md`, sanitisation of personally identifiable information is a key part of what allows my application to remain compliant to ebay's data handling restrictions.

This sanitisation is carried out by the `sanitise_text` method within `user_class.py`, which uses microsoft's presidio library to automatically detect and redact potentially sensitive information.

This content could include names, phone numbers, email addresses, and other personally identifiable information within the conversations received from ebay's api. By redacting this information before the conversation could be processed by the ai model, the risk of sensitive customer data exposure is reduced. Assisting my application, by allowing it to remain compliant to ebay's developer license agreement, even with the addition of the usage of a local ai model.

As explained in detail within `ebay_integration.md` this use of microsoft's presidio library, can of course not guarantee that all sensitive information will be discovered and removed by the program. Which is why mandatory user manual review of the sanitised conversation is included within the design of my application.

This step is enforced at the ui level, within `generate_dialog.py` as the generation button is intentionally disabled until the sanitisation process has been carried out and the user has reviewed the resulting content.

### Ai processing

The decision was made to run the ollama ai model locally on the user’s machine, in an effort to avoid transmitting data externally to any ai services. Even at the cost of increasing the size of the applications initial set up, and the amount of local storage required.

This reduces the risk of sensitive information being intercepted, stored, or used in ways outside of my applications control. While also supporting compliance with ebay’s data handling requirements.

### Api scope

When authenticating my application within the oauth process, ebay requires that an api scope is 
included within the initial http authorisation request. As this scope is used to define the level of access requested by my application.

To align with the principle of data minimisation, my application only requests the minimum level of scope required in `https://api.ebay.com/oauth/api_scope/commerce.message`. Which grants my application access, through the limited access token provided, only to the messaging api for the currently authenticated ebay account.

This decision was made because if an access token was to be somehow compromised, the holder of this token would only gain access to the messaging data of the user. And not access to other elements of the users ebay account, such as payment information and current listings.

By limiting the permissions granted to my application, I am minimising the potential impact of a compromised access token on the user.

## Error handling

All api http requests made within `ebay_client.py` validate the http status code of the responses received, before returning any data to my application.

If an unexpected status code is received, the request attempt is treated as a failure and my code raises a runtime error with a clear message, displayed through the terminal. This message includes the unexpected http status code returned by the api, allowing the source of the request failure to be identified.

This also ensures that unexpected api responses are detected immediately, preventing invalid or incomplete data from a fail request, being returned to my application layer.

Known failures are also handled more specifically. A clear example of this is displayed within my `chat_widget.py` file as some of the conversations displayed within the ui list, when clicked, may return a `404` error when the message data is requested from ebays api. 

If this is the case, the conversation corresponding to the message data failed to be retried, is removed from the ui list. Preventing the future accidental requests being made, and recurring error messages displayed to the user, if the fault conversation was to be accidentally selected again.

Lastly, all of the http responses and also failed requests, involving either the external render hosted flask server, the locally running ollama model, or ebays api, are handled within the files responsible for their corresponding communication.

Failures within each of these workflows are also handled accordingly, depending on which endpoint they are involved with, and what the expected results of the http request made are.

This design allows useful information, such as returned http status codes, to be retained for debugging purposes ,while warning messages are also displayed to the user through the interface. With the aim to inform the user of issues preventing the current workflow they are involved with, from proceeding.




