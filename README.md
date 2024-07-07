# ABC Call Center

## Overview

This is a sample ABC Call Center built for this project. The idea behind it was to start small and simple. Though it isn't intended for a real customer or client, it showcases ideas that make the call center scalable for multiple teams and business lines. The components of the call center, including its flows, Lambdas, and Lex bots, are designed to be dynamic and adaptable for various business lines.

## Call Flows

The call center consists of three flows:

- [ABC-Landing](https://github.com/saucemills/abc-call-center/blob/main/contact_flows/ABC-Landing.png)
- **ABC-MainMenu**
- **ABC-Transfer**

### ABC-Landing

All calls start at ABC-Landing. In this call flow, the dialed number (DNIS) is input into a Lambda that checks a DynamoDB log of all the phone numbers for the call center. It returns relevant information concerning the DNIS back to the call flow, such as `businessLine` and `nextCallFlow`.

This allows the client to direct calls based on the number dialed. For example, a number can go straight to a queue or send the caller to the main menu to handle the caller's needs more specifically.

#### Example DNIS Config Item:

```json
{
  "node": "+18449955666",
  "dnis": "+18449955666",
  "businessLine": "sales",
  "nextCallFlow": "ABC-MainMenu",
  "nextCallFlowArn": ""
}
```

Then, in ABC-MainMenu, the business line set in the DNIS-config Lambda will be input into a prompt Lambda. The prompt Lambda will return all the relevant prompts that may be used in this call flow. This is also done to maintain dynamism throughout the flow and allow different business lines to use the same call flow and have their own specific prompts based on what they want said to the caller.

#### Example Prompt Item:

```json
{
  "businessLine": "sales",
  "mainMenuPrompt": "Thank you for calling the sales menu. Press 1 for an open queue. Press 2 for a queue on holiday. Press 3 to Repeat the options.",
  "openQueueTransfer": "Now transferring you to the open queue.",
  "holidayQueueTransfer": "Now transferring you to the holiday queue.",
  "errorPrompt": "Something went wrong."
}
```

The flow then goes to a get user input menu where it will use the `mainMenuPrompt` that it got from the prompt Lambda and ask the caller to pick from three options: an open queue, a closed queue, or to repeat the options. Based on which option they choose, the appropriate prompt will play, and they will be sent to the next flow, ABC-Transfer, to determine queue status and transfer to the queue.

### ABC-Transfer

In ABC-Transfer, the call flow will send the `callerIntent` to the transfer Lambda. The Lambda will then do a couple of things. First, it will get the intent and look at the transfer type and information from a DynamoDB transfer item. If it is a queue, it will check the queue’s hours from the transfer item against the current day and time and return a queue status. If the queue status is open, the flow will then set the queue and transfer the caller to the queue. If it is closed, it will play a closed message and end the call.

#### Example Transfer Item:

```json
{
  "callerIntent": "OpenQueueIntent",
  "transferType": "queue",
  "transferpointName": "Open_Queue",
  "transferPoint": "arn:aws:connect:us-west-2:058264086287:instance/ab726981-c854-43ad-8b06-bd7e651f7fe3/queue/19a8427d-b3ed-4217-acb0-78ff52d89bb2",
  "timeZone": "US/Eastern",
  "hours": {
    "Sunday": { "start": "00:00:00", "end": "23:59:59" },
    "Monday": { "start": "00:00:00", "end": "23:59:59" },
    "Tuesday": { "start": "00:00:00", "end": "23:59:59" },
    "Wednesday": { "start": "00:00:00", "end": "23:59:59" },
    "Thursday": { "start": "00:00:00", "end": "23:59:59" },
    "Friday": { "start": "00:00:00", "end": "23:59:59" },
    "Saturday": { "start": "00:00:00", "end": "23:59:59" }
  }
}
```

ABC-Transfer and the transfer Lambda are meant to be able to be flexible and handle different types of transfers, not just queue transfers. The client could just as easily set up the transfer type as another flow, such as a self-service flow or an authentication flow, to get more information from the caller. It could also handle an external transfer and send the call to that external number.

These options are meant to maintain flexibility and scalability as the center and uses for the call flows grow.

## Other Considerations

There are a few things I have implemented around the flows, Lambdas, and AWS console to help with error tracking:

1. **Journey Attribute**: At the beginning of each call flow and at important inflection points inside each call flow, I have added a ‘journey’ attribute in different set contact attribute blocks which logs where the call goes. This makes it easier in the contact search records to see where a call went or where it possibly failed straight from the Amazon Connect console without having to use CloudWatch.

2. **CloudWatch Queries**: For occasions when you might need more information, such as what a Lambda returned or exact values extracted in an Amazon Connect call flow, I have set up my own Amazon Connect CloudWatch query so that anyone with appropriate access to the AWS environment can search easily in CloudWatch for a call and get detailed information on it, only needing the contact ID for the call.

3. **Lambda Logging**: Each Lambda has been set up with logging at important points to be able to see in its CloudWatch logs more detailed information on what happened or possibly anything that went wrong.

## Future Improvements

With more time, I had a lot of ideas for things I could have implemented:

- Unit tests for the Lambdas to ensure changes do not break functionality.
- More dynamism inside the MainMenu Lex bot, including functionality to separately handle DTMF inputs so that different business lines could use the same Lambda and have different DTMF inputs and intents despite using the same menu.
