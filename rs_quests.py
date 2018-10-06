from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response
from ask_sdk_model.ui import SimpleCard
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from boto3.dynamodb.types import TypeDeserializer
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
    quest_name = slot.value.title()
    response = client.get_item(
        Key={
            'name': {
                'S': quest_name.title(),
            }
        },
        TableName='Runescape_Quests'
    )

    if 'Item' not in response:
        speech_text = 'This quest is currently not supported. Please try again later.'
        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard('Unknown Quest', speech_text)).set_should_end_session(True)
        return handler_input.response_builder.response

    quest = response['Item']

    deserializer = TypeDeserializer()

    if 'requiredItems' in quest or 'requiredSkills' in quest:
        speech_text = "For %s, you will need" % quest_name
        if 'requiredItems' in quest:
            speech_text = speech_text + ' ' + deserializer.deserialize(quest['requiredItems'])
        
        if 'requiredItems' in quest and 'requiredSkills' in quest:
            speech_text = speech_text + ' and '

        if 'requiredSkills' in quest:
            speech_text = speech_text + ' ' + deserializer.deserialize(quest['requiredSkills'])
        
        speech_text = speech_text + '. '
    else:
        speech_text = "%s does not require any item or skill. " % quest_name

    speech_text = speech_text + 'Do you want to start or cancel?'

    handler_input.response_builder.speak(speech_text).set_card(
        SimpleCard(quest_name, speech_text)).set_should_end_session(False)

    handler_input.attributes_manager.session_attributes['step'] = -1
    handler_input.attributes_manager.session_attributes['steps'] = deserializer.deserialize(quest['steps'])
    handler_input.attributes_manager.session_attributes['quest_name'] = quest_name
    
    return handler_input.response_builder.response

@sb.request_handler(can_handle_func=is_intent_name("NextIntent"))
def next_intent_handler(handler_input):
    step = handler_input.attributes_manager.session_attributes['step']
    steps = handler_input.attributes_manager.session_attributes['steps']
    quest_name = handler_input.attributes_manager.session_attributes['quest_name']

    if len(steps) >= step + 1:
        speech_text = steps[step + 1]
        handler_input.attributes_manager.session_attributes['step'] += 1
        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("%s: Step %s" % (quest_name, step), speech_text)).set_should_end_session(False)
    else:
        speech_text = "You have completed %s. Thank you for using Runescape Quests" % quest_name
        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard(quest_name, speech_text)).set_should_end_session(True)
        
    return handler_input.response_builder.response

@sb.request_handler(can_handle_func=is_intent_name("RepeatIntent"))
def repeat_intent_handler(handler_input):
    step = handler_input.attributes_manager.session_attributes['step']
    steps = handler_input.attributes_manager.session_attributes['steps']
    quest_name = handler_input.attributes_manager.session_attributes['quest_name']
    speech_text = steps[step]

    handler_input.response_builder.speak(speech_text).set_card(
        SimpleCard("%s: Step %s" % (quest_name, step), speech_text)).set_should_end_session(False)
        
    return handler_input.response_builder.response

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
        SimpleCard("Runescape Quests", speech_text)).set_should_end_session(True)
    return handler_input.response_builder.response

@sb.exception_handler(can_handle_func=lambda i, e: True)
def all_exception_handler(handler_input, exception):
    # type: (HandlerInput, Exception) -> Response
    # Log the exception in CloudWatch Logs
    print(exception)

    speech = "Sorry, I didn't get it. Can you please say it again!!"
    handler_input.response_builder.speak(speech).ask(speech)
    return handler_input.response_builder.response