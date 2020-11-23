# Commands
| Feature               | Input type | Input                                | Expected result                         | Passing? | Notes |
|-----------------------|------------|--------------------------------------|-----------------------------------------|----------|-------|
| key press commands    | valid      | all commands and aliases from dict   | key is pressed                          |          |       |
| hotkey commands       | valid      | -                                    | both keys are pressed                   |          |       |
| click commands        | valid      | click, rightclick, middleclick       | button is clicked                       |          |       |
|                       | edge       | doubleclick                          | left button clicked twice               |          |       |
| mouse hold commands   | valid      | hold mouse, hold the mouse           | left button hold 3 secs                 |          |       |
|                       | valid      | hold mouse long, hold the mouse long | left button hold 9 secs                 |          |       |
| mouse scroll commands | valid      | scroll (down, up)                    | scrolled 60px 5 times                   |          |       |
| mouse move commands   | valid      | all commands and aliases from dict   | mouse move appropriate number of pixels |          |       |
| mouse drag commands   | valid      | all commands and aliases from dict   | mouse drag appropriate number of pixels |          |       |
| type commands         | valid      | type test                            | t-e-s-t pressed                         |          |       |
|                       | edge       | type 😳                              | nothing                                 |          |       |
|                       | edge       | type test😳                          | t-e-s-t pressed                         |          |       |
|                       | valid      | press test                           | t-e-s-t pressed                         |          |       |
|                       | edge       | press 😳                             | nothing                                 |          |       |
|                       | edge       | press test😳                         | t-e-s-t pressed                         |          |       |
| misc commands         |            |                                      |                                         |          |       |
| !modalert command     | valid      | !modalert                            | ping in discord                         |          |       |
|                       | valid      | !modalert test                       | ping in discord with test message       |          |       |
| go to command         | valid      | go to 300 400                        | mouse goes to co-ords                   |          |       |
|                       | edge       | go to 0 0                            | mouse goes to co-ords                   |          |       |
|                       | invalid    | go to, go to 300, go to a b          | nothing                                 |          |       |
| gtype command         | valid      | gtype test                           | t-e-s-t pressed slowly, works in games  |          |       |
|                       | edge       | gtype 😳                             | nothing                                 |          |       |
|                       | edge       | gtype test😳                         | t-e-s-t pressed slowly, works in games  |          |       |
| ptype command         | valid      | type test                            | test pasted                             |          |       |
|                       | valid      | type 😳                              | 😳 pasted                               |          |       |
|                       | valid      | type test😳                          | test😳 pasted                           |          |       |

# Permission restricted commands

| Feature                        | Input type | Input                                                          | Expected result                                                                         | Passing? | Notes |
|--------------------------------|------------|----------------------------------------------------------------|-----------------------------------------------------------------------------------------|----------|-------|
| testconn command               | valid      | script- testconn                                               | Correct message appears in #mod-chat discord channel                                    |          |       |
| reqdata command                | valid      | script- reqdata                                                | Correct active information appears in #mod-chat                                         |          |       |
| apirefresh command             | valid      | script- apirefresh                                             | permissions_handler_from_json is run correctly, success message appears in #system-logs |          |       |
| forceerror command             | valid      | script- forceerror                                             | dummy error embed with correct info appears in #system-logs                             |          |       |
| chatbot control                | valid      | chatbot- start                                                 | Message appears in #system-logs with command, status code 204                           |          |       |
|                                | valid      | chatbot- stop                                                  | \--                                                                                     |          |       |
|                                | valid      | chatbot- restart                                               | \--                                                                                     |          |       |
|                                | valid      | chatbot- kill                                                  | \--                                                                                     |          |       |
|                                | invalid    | chatbot- bbbb                                                  | \-, status code 403                                                                     |          |       |
| modsay command                 | valid      | modsay test                                                    | message appears in #mod-chat                                                            |          |       |
|                                | edge       | modsay                                                         | nothing                                                                                 |          |       |
| misc mod-only commands         | valid      | hideall                                                        | win + m pressed                                                                         |          |       |
|                                | valid      | mute                                                           | mute key pressed                                                                        |          |       |
|                                | valid      | el muchacho                                                    | browser window opened                                                                   |          |       |
|                                | valid      | shutdownabort                                                  | system runs shutdown -a                                                                 |          |       |
| suspend script command         | valid      | script- suspend 3                                              | script sleeps for 3 seconds                                                             |          |       |
|                                | invalid    | script- suspend b                                              | non-numeric arg log message                                                             |          |       |
|                                | invalid    | script- suspend -1                                             | negative arg log message                                                                |          |       |
|                                | invalid    | script- suspend 999999999999999999                             | too large arg log message                                                               |          |       |
| !defcon command                | valid      | !defcon 1                                                      | win + m pressed, mute key pressed, system shuts down immediately, script sleeps         |          |       |
|                                | valid      | !defcon 3                                                      | win + m pressed, mute key pressed, script sleeps                                        |          |       |
|                                | valid      | !defcon blue                                                   | browser window opened, script sleeps 30 secds                                           |          |       |
|                                | invalid    | !defcon mmm                                                    | nothing                                                                                 |          |       |
|                                | invalid    | !defcon                                                        | nothing                                                                                 |          |       |
| script shutdown                | valid      | correct key while logged in as account with script permissions | script quits                                                                            |          |       |
|                                | invalid    | incorrect key                                                  | nothing                                                                                 |          |       |
|                                | invalid    | correct key with no script permissions                         | nothing                                                                                 |          |       |

# Command cooldowns

# Logging with `logging`

# Obs logging