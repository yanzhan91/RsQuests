from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response
from ask_sdk_model.ui import SimpleCard
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
import boto3
import logging as log
import json

sb = SkillBuilder()
client = boto3.client('dynamodb')
handler = sb.lambda_handler()

@sb.request_handler(can_handle_func=is_request_type("LaunchRequest"))
def launch_request_handler(handler_input):
    # type: (HandlerInput) -> Response
    speech_text = "Welcome to the Alexa Skills Kit, you can say hello!"
    log.info(handler_input)

    handler_input.response_builder.speak(speech_text).set_card(
         SimpleCard("Hello World", speech_text)).set_should_end_session(
         False)
    return handler_input.response_builder.response

@sb.request_handler(can_handle_func=is_intent_name("QuestIntent"))
def quest_intent_handler(handler_input):
    slots = handler_input.request_envelope.request.intent.slots
    slot = slots['name']
    quest_name = slot.value
    response = client.get_item(
        Key={
            'name': {
                'S': quest_name,
            }
        },
        TableName='Runescape_Quests'
    )
    print(type(response))
    print(response)
    print(response['Item'])
    quest = response['Item']

    # if 'requiredItems' in quest or 'requiredSkills' in quest:
    #     speech_text = 'For this quest you will need'
    #     if 'requiredItems' in quest:
    #         speech_text = speech_text + ' ' + quest['requiredItems']
        
    #     if 'requiredItems' in quest and 'requiredSkills' in quest:
    #         speech_text = speech_text + ' and '

    #     if 'requiredSkills' in quest:
    #         speech_text = speech_text + ' ' + quest['requiredSkills']
        
    #     speech_text = speech_text + '.'
    # else:
    #     speech_text = 'No requirements are needed for this quest. '

    # speech_text = speech_text + 'Do you want to start or cancel?'
    speech_text = "Hello Yan"

    handler_input.response_builder.speak(speech_text).set_card(
        SimpleCard(quest, speech_text)).set_should_end_session(False)

    print(type(handler_input.attributes_manager))
    print(type(handler_input.attributes_manager.session_attributes))
        
    return handler_input.response_builder.response

@sb.request_handler(can_handle_func=is_intent_name("NextIntent"))
def next_intent_handler(handler_input):
    return None

@sb.request_handler(can_handle_func=is_intent_name("RepeatIntent"))
def repeat_intent_handler(handler_input):
    return None

@sb.request_handler(can_handle_func=is_intent_name("AMAZON.HelpIntent"))
def help_intent_handler(handler_input):
    # type: (HandlerInput) -> Response
    speech_text = "Which quest would you like to start. For example, you can say, start demon slayer."

    handler_input.response_builder.speak(speech_text).ask(speech_text).set_card(
        SimpleCard("Runescape Quest Help", speech_text)).should_end_session(True);
    return handler_input.response_builder.response

@sb.request_handler(
    can_handle_func=lambda handler_input :
        is_intent_name("AMAZON.CancelIntent")(handler_input) or
        is_intent_name("AMAZON.StopIntent")(handler_input))
def cancel_and_stop_intent_handler(handler_input):
    # type: (HandlerInput) -> Response
    speech_text = "Goodbye!"

    handler_input.response_builder.speak(speech_text).set_card(
        SimpleCard("Hello World", speech_text)).set_should_end_session(True)
    return handler_input.response_builder.response

@sb.exception_handler(can_handle_func=lambda i, e: True)
def all_exception_handler(handler_input, exception):
    # type: (HandlerInput, Exception) -> Response
    # Log the exception in CloudWatch Logs
    print(exception)

    speech = "Sorry, I didn't get it. Can you please say it again!!"
    handler_input.response_builder.speak(speech).ask(speech)
    return handler_input.response_builder.response