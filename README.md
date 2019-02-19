# serpent 2.1.0
Halo Script without the LISP

Requires Python 3 and the Halo Editing Kit.

## Usage
`serpent.py [-h] [--pretty] [--reverse] [--strip] <input> <output>`

`<input>` is the input script. `<output>` is the output script. By default, serpent converts serpent
scripts into HSC scripts.

Using `--reverse` converts HSC scripts into serpent scripts.

`--pretty` adds whitespace characters to the output to make the script more human-readable. This is on by default when
converting from HSC scripts.

`--strip` removes whitespace characters from the output that are not necessary for the script to work. This is on by
default when converting to HSC scripts.

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
If/else(if) statements can be used with the following syntax:

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

This will invoke Halo's `(set)` function. Therefore, using `set(variable, expression)` will have the same result. Note
that only global variables can be set. Halo does not support local variables.

### Calling functions
Functions may be called using the following syntax:

```
<function-name>([parameter-expression][, <parameter-expression> ...])
```

Built-in functions and any previously defined function can be used. To do recursion with a static script, a stub script
with the same script name must be defined. Halo's low static allocation for scripts may cause issues with deep
recursion.

### Logical operators
There are several different operators which can be used for logic.

| Operator  | Result                                  | Halo Script |
| --------- | --------------------------------------- | ----------- |
| `a == b`  | true if a and b are equal               | `(= a b)`   |
| `a != b`  | true if a and b are not equal           | `(!= a b)`  |
| `a < b`   | true if a is less than b                | `(< a b)`   |
| `a > b`   | true if a is greater than b             | `(> a b)`   |
| `a <= b`  | true if a is less than or equal to b    | `(<= a b)`  |
| `a >= b`  | true if a is greater than or equal to b | `(>= a b)`  |
| `a and b` | true if a and b are true                | `(and a b)` |
| `a or b`  | true if a or b are true                 | `(or a b)`  |
| `!a`      | true if a is not true                   | `(not a)`   |

#### Order of operations
Halo's LISP does not have any concept of order of operations, as each operation is evaluated first-to-last. Operations
used in serpent will therefore be reordered and output so they are in this order. Operators in the same row are
evaluated in whichever order they appear in the script.

| Operators            |
| -------------------- |
| `!`                  |
| `*`, `/`             |
| `+`, `-`             |
| `<`, `>`, `<=`, `>=` |
| `==`, `!=`           |
| `and`                |
| `or`                 |

To make code more readable and prevent unexpected logical errors, it is generally recommended to use parenthesis when
combining `and` and `or` in a single expression.

## Using serpent in your own tool
If you want to use serpent, it is recommended that you do not implement the serpent.py, itself, as it is intended to be
used as a standalone command-line program. Instead, you should call the functions that serpent.py calls, as this will
allow you to do error handling.

To do this, these are the the functions you will need to call to convert serpent scripts into HSC scripts:

| Function                                   | Module       | Usage                                                          | Error         |
| ------------------------------------------ | ------------ | -------------------------------------------------------------- | ------------- |
| `tokenize(text, line)`                     | tokenizer    | Return an array of tokens for the given line text and number.  | TokenError    |
| `parse_serpent_script(tokens)`             | parser       | Return a statement tree for the tokenized serpent script.      | ParserError   |
| `compile_hsc_script(statement, strip)`     | compiler     | Recursively generate a HSC script from the statement tree.     | CompilerError |

For converting HSC scripts into sapien scripts, these are the functions needed:

| Function                                   | Module       |                                                                | Error         |
| ------------------------------------------ | ------------ | -------------------------------------------------------------- | ------------- |
| `tokenize(text, line)`                     | tokenizer    | *(See above)*                                                  | TokenError    |
| `parse_hsc_script(tokens)`                 | parser       | Return a statement tree for the tokenized HSC script.          | ParserError   |
| `compile_serpent_script(statement, strip)` | compiler     | Recursively generate a serpent script from the statement tree. | CompilerError |
