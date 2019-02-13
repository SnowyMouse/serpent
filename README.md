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

## Syntax

### Global variables
Global variables can be defined with the following syntax:

```
global <type> <variable-name> = <initial-expression>
```

Halo requires an initial value for all global scripts. Functions may be required for value types that cannot be
represented with an explicit value.

### Scripts
Scripts can be defined with the following syntax:

```
<script-type> [<return-type>] <script-name> [...] end
```

Return types are required for static and stub scripts. Other scripts do not have a return type. The last function
called in a static or stub script will be the value it returns. Note that Halo does not support defining functions with
parameters. Therefore, globals must be used.

### If statements
If/else(if) statements can be defined with the following syntax:

```
if <expression> [...] [elseif <expression> [...] ...] [else [...]] end
```

Any number of elseif statements can be used, but Halo's low stack allocation for scripts may cause issues with many
elseif or nested if statements.

### Setting variables
Variables may be set using the following syntax:

```
<variable> = <expression>
```

This will invoke Halo's `(set)` function. Therefore, using `set(variable, expression)` will have the same result.

### Calling functions
Functions may be called using the following syntax:

```
<function-name>([parameter][,<parameter> ...])
```

Built-in functions and any previously defined function can be used. To do recursion with a static script, a stub script
with the same script name must be defined. Halo's low static allocation for scripts may cause issues with deep
recursion.

### Logical operators
There are several different operators which can be used for logic.

| Operator  | Result                                  |
| --------- | --------------------------------------- |
| `a == b`  | true if a and b are equal               |
| `a != b`  | true if a and b are not equal           |
| `a < b`   | true if a is less than b                |
| `a > b`   | true if a is greater than b             |
| `a <= b`  | true if a is less than or equal to b    |
| `a >= b`  | true if a is greater than or equal to b |
| `a and b` | true if a and b are true                |
| `a or b`  | true if a or b are true                 |

#### Order of operations
Halo's LISP does not have any concept of order of operations, as each operation is evaluated first-to-last. Operations
used in serpent will therefore be reordered and output so they are in this order. Operators in the same row are
evaluated in whichever order they appear in the script.

| Operators            |
| -------------------- |
| `*`, `/`             |
| `+`, `-`             |
| `<`, `>`, `<=`, `>=` |
| `==`, `!=`           |
| `and`                |
| `or`                 |

To make code more readable and prevent unexpected logical errors, it is generally recommended to use parenthesis when
combining `and` and `or` in a single expression.
