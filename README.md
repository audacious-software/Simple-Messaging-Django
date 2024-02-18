# Simple Messaging

This is an infrastructure package for Django intended to build interactive messaging applications.

This infrastructure is intended to embedded in larger projects and extended for building actual applications. For example, by installing and configuring [Simple Messaging: Twilio](https://github.com/audacious-software/Simple-Messaging-Django-Twilio/) and [the Quicksilver job management system](https://github.com/audacious-software/Quicksilver-Django), you can stand up a simple SMS messaging site compatible with Twilio that can send and receive messages using that Twilio's API. (The more Microsoft-oriented crowd can substitute [Simple Messaging: Azure](https://github.com/audacious-software/Simple-Messaging-Django-Azure/) to use that service instead.)

This package provides the basic incoming and outgoing message Django models, as well as supporting models for attaching media to messages. If so configured, it also implements column-level encryption for message sender and receivers. When combined with our [URL Shortener package](https://github.com/audacious-software/Django-URL-Shortener), it will use that service to shorten URLs of outgoing messages (not necessarily a recommended configuration now that shortened URLs may be blocked elsewhere in messaging networks).

## Models

### Incoming Message

Represents an message received from outside the system. 

**Sender:** Phone number or address of the party originating the message. Note that this framework *does not* impose any validation or checking of correctness, as this model may be used in a *wide* variety of use cases: phone numbers, e-mail addresses, instant messenger handlee, etc. Note that this *may* be encrypted for security reasons if configured.

**Recipient:** Phone number or address of the party receiving the message. Note that this framework *does not* impose any validation or checking of correctness, as this model may be used in a *wide* variety of use cases: phone numbers, e-mail addresses, instant messenger handlee, etc. When used with services like Azure or Twilio, this is often the central phone number being used to send and receive messages by the server.

**Receive date:** Timestamp when the message was received by the server.

**Message:** Textual content of the message. Note that media attachments will be attached to the message as [incoming message media](#incoming-message-media) files. If media is attached, this field *may* be empty.

**Trandmission metadata:** Additional metadata provided by the service sending the message to the server. May include sender information, transmission metadata, and more. Stored as a JSON-encoded structure.

**Lookup key:** Indexed optional field that may be used by the server to implement specific look-up algorthims for querying the table for a phone number in a table full of encrypted phone numbers. Obfuscated data types such as hashes may be used to counteract the speed penalty imposed by source and destination encrytion.

### Incoming Message Media

Small model wrapping a file or other multimedia content received with a message. 

**Message:** Incoming message that arrived with this media.

**Index:** Order within the message (default: `0`).

**Content file:** [Django `File` object](https://docs.djangoproject.com/en/3.2/ref/files/file/) where the content of the media is stored on disk.

**Content URL:** Original location of the media. This is often an ephememral URL that does not persists, so content is cached locally in the *Content file*.

**Content Type:** [MIME-type](https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types) of the message media.

### Outgoing Message

Represents an message sent from the system. 

**Destination:** Phone number or address of the to receive the message Note that this framework *does not* impose any validation or checking of correctness, as this model may be used in a *wide* variety of use cases: phone numbers, e-mail addresses, instant messenger handlee, etc. Note that this *may* be encrypted for security reasons if configured.

**Reference ID:** Optional field that may be used to reference other objects in site-specific contexts.

**Send date:** Timestamp when the message should be sent by the server. Note that a periodic background job (every 5 seconds or so) is responsible for determining when a message is due to be sent and attempts to send it. Send dates *may* be scheduled for the future to schedule automated messages ahead of time.

**Sent date:** Timestamp when the message was actually sent by the server. Large persistent delays between *send dates* and *sent dates* may indicate a local system problem that should be investigated.

**Message:** Textual content of the message. Note that media attachments will be attached to the message as [outgoing message media](#outgoing-message-media) files. If media is attached, this field *may* be empty.

**Errored:** Indicates whether an error occured while transmitting the message. Error information will often be stored in the *transmission metadata* field.

**Trandmission metadata:** Additional metadata provided by the service sending the message to the recipient. Includes transmission results, erors, or other details. Stored as a JSON-encoded structure.

**Message metadata:** Additional metadata related to the message or the sender to be used by the system itself. For example, when used with a dialog system, this may include some dialog state information relevant to the message, such as demographic details used to select a specific message or variables used to populate placeholders. Stored as a JSON-encoded structure.

**Lookup key:** Indexed optional field that may be used by the server to implement specific look-up algorthims for querying the table for a phone number in a table full of encrypted phone numbers. Obfuscated data types such as hashes may be used to counteract the speed penalty imposed by source and destination encrytion.

### Outgoing Message Media

Small model wrapping files or other multimedia content to be transmitted alongside a message. 

**Message:** Outgoing message that includes this content.

**Index:** Order within the message (default: `0`).

**Content file:** [Django `File` object](https://docs.djangoproject.com/en/3.2/ref/files/file/) where the content of the media is stored on disk.

**Content Type:** [MIME-type](https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types) of the message media.

## Compatible Packages

Simple Messaging is designed to work in conjunction with additional add-on packages.

### Message Transmission

[Simple Messaging: Azure](https://github.com/audacious-software/Simple-Messaging-Django-Azure) - Implements the infrastructure to send and receive via [Azure Communication Services](https://azure.microsoft.com/en-us/products/communication-services). Includes SMS messaging.

[Simple Messaging: Twilio](https://github.com/audacious-software/Simple-Messaging-Django-Twilio) - Implements the infrstructure to send and receive via Twilio services. Includes SMS, MMS, and WhatsApp messaging.

[Simple Messaging: E-Mail](https://github.com/audacious-software/Simple-Messaging-Django-Email) - Implements sending messages as outbound e-mails. Does not include support (yet) for e-mail as an incoming messaging channel.

[Simple Messaging: Switchboard](https://github.com/audacious-software/Simple-Messaging-Switchboard) - Implements a meta-infrastructure that allows multiple messaging channels to be used by the same site, including multiple instances of the same channel (e.g. two Twilio phone numbers) or mixing different types of channels (e.g. using Azure for interactive messaging, e-mail for other communications).

### Interactive Dialog Systems

Simple Messaging may be combined alongside the messaging transmission pacakages above and the following components to implement an interactive dialog system.

[Django Dialog Engine](https://github.com/audacious-software/Django-Dialog-Engine) - Provides the core foundation for an interactive state-machine-driven dialog system, including a default set of programming primitives to construct a full dialog, the execution environment of the state machine, and suitable options for expanding and extending the dialog system with new node types and capabilities. **(Required)**

[Django Dialog Engine: Builder](https://github.com/audacious-software/Django-Dialog-Engine-Builder) - Provides an interactive authoring environment for constructing dialogs. **(Optional)**

[Simple Messaging: Dialog Support](https://github.com/audacious-software/Simple-Messaging-Dialog-Engine-Support) - Provides the necessary bridging infrastructure that allows Django Dialog Engine to use Simple Messaging as a communications channel, and allows Simple Messaging to inititiate and manage dialogs. **(Required)**

To review how to set up a site utilizing these components, review [the SMS Dialog Site repository](https://github.com/audacious-software/SMS-Dialog-Site-Django), which contains a complete Django project utilizing all of these components.

### Other Compatible Packages

Simple Messaging is compatible with the following additional packages, should they be present on the system:

* [Nagios Monitor](https://github.com/audacious-software/Django-Nagios-Monitoring) - Used to validate the configuration of the local Simple Messaging package, as well as any additional associated packages.
* [Simple Data Export](https://github.com/audacious-software/Simple-Data-Export-Django) - Provides message transcripts as an exportable report when this package is present. When used with Simple Message: Dialog Support, other reports become available related to dialog states and progress.
* [Simple Backup](https://github.com/audacious-software/Simple-Backup-Django) - When present, Simple Messaging objects will be included in system-wide incremental backups created by the Simple Backup package.


## Licensing Information

Copyright 2020-2024 Audacious Software

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at

[http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0)

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
