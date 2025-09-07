from behave import given, when, then
from responses_openapi.example import say_hello


@given('I have a name "{name}"')
def step_given_name(context, name):
    context.name = name


@given("I have no name")
def step_given_no_name(context):
    context.name = None


@when("I call say_hello with the name")
def step_when_call_say_hello(context):
    context.result = say_hello(context.name)


@when("I call say_hello with None")
def step_when_call_say_hello_none(context):
    context.result = say_hello(None)


@then('I should get the greeting "{expected_greeting}"')
def step_then_check_greeting(context, expected_greeting):
    assert context.result == expected_greeting, f"Expected '{expected_greeting}', but got '{context.result}'"
