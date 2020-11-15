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