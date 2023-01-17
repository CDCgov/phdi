# PHDI Alerts Container

This Docker container provides a simple API for sending alerts via SMS, Slack, or Microsoft Teams. It can be run as a local service or deployed as part of a full pipeline using PHDI Building Blocks as in [CDCgov/phdi-azure](https://github.com/CDCgov/phdi-azure).

## Usage

Some manual steps need to be taken to enable alerts in your particular environment.

### SMS

In order to send text messages, you'll need to create an Azure Communication Service. Follow this [quickstart guide](https://learn.microsoft.com/en-us/azure/communication-services/quickstarts/create-communication-resource?tabs=windows&pivots=platform-azp) to set up the resource. Once created, you'll need to provide the name of your resource as an environment variable (`COMMUNICATION_SERVICE_NAME`) to the container.  
  
The first time you make a call to `/sms-alert`, the container will purchase a phone number to use for sending text messages. This will charge your Azure account $2/month to reserve the phone number.

Support for other SMS providers besides Azure are coming soon!

#### Sample request

`POST /sms-alert`
```json
{
    "phone_number": "+19168675309",
    "message": "Hi this is a test"
}
```

### Slack

To send alerts to your Slack workspace, you'll need to create a Slack application. Follow this [guide](https://github.com/slackapi/python-slack-sdk/blob/main/tutorial/01-creating-the-slack-app.md) to create the Slack app, giving it a name you'll recognize, such as `PHDI Alerts`. The OAuth access token must be provided to the container as an environment variable (`SLACK_BOT_TOKEN`). You must also invite the application to any channel you wish to alert (type `/invite` in the channel and choose "Add apps to channel"). To get the ID of a channel, right click the channel name and choose "View channel details". The ID is at the bottom of the modal that appears.

#### Sample request

`POST /slack-alert`
```json
{
    "channel_id": "C04GKBFMGRM",
    "message": "Hi this is a test"
}
```

### Microsoft Teams

To send alerts to Microsoft Teams, you'll need to create a webhook in the channel you wish to alert. To add an incoming webhook to a Teams channel:

1. Navigate to the channel where you want to add the webhook and select (•••) Connectors from the top navigation bar.
1. Search for Incoming Webhook, and add it.
1. Click Configure and provide a name for your webhook.
1. Copy the URL which appears and click "OK".

Provide this URL as an environment variable (`TEAMS_WEBHOOK_URL`) to the container.

#### Sample request

`POST /teams-alert`
```json
{
    "message": "Hi this is a test"
}
```