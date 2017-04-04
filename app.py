import random
import re

import flask
from  twilio import twiml

app = flask.Flask(__name__)

BANNED_PINS = [
  '12345678',
  '87654321',
  '12341234',
  '43214321',
  '12123434',
  '123456789',
  '987654321',
  '1234567890',
  '0123456789'
  '987654321',
  '0987654321',
]

@app.route('/init', methods=['GET', 'POST'])
def init():
  r = twiml.Response()
  r.say('Your message here! Call 1-844-BEG-NEON.')
  r.say('Hello, and welcome to 1-844-BEG-NEON!')
  r.redirect(url='/main_menu')

  return str(r)

@app.route('/main_menu', methods=['GET', 'POST'])
def main_menu():
  r = twiml.Response()
  with r.gather(action='/get_started', method='POST', numDigits=1) as g:
    g.say('To get started, press 1. To create an advertisement, press 2. '
          'To place an ad, press 3. To hear these options in Spanish, contact '
          'the administrator of this service and provide him or her with a '
          'spanish translation of this text.')

  return str(r)

@app.route('/get_started', methods=['GET', 'POST'])
def get_started():
  r = twiml.Response()
  digit_pressed = flask.request.values.get('Digits', None)
  if digit_pressed in ('1', '2', '3'):
    guess = random.randint(1, 3)
    print(guess, int(digit_pressed), guess == int(digit_pressed))
    if random.randint(1, 3) == int(digit_pressed):
      r.redirect('/setup')
    else:
      r.say('Thank you for your selection. That service is not available at '
            'this time. Please make another selection.')
      r.redirect('/main_menu')
  else:
    r.say('Sorry, that is not a valid selection. Please try again.')
    r.redirect('/main_menu')

  return str(r)

@app.route('/setup', methods=['GET', 'POST'])
def setup():
  r = twiml.Response()
  r.say('Thank you for your interest in SERVICE NAME. To begin, lets choose a '
        'pin. Your pin must be between 8 and 32 digits long and may not '
        'contain any special character or uppercase letters. When you are '
        'done, press the pound key')
  r.gather(action='/pin_select?tries=1', method='GET', timeout=60,
           finishOnKey='#')

  return str(r)

@app.route('/pin_select', methods=['GET', 'POST'])
def pin_select():
  r = twiml.Response()
  tries = flask.request.values.get('tries', None)
  digits = flask.request.values.get('Digits', None)
  origDigits = flask.request.values.get('origDigits', None)
  secDigits = flask.request.values.get('secDigits', None)
  if tries == '1':
    r.say('Please re-enter the same pin, followed by the pound sign')
    r.gather(action='/pin_select?tries=2&origDigits=' + digits, method='GET',
             timeout=60, finishOnKey='#')
  elif tries == '2':
    r.say('For added security, please repeat your pin one last time')
    actionStr = ('/pin_select?tries=3&origDigits=' + origDigits + 
                 '&secDigits=' + digits)
    r.gather(action=actionStr, method='GET', timeout=60,
             finishOnKey='#')
  elif tries == '3':
    if digits in BANNED_PINS:
      r.say('We\'re sorry, that pin is too simple, or on a list of well known '
            'banned pins. We take your security very seriously. Please try '
            'again.')
      r.redirect('/setup')
    if (digits == origDigits and digits == secDigits and len(digits) >= 8 and
        len(digits) <= 32):
      if re.search(r'(\d)\1', digits):
        r.say('Sorry, for your security, your pin cannot contain the same '
              'digit twice in a row. Please try entering your pin again. ')
        r.redirect('/setup')

      digitToCount = {}
      for digit in digits:
        digitToCount[digit] = digitToCount.get(digit, 0) + 1
      for value in digitToCount.values():
        if value >= 4:
          r.say('Sorry, for your security, your pin cannot contain the same '
                'digit more than 3 total times. Please try entering your pin '
                'again')
          r.redirect('/setup')
          break
      else:
        r.say('You have successfully set your pin! Congratulations!')
        r.redirect('/create_ad')
    else:
      r.say('Sorry, there was a problem with your entry. Please try entering '
          'your pin again. Your security is important to us.')
      r.redirect('/setup')

  return str(r)

@app.route('/create_ad', methods=['GET', 'POST'])
def create_ad():
  r = twiml.Response()
  r.say('Unfortunately, ads cannot be set up at this time. Thank you for '
        'using 1-844-BEG-NEON. Goodbye!')
  r.hangup()
  
  return str(r)

if __name__ == "__main__":
  app.run(debug=True, port=8000)
