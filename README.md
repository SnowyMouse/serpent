# serpent 1.1.0
Halo Script without the LISP

Requires Python 3 and the Halo Editing Kit.

## Example script

```
global string hello_world = "hello world"

startup start
    developer_mode = 127
    if (4 + 1) > 4
        print(hello_world)
        print("5 is greater than 4!")
    elseif 5 / 0
        print("wait, what?")
    end
end
```
When serpent.py is run, it will output a script that can be compiled by Sapien into Halo Custom Edition:

```
(global string hello_world "hello world")(script startup start (set developer_mode 127)(if (> (+ 4 1)4)(begin (print hello_world)(print "5 is greater than 4!"))(if (/ 5 0)(print "wait, what?"))))
```
